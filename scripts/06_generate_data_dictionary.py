"""
Gera o dicionário técnico e semântico das camadas Bronze, Silver e Gold.

O catálogo combina o perfil observado nos arquivos com metadados oficiais e
regras do projeto. São produzidos:

* docs/dicionario_dados_gerado.csv  - catálogo tabular para consulta/filtros;
* docs/dicionario_dados_gerado.md   - versão legível e resumo das tabelas;
* docs/validacao_dicionario_dados.json - evidências da validação automática.

Uso:
    python scripts/06_generate_data_dictionary.py
    python scripts/06_generate_data_dictionary.py --sample-size 10000

Por padrão, todos os registros são perfilados. ``--sample-size`` permite uma
amostra determinística (seed 42) para bases futuras muito maiores.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT_DIR / "docs"

MONITORAR_URL = (
    "https://services1.arcgis.com/OlP4dGNtIcnD3RYf/arcgis/rest/services/"
    "Qualidade_do_ar_dados_horarios_2011_2018/FeatureServer/2"
)
IBGE_DICTIONARY_URL = (
    "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/"
    "Agregados_por_Setores_Censitarios_Caracteristicas_urbanisticas_do_entorno_dos_domicilios/"
    "dicionarios_de_dados_entorno.zip"
)
IPS_URL = "https://www.data.rio/documents/918dd39478594792a9cfa7080b84c0b5"


@dataclass(frozen=True)
class TableSpec:
    name: str
    path: str
    family: str
    source: str
    source_url: str
    grain: str
    description: str
    excel_sheet: str | None = None


TABLE_SPECS = [
    TableSpec(
        "bronze.monitorar_horario_2024",
        "bronze/monitorar_horario_2024.csv",
        "monitorar",
        "MonitorAr-Rio / SMAC-PCRJ",
        MONITORAR_URL,
        "Estação de monitoramento × hora",
        "Medições horárias brutas de qualidade do ar e meteorologia em 2024.",
    ),
    TableSpec(
        "bronze.ibge_entorno_bairro_BR",
        "bronze/ibge_entorno_bairro_BR.csv",
        "ibge",
        "IBGE — Censo Demográfico 2022, entorno dos domicílios",
        IBGE_DICTIONARY_URL,
        "Bairro do Brasil",
        "Agregados nacionais por bairro; proxy estrutural de 2022 para a análise de 2024.",
    ),
    TableSpec(
        "bronze.ips_ra_2024",
        "bronze/ips_ra_2024.xlsx",
        "ips",
        "Instituto Pereira Passos / data.rio — IPS Rio 2024",
        IPS_URL,
        "Região Administrativa do Rio de Janeiro",
        "Dimensões e componentes do IPS por RA na edição 2024.",
        "Dimensões e Componentes 2024",
    ),
    TableSpec(
        "silver.monitorar_horario_rj_2024",
        "silver/monitorar_horario_rj_2024.csv",
        "monitorar",
        "MonitorAr-Rio / SMAC-PCRJ",
        MONITORAR_URL,
        "Estação de monitoramento × hora",
        "Medições horárias de 2024 disponibilizadas na camada Silver do projeto.",
    ),
    TableSpec(
        "silver.ibge_entorno_bairro_rj",
        "silver/ibge_entorno_bairro_rj.csv",
        "ibge",
        "IBGE — Censo Demográfico 2022, entorno dos domicílios",
        IBGE_DICTIONARY_URL,
        "Bairro do município do Rio de Janeiro",
        "Agregados por bairro filtrados para o Rio; proxy estrutural de 2022.",
    ),
    TableSpec(
        "silver.ips_ra_rj_2024",
        "silver/ips_ra_rj_2024.xlsx",
        "ips",
        "Instituto Pereira Passos / data.rio — IPS Rio 2024",
        IPS_URL,
        "Região Administrativa do Rio de Janeiro",
        "Dimensões e componentes do IPS por RA na edição 2024.",
        "Dimensões e Componentes 2024",
    ),
    TableSpec(
        "gold.massa_dados",
        "gold/massa_dados.csv",
        "gold_daily",
        "Pipeline interno Silver → Gold",
        "",
        "Região Administrativa/estação × dia de 2024",
        "Massa diária integrada para análises socioambientais.",
    ),
    TableSpec(
        "gold.massa_horaria_rj_2024",
        "gold/massa_horaria_rj_2024.parquet",
        "monitorar",
        "Pipeline interno Silver → Gold; origem MonitorAr-Rio",
        MONITORAR_URL,
        "Estação de monitoramento × hora",
        "Massa horária validada e armazenada em formato colunar.",
    ),
]


IPS_COLUMNS = [
    "ra_nome",
    "ips_geral",
    "dim_necessidades",
    "nutricao",
    "agua_saneamento",
    "moradia",
    "seguranca",
    "dim_bem_estar",
    "acesso_conhecimento",
    "acesso_info",
    "saude_bem_estar",
    "meio_ambiente",
    "dim_oportunidades",
    "direitos",
    "liberdade",
    "inclusao",
    "ensino_superior",
]


def meta(
    description: str,
    unit: str = "—",
    nature: str = "",
    role: str = "Atributo",
    join: str = "—",
    note: str = "—",
    logical_type: str = "",
) -> dict[str, str]:
    return {
        "description": description,
        "unit": unit,
        "nature": nature,
        "role": role,
        "join": join,
        "note": note,
        "logical_type": logical_type,
    }


MONITORAR_META = {
    "objectid": meta(
        "Identificador único do registro no serviço ArcGIS.",
        role="Chave primária",
        join="Junção direta entre as cópias Bronze, Silver e Gold horária.",
        logical_type="INTEGER",
    ),
    "data": meta(
        "Data e hora local da medição (GMT-3 em todo o recorte de 2024).",
        role="Chave temporal composta",
        join="Combinar com estação para identificar uma observação horária.",
        logical_type="DATETIME",
    ),
    "codnum": meta(
        "Código numérico da estação de monitoramento.",
        role="Chave de referência",
        join="Relaciona o cadastro da estação.",
        logical_type="INTEGER",
    ),
    "estação": meta(
        "Sigla oficial da estação MonitorAr: AV, BG, CA, CG, IR, PG, SC ou SP.",
        role="Chave espacial composta",
        join="Combinar com data; na fonte oficial CA=Centro e AV=Copacabana.",
        note="A configuração Gold atual inverte CA e AV; não usar o nome de região sem revisar esse mapeamento.",
        logical_type="STRING",
    ),
    "chuva": meta("Precipitação pluviométrica acumulada na hora.", "mm"),
    "pres": meta("Pressão atmosférica local.", "mbar/hPa"),
    "rs": meta("Radiação solar global incidente.", "W/m²"),
    "temp": meta("Temperatura do ar na estação.", "°C"),
    "ur": meta("Umidade relativa do ar.", "%"),
    "dir_vento": meta("Direção predominante do vento.", "graus (0–360)"),
    "vel_vento": meta("Velocidade do vento.", "m/s"),
    "so2": meta("Concentração horária de dióxido de enxofre (SO₂).", "µg/m³"),
    "no2": meta("Concentração horária de dióxido de nitrogênio (NO₂).", "µg/m³"),
    "hcnm": meta("Concentração horária de hidrocarbonetos não metano (HCNM).", "ppm"),
    "hct": meta("Concentração horária de hidrocarbonetos totais (HCT).", "ppm"),
    "ch4": meta("Concentração horária de metano (CH₄).", "ppm"),
    "co": meta("Concentração horária de monóxido de carbono (CO).", "ppm"),
    "no": meta("Concentração horária de monóxido de nitrogênio (NO).", "µg/m³"),
    "nox": meta("Concentração horária de óxidos de nitrogênio (NO + NO₂).", "µg/m³"),
    "o3": meta("Concentração horária de ozônio troposférico (O₃).", "µg/m³"),
    "pm10": meta("Concentração horária de material particulado inalável PM₁₀.", "µg/m³"),
    "pm2_5": meta("Concentração horária de material particulado fino PM₂,₅.", "µg/m³"),
    "lat": meta("Latitude da estação no sistema WGS 84.", "graus decimais"),
    "lon": meta("Longitude da estação no sistema WGS 84.", "graus decimais"),
    "x_utm_sirgas2000": meta("Coordenada leste UTM da estação, SIRGAS 2000 / zona 23S.", "metros"),
    "y_utm_sirgas2000": meta("Coordenada norte UTM da estação, SIRGAS 2000 / zona 23S.", "metros"),
}


IBGE_LABELS = {
    "V05000": "Total de domicílios particulares permanentes ocupados em setor selecionado para o levantamento do entorno.",
    "V05001": "Domicílios em face com circulação de caminhão ou ônibus.",
    "V05002": "Domicílios em face com circulação de carro de passeio ou van.",
    "V05003": "Domicílios em face com circulação de pedestres, bicicletas ou motocicletas.",
    "V05004": "Domicílios em face com circulação por aquavia.",
    "V05005": "Domicílios sem declaração válida para o tipo de circulação da via (saltado).",
    "V05006": "Domicílios em face com via pavimentada.",
    "V05007": "Domicílios em face sem via pavimentada.",
    "V05008": "Domicílios com pavimentação da via não declarada.",
    "V05009": "Domicílios em face com bueiro ou boca de lobo.",
    "V05010": "Domicílios em face sem bueiro ou boca de lobo.",
    "V05011": "Domicílios com presença de bueiro não declarada.",
    "V05012": "Domicílios em face com iluminação pública.",
    "V05013": "Domicílios em face sem iluminação pública.",
    "V05014": "Domicílios com iluminação pública não declarada.",
    "V05015": "Domicílios em face com ponto de ônibus.",
    "V05016": "Domicílios em face sem ponto de ônibus.",
    "V05017": "Domicílios com presença de ponto de ônibus não declarada.",
    "V05018": "Domicílios em face com via sinalizada para bicicleta.",
    "V05019": "Domicílios em face sem via sinalizada para bicicleta.",
    "V05020": "Domicílios com sinalização cicloviária não declarada.",
    "V05021": "Domicílios em face com calçada.",
    "V05022": "Domicílios em face sem calçada.",
    "V05023": "Domicílios com presença de calçada não declarada.",
    "V05024": "Domicílios em face com obstáculo na calçada.",
    "V05025": "Domicílios em face sem obstáculo na calçada.",
    "V05026": "Domicílios com obstáculo na calçada não declarado.",
    "V05027": "Domicílios em face com rampa para cadeirante.",
    "V05028": "Domicílios em face sem rampa para cadeirante.",
    "V05029": "Domicílios com presença de rampa para cadeirante não declarada.",
    "V05030": "Domicílios em face sem árvores.",
    "V05031": "Domicílios em face com 1 a 2 árvores.",
    "V05032": "Domicílios em face com 3 a 4 árvores.",
    "V05033": "Domicílios em face com 5 ou mais árvores.",
    "V05034": "Domicílios com arborização não declarada (saltado).",
}

IBGE_META = {
    "CD_BAIRRO": meta(
        "Código oficial do bairro no Censo Demográfico 2022.",
        nature="Proxy Censo 2022",
        role="Chave primária",
        join="Usar tabela oficial bairro → RA; não juntar somente pelo nome.",
        logical_type="STRING",
    ),
    "NM_BAIRRO": meta(
        "Nome oficial do bairro no Censo Demográfico 2022.",
        nature="Proxy Censo 2022",
        role="Chave de referência",
        join="Apoio à conferência; normalizar acentos e homônimos antes de cruzar.",
        logical_type="STRING",
    ),
}
IBGE_META.update(
    {
        field: meta(
            label,
            "domicílios",
            nature="Proxy Censo 2022",
            note=(
                "Definição conferida no dicionário oficial do IBGE. Atenção: o ETL atual usa este campo como arborização, mas ele mede rampa para cadeirante."
                if field == "V05027"
                else "Definição conferida no dicionário oficial do IBGE."
            ),
            logical_type="INTEGER",
        )
        for field, label in IBGE_LABELS.items()
    }
)


IPS_DESCRIPTIONS = {
    "ra_nome": "Código romano e nome da Região Administrativa.",
    "ips_geral": "Índice de Progresso Social geral da RA.",
    "dim_necessidades": "Nota da dimensão Necessidades Humanas Básicas.",
    "nutricao": "Nota do componente Nutrição e Cuidados Médicos Básicos.",
    "agua_saneamento": "Nota do componente Água e Saneamento.",
    "moradia": "Nota do componente Moradia.",
    "seguranca": "Nota do componente Segurança Pessoal.",
    "dim_bem_estar": "Nota da dimensão Fundamentos do Bem-Estar.",
    "acesso_conhecimento": "Nota do componente Acesso ao Conhecimento Básico.",
    "acesso_info": "Nota do componente Acesso à Informação.",
    "saude_bem_estar": "Nota do componente Saúde e Bem-Estar.",
    "meio_ambiente": "Nota do componente Qualidade do Meio Ambiente.",
    "dim_oportunidades": "Nota da dimensão Oportunidades.",
    "direitos": "Nota do componente Direitos Individuais.",
    "liberdade": "Nota do componente Liberdades Individuais.",
    "inclusao": "Nota do componente Tolerância e Inclusão.",
    "ensino_superior": "Nota do componente Acesso à Educação Superior.",
}
IPS_META = {
    field: meta(
        description,
        "pontos (0–100)" if field != "ra_nome" else "—",
        nature="Real — edição IPS 2024",
        role="Chave espacial" if field == "ra_nome" else "Atributo",
        join="Normalizar código/nome da RA antes do cruzamento." if field == "ra_nome" else "—",
        logical_type="STRING" if field == "ra_nome" else "DECIMAL",
    )
    for field, description in IPS_DESCRIPTIONS.items()
}


GOLD_META = {
    "data": meta("Data civil da observação diária.", nature="Real 2024", role="Chave temporal composta", join="Combinar com ra_codigo/região.", logical_type="DATE"),
    "mes": meta("Número do mês da observação.", nature="Derivado de data", logical_type="INTEGER"),
    "dia_ano": meta("Dia sequencial do ano bissexto de 2024 (1–366).", nature="Derivado de data", logical_type="INTEGER"),
    "regiao": meta("Nome amigável da região atribuído à estação pelo ETL.", nature="Derivado por mapeamento", role="Chave espacial composta", join="Preferir ra_codigo para cruzamentos.", note="O ETL atual inverte Centro/Copacabana para os códigos CA/AV; revisar antes da análise.", logical_type="STRING"),
    "ra_codigo": meta("Código romano da Região Administrativa atribuído pelo ETL.", nature="Derivado por mapeamento", role="Chave espacial composta", join="Chave recomendada para IPS e agregações territoriais.", note="Revisar as RAs associadas a CA/AV antes da análise.", logical_type="STRING"),
    "ra_nome": meta("Código e nome oficial da Região Administrativa atribuído pelo ETL.", nature="Derivado por mapeamento", role="Chave de referência", join="Normalizar antes de cruzar com IPS.", note="Revisar as RAs associadas a CA/AV antes da análise.", logical_type="STRING"),
    "lat": meta("Latitude de referência configurada para a região/estação.", "graus decimais", nature="Derivado por mapeamento"),
    "lon": meta("Longitude de referência configurada para a região/estação.", "graus decimais", nature="Derivado por mapeamento"),
    "pm10_media": meta("Média diária de PM₁₀ após regras de validade e imputação.", "µg/m³", nature="Derivado de medições reais 2024"),
    "pm10_max": meta("Máximo horário de PM₁₀ observado no dia.", "µg/m³", nature="Derivado de medições reais 2024"),
    "pm2_5_media": meta("Média diária de PM₂,₅; disponível principalmente para Irajá.", "µg/m³", nature="Derivado de medições reais 2024"),
    "o3_media": meta("Média diária de ozônio troposférico.", "µg/m³", nature="Derivado de medições reais 2024"),
    "o3_max": meta("Máximo horário de ozônio troposférico observado no dia.", "µg/m³", nature="Derivado de medições reais 2024"),
    "no2_media": meta("Média diária de dióxido de nitrogênio.", "µg/m³", nature="Derivado de medições reais 2024"),
    "co_media": meta("Média diária de monóxido de carbono.", "ppm", nature="Derivado de medições reais 2024"),
    "so2_media": meta("Média diária de dióxido de enxofre.", "µg/m³", nature="Derivado de medições reais 2024"),
    "temp_media": meta("Temperatura média diária.", "°C", nature="Derivado de medições reais 2024"),
    "temp_max": meta("Temperatura máxima horária do dia.", "°C", nature="Derivado de medições reais 2024"),
    "temp_min": meta("Temperatura mínima horária do dia.", "°C", nature="Derivado de medições reais 2024"),
    "ur_media": meta("Umidade relativa média diária.", "%", nature="Derivado de medições reais 2024"),
    "ur_min": meta("Umidade relativa mínima horária do dia.", "%", nature="Derivado de medições reais 2024"),
    "chuva_dia": meta("Precipitação total acumulada no dia.", "mm", nature="Derivado de medições reais 2024"),
    "derivada_pm10": meta("Taxa diária de variação de PM₁₀ por diferenças finitas.", "µg/(m³·dia)", nature="Derivado/calculado 2024"),
    "derivada_temp": meta("Taxa diária de variação da temperatura por diferenças finitas.", "°C/dia", nature="Derivado/calculado 2024"),
    "integral_acumulada_pm10": meta("Exposição acumulada de PM₁₀ pela regra dos trapézios.", "µg·dia/m³", nature="Derivado/calculado 2024"),
    "integral_acumulada_pm2_5": meta("Exposição acumulada de PM₂,₅ pela regra dos trapézios; preenchida para Irajá.", "µg·dia/m³", nature="Derivado/calculado 2024"),
    "ips_2024": meta("Índice de Progresso Social geral da RA na edição 2024.", "pontos (0–100)", nature="Real — edição IPS 2024"),
    "ips_dim_necessidades": meta("Nota da dimensão Necessidades Humanas Básicas.", "pontos (0–100)", nature="Real — edição IPS 2024"),
    "ips_dim_bem_estar": meta("Nota da dimensão Fundamentos do Bem-Estar.", "pontos (0–100)", nature="Real — edição IPS 2024"),
    "ips_dim_oportunidades": meta("Nota da dimensão Oportunidades.", "pontos (0–100)", nature="Real — edição IPS 2024"),
    "ips_comp_meio_ambiente": meta("Nota do componente Qualidade do Meio Ambiente.", "pontos (0–100)", nature="Real — edição IPS 2024"),
    "ips_dim_moradia": meta("Nota do componente Moradia.", "pontos (0–100)", nature="Real — edição IPS 2024"),
    "pct_arborizacao_2022": meta("Percentual rotulado como arborização no Gold, calculado atualmente como V05027/V05000 × 100.", "%", nature="Derivado de proxy Censo 2022", note="Inconsistência crítica: V05027 mede rampa para cadeirante. Arborização oficial está em V05030–V05034; este indicador precisa ser recalculado."),
    "qtd_domicilios_arborizados": meta("Quantidade rotulada como domicílios arborizados, atualmente copiada de V05027.", "domicílios", nature="Derivado de proxy Censo 2022", note="Inconsistência crítica: V05027 mede rampa para cadeirante; não representa domicílios arborizados.", logical_type="INTEGER"),
    "total_domicilios": meta("Total de domicílios particulares permanentes ocupados nos bairros agregados da RA.", "domicílios", nature="Proxy Censo 2022", logical_type="INTEGER"),
    "isa": meta("Índice de Saúde Arbórea sintético, calculado somente com estressores ambientais de 2024.", "pontos (0–100)", nature="Métrica derivada/sintética 2024"),
    "isa_classe": meta("Classe do ISA: Boa, Regular ou Ruim.", nature="Métrica derivada/sintética 2024", logical_type="STRING"),
    "flag_missing_pm10": meta("Indica média diária de PM₁₀ ausente antes da imputação.", "0/1", nature="Flag de qualidade", logical_type="BOOLEAN"),
    "flag_outlier_pm10": meta("Indica máximo horário de PM₁₀ acima do limite IQR da estação.", "0/1", nature="Flag de qualidade", logical_type="BOOLEAN"),
    "flag_imputado": meta("Indica que ao menos uma variável diária principal foi imputada.", "0/1", nature="Flag de qualidade", logical_type="BOOLEAN"),
}


def normalize_text(value: str) -> str:
    return "".join(
        char
        for char in unicodedata.normalize("NFD", str(value))
        if unicodedata.category(char) != "Mn"
    ).casefold()


def read_ips(path: Path, requested_sheet: str) -> pd.DataFrame:
    workbook = pd.ExcelFile(path)
    target = normalize_text(requested_sheet)
    matches = [sheet for sheet in workbook.sheet_names if normalize_text(sheet) == target]
    if not matches:
        raise ValueError(f"Aba '{requested_sheet}' não encontrada em {path}.")
    raw = pd.read_excel(path, sheet_name=matches[0], header=None)
    if raw.shape[1] != len(IPS_COLUMNS):
        raise ValueError(
            f"Layout inesperado no IPS: {raw.shape[1]} colunas; esperado {len(IPS_COLUMNS)}."
        )
    data = raw.iloc[8:41].copy()
    data.columns = IPS_COLUMNS
    return data.dropna(subset=["ra_nome"]).reset_index(drop=True)


def read_table(spec: TableSpec) -> pd.DataFrame:
    path = ROOT_DIR / spec.path
    if not path.exists():
        raise FileNotFoundError(f"Tabela não encontrada: {path}")
    suffix = path.suffix.casefold()
    if suffix == ".csv":
        return pd.read_csv(path, low_memory=False)
    if suffix == ".parquet":
        return pd.read_parquet(path)
    if suffix == ".xlsx" and spec.excel_sheet:
        return read_ips(path, spec.excel_sheet)
    raise ValueError(f"Formato sem leitor configurado: {path}")


def semantic_metadata(spec: TableSpec, field: str) -> dict[str, str]:
    maps = {
        "monitorar": MONITORAR_META,
        "ibge": IBGE_META,
        "ips": IPS_META,
        "gold_daily": GOLD_META,
    }
    metadata = maps[spec.family].get(field)
    if metadata is None:
        raise KeyError(f"Campo sem definição semântica: {spec.name}.{field}")
    result = metadata.copy()
    if not result["nature"]:
        result["nature"] = "Real 2024" if spec.family == "monitorar" else "Misto"
    return result


def non_blank_series(series: pd.Series) -> pd.Series:
    if pd.api.types.is_object_dtype(series.dtype) or pd.api.types.is_string_dtype(series.dtype):
        return series.replace(r"^\s*$", pd.NA, regex=True).dropna()
    return series.dropna()


def infer_logical_type(series: pd.Series, override: str) -> str:
    if override:
        return override
    values = non_blank_series(series)
    if pd.api.types.is_datetime64_any_dtype(series.dtype):
        return "DATETIME"
    if pd.api.types.is_bool_dtype(series.dtype):
        return "BOOLEAN"
    if pd.api.types.is_integer_dtype(series.dtype):
        return "INTEGER"
    if pd.api.types.is_float_dtype(series.dtype):
        if not values.empty and np.isclose(values.astype(float) % 1, 0).all():
            return "INTEGER"
        return "DECIMAL"
    return "STRING"


def integer_digits(values: pd.Series) -> int:
    if values.empty:
        return 0
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    if numeric.empty:
        return 0
    return max(len(str(abs(int(value)))) for value in numeric)


def decimal_shape(values: pd.Series) -> tuple[int, int] | None:
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    if numeric.empty:
        return None
    max_integer = 1
    max_scale = 0
    for value in numeric:
        try:
            decimal_value = Decimal(str(value))
        except (InvalidOperation, ValueError):
            continue
        _, digits, exponent = decimal_value.as_tuple()
        scale = max(-exponent, 0)
        integer_count = max(len(digits) - scale, 1) + max(exponent, 0)
        max_integer = max(max_integer, integer_count)
        max_scale = max(max_scale, scale)
    return max_integer + max_scale, max_scale


def field_precision(series: pd.Series, logical_type: str) -> str:
    values = non_blank_series(series)
    if logical_type == "STRING":
        maximum = max((len(str(value)) for value in values), default=0)
        return f"VARCHAR({maximum}) observado" if maximum else "VARCHAR — sem valor observado"
    if logical_type == "INTEGER":
        digits = integer_digits(values)
        return f"INTEGER ({digits} dígitos observados)" if digits else "INTEGER — sem valor observado"
    if logical_type == "DECIMAL":
        shape = decimal_shape(values)
        return f"DECIMAL({shape[0]},{shape[1]}) observado" if shape else "DECIMAL — sem valor observado"
    if logical_type == "BOOLEAN":
        return "BOOLEAN (1 bit lógico)"
    if logical_type == "DATE":
        return "DATE (AAAA-MM-DD)"
    if logical_type == "DATETIME":
        return "DATETIME (precisão até segundos)"
    return str(series.dtype)


def display_value(value: Any) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat(sep=" ")
    if isinstance(value, (float, np.floating)):
        return f"{float(value):.12g}"
    return str(value).replace("\n", " ").strip()


def examples(values: pd.Series, limit: int = 3) -> str:
    seen: list[str] = []
    for value in values:
        formatted = display_value(value)
        if formatted and formatted not in seen:
            seen.append(formatted)
        if len(seen) == limit:
            break
    return " | ".join(seen) if seen else "—"


def min_max(values: pd.Series, logical_type: str) -> tuple[str, str]:
    if values.empty:
        return "—", "—"
    if logical_type in {"INTEGER", "DECIMAL"}:
        numeric = pd.to_numeric(values, errors="coerce").dropna()
        if numeric.empty:
            return "—", "—"
        return display_value(numeric.min()), display_value(numeric.max())
    if logical_type in {"DATE", "DATETIME"}:
        dates = pd.to_datetime(values, errors="coerce").dropna()
        if dates.empty:
            return "—", "—"
        return display_value(dates.min()), display_value(dates.max())
    return "—", "—"


def profile_field(
    spec: TableSpec,
    field: str,
    full_series: pd.Series,
    sample_series: pd.Series,
    total_rows: int,
    sampled_rows: int,
) -> dict[str, Any]:
    semantic = semantic_metadata(spec, field)
    logical_type = infer_logical_type(sample_series, semantic["logical_type"])
    values = non_blank_series(sample_series)
    null_count = sampled_rows - len(values)
    minimum, maximum = min_max(values, logical_type)
    distinct_count = int(values.nunique(dropna=True))

    if sampled_rows == total_rows:
        unique_observed = len(non_blank_series(full_series)) == total_rows and full_series.nunique(dropna=True) == total_rows
        uniqueness = "Sim" if unique_observed else "Não"
    else:
        uniqueness = "Provável na amostra" if null_count == 0 and distinct_count == sampled_rows else "Não na amostra"

    domain = "—"
    if 0 < distinct_count <= 20:
        domain = " | ".join(sorted({display_value(value) for value in values})[:20])

    return {
        "nome_tabela": spec.name,
        "arquivo_origem": spec.path.replace("/", str(Path("/"))),
        "granularidade": spec.grain,
        "nome_campo": field,
        "tipo_fisico_observado": str(full_series.dtype),
        "tipo_logico": logical_type,
        "tamanho_precisao": field_precision(sample_series, logical_type),
        "descricao_resumida": semantic["description"],
        "unidade_medida": semantic["unit"],
        "natureza_dado": semantic["nature"],
        "papel_chave": semantic["role"],
        "orientacao_cruzamento": semantic["join"],
        "aceita_nulo_observado": "Sim" if null_count else "Não",
        "quantidade_registros_tabela": total_rows,
        "quantidade_registros_analisados": sampled_rows,
        "quantidade_nulos_amostra": null_count,
        "percentual_nulos_amostra": round((null_count / sampled_rows * 100) if sampled_rows else 0.0, 4),
        "quantidade_distintos_amostra": distinct_count,
        "unicidade_observada": uniqueness,
        "valor_minimo_observado": minimum,
        "valor_maximo_observado": maximum,
        "dominio_observado": domain,
        "exemplos_observados": examples(values),
        "fonte": spec.source,
        "url_fonte": spec.source_url or "—",
        "observacoes_integridade": semantic["note"],
    }


def generate_catalog(sample_size: int) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    rows: list[dict[str, Any]] = []
    tables: dict[str, pd.DataFrame] = {}
    for spec in TABLE_SPECS:
        frame = read_table(spec)
        tables[spec.name] = frame
        if sample_size and len(frame) > sample_size:
            sample = frame.sample(n=sample_size, random_state=42).sort_index()
        else:
            sample = frame
        for field in frame.columns:
            rows.append(
                profile_field(
                    spec,
                    str(field),
                    frame[field],
                    sample[field],
                    len(frame),
                    len(sample),
                )
            )
    return pd.DataFrame(rows), tables


def make_check(name: str, passed: bool, detail: str) -> dict[str, Any]:
    return {"nome": name, "resultado": "PASSOU" if passed else "FALHOU", "detalhe": detail}


def validate_catalog(catalog: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    expected_rows = sum(len(frame.columns) for frame in tables.values())
    checks.append(make_check("Cobertura de campos", len(catalog) == expected_rows, f"{len(catalog)}/{expected_rows} campos catalogados."))
    duplicates = int(catalog.duplicated(["nome_tabela", "nome_campo"]).sum())
    checks.append(make_check("Unicidade tabela/campo", duplicates == 0, f"{duplicates} duplicidades."))

    required = ["descricao_resumida", "tipo_logico", "tamanho_precisao", "fonte", "natureza_dado"]
    missing_required = int(catalog[required].replace("", pd.NA).isna().sum().sum())
    checks.append(make_check("Metadados obrigatórios", missing_required == 0, f"{missing_required} valores obrigatórios ausentes."))

    ibge = catalog[catalog["nome_tabela"] == "silver.ibge_entorno_bairro_rj"].set_index("nome_campo")
    ibge_ok = (
        "rampa para cadeirante" in ibge.at["V05027", "descricao_resumida"].casefold()
        and "sem árvores" in ibge.at["V05030", "descricao_resumida"].casefold()
        and "1 a 2 árvores" in ibge.at["V05031", "descricao_resumida"].casefold()
    )
    checks.append(make_check("Semântica oficial IBGE", ibge_ok, "V05027 e V05030–V05034 conferidos contra o dicionário oficial."))

    monitor = tables["silver.monitorar_horario_rj_2024"].copy()
    monitor["data"] = pd.to_datetime(monitor["data"], errors="coerce")
    monitor_ok = (
        len(monitor) == 70272
        and monitor["estação"].nunique() == 8
        and monitor["data"].min().year == 2024
        and monitor["data"].max().year == 2024
        and monitor["objectid"].is_unique
    )
    checks.append(make_check("Integridade MonitorAr 2024", monitor_ok, f"{len(monitor)} registros, {monitor['estação'].nunique()} estações e objectid único."))

    ibge_rj = tables["silver.ibge_entorno_bairro_rj"]
    ibge_rows_ok = len(ibge_rj) == 162 and ibge_rj["CD_BAIRRO"].astype(str).str.startswith("3304557").all()
    checks.append(make_check("Recorte IBGE Rio", bool(ibge_rows_ok), f"{len(ibge_rj)} bairros; códigos municipais válidos."))

    gold = tables["gold.massa_dados"]
    counts = gold.groupby("regiao").size()
    gold_ok = len(gold) == 2928 and gold["regiao"].nunique() == 8 and bool((counts == 366).all())
    checks.append(make_check("Grão da massa Gold", gold_ok, f"{len(gold)} linhas, {gold['regiao'].nunique()} regiões e 366 dias por região."))

    alerts = [
        {
            "severidade": "CRÍTICA",
            "codigo": "IBGE-V05027",
            "descricao": (
                "O ETL atual calcula pct_arborizacao_2022 e qtd_domicilios_arborizados com V05027, "
                "mas o dicionário oficial informa que V05027 mede rampa para cadeirante. "
                "Os campos de arborização são V05030–V05034."
            ),
        },
        {
            "severidade": "CRÍTICA",
            "codigo": "MONITORAR-CA-AV",
            "descricao": (
                "A fonte oficial identifica CA como Centro e AV como Copacabana; "
                "o ESTACOES_CONFIG do ETL atual associa AV a Centro e CA a Copacabana."
            ),
        },
    ]

    failed = [check for check in checks if check["resultado"] == "FALHOU"]
    status = "REPROVADO" if failed else "APROVADO_COM_RESSALVAS_CRITICAS"
    return {
        "gerado_em_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "tabelas_catalogadas": len(tables),
        "campos_catalogados": len(catalog),
        "checks": checks,
        "alertas": alerts,
    }


def escape_markdown(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_markdown(catalog: pd.DataFrame, validation: dict[str, Any], output: Path) -> None:
    lines = [
        "# Dicionário de Dados Gerado — Data Flora",
        "",
        f"**Gerado em:** {validation['gerado_em_utc']}",
        f"**Status da validação:** {validation['status']}",
        f"**Cobertura:** {validation['tabelas_catalogadas']} tabelas e {validation['campos_catalogados']} campos",
        "",
        "Este catálogo foi construído a partir dos arquivos atuais das camadas Bronze, Silver e Gold. "
        "Tipos, tamanhos, precisão, nulidade, cardinalidade, limites e exemplos refletem os valores observados; "
        "descrições e unidades foram confrontadas com as fontes oficiais e com as regras do projeto.",
        "",
        "## Alertas de integridade semântica",
        "",
    ]
    for alert in validation["alertas"]:
        lines.append(f"- **{alert['severidade']} — {alert['codigo']}:** {alert['descricao']}")
    lines.extend(["", "## Validação automática", ""])
    for check in validation["checks"]:
        lines.append(f"- **{check['resultado']} — {check['nome']}:** {check['detalhe']}")

    for spec in TABLE_SPECS:
        subset = catalog[catalog["nome_tabela"] == spec.name]
        lines.extend(
            [
                "",
                f"## `{spec.name}`",
                "",
                f"- Arquivo: `{spec.path}`",
                f"- Grão: {spec.grain}",
                f"- Registros: {int(subset['quantidade_registros_tabela'].iloc[0])}",
                f"- Descrição: {spec.description}",
                "",
                "| Campo | Tipo lógico | Tamanho/precisão | Nulos % | Papel | Descrição | Observações |",
                "|---|---|---|---:|---|---|---|",
            ]
        )
        for row in subset.to_dict("records"):
            cells = [
                f"`{row['nome_campo']}`",
                row["tipo_logico"],
                row["tamanho_precisao"],
                row["percentual_nulos_amostra"],
                row["papel_chave"],
                row["descricao_resumida"],
                row["observacoes_integridade"],
            ]
            lines.append("| " + " | ".join(escape_markdown(cell) for cell in cells) + " |")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera e valida o dicionário de dados do projeto Data Flora.")
    parser.add_argument(
        "--sample-size",
        type=int,
        default=0,
        help="Quantidade máxima de linhas analisadas por tabela; 0 usa a tabela completa (padrão).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.sample_size < 0:
        raise ValueError("--sample-size deve ser zero ou um inteiro positivo.")

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    catalog, tables = generate_catalog(args.sample_size)
    validation = validate_catalog(catalog, tables)

    csv_path = DOCS_DIR / "dicionario_dados_gerado.csv"
    md_path = DOCS_DIR / "dicionario_dados_gerado.md"
    validation_path = DOCS_DIR / "validacao_dicionario_dados.json"

    catalog.to_csv(csv_path, index=False, sep=";", encoding="utf-8-sig")
    validation_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(catalog, validation, md_path)

    print(f"Dicionário CSV: {csv_path}")
    print(f"Dicionário Markdown: {md_path}")
    print(f"Validação: {validation_path}")
    print(f"Tabelas catalogadas: {validation['tabelas_catalogadas']}")
    print(f"Campos catalogados: {validation['campos_catalogados']}")
    print(f"Status: {validation['status']}")

    return 1 if validation["status"] == "REPROVADO" else 0


if __name__ == "__main__":
    raise SystemExit(main())
