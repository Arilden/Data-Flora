"""
Extração — IBGE Censo 2022: características urbanísticas do entorno dos
domicílios (inclui a variável "arborização"), agregado por bairro.

Fonte (FTP público do IBGE, sem autenticação, sem limite de requisições):
  https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/
  Agregados_por_Setores_Censitarios_Caracteristicas_urbanisticas_do_entorno_dos_domicilios/
  Agregados_por_Bairro_csv/
  Agregados_por_bairros_entorno_domicílios_BR.zip

O arquivo cobre o Brasil inteiro (todos os municípios); o script baixa,
descompacta em memória, tenta filtrar para o município do Rio de Janeiro
(código IBGE 3304557) e salva tanto a versão nacional bruta (para conferência)
quanto a versão já filtrada para o RJ.

NOTA sobre o recorte de 2024 deste projeto: o Censo é decenal, não existe
edição 2024. Esta base (Censo 2022) entra na massa de 2024 como PROXY da
condição estrutural do bairro (arborização não muda de um ano para o outro
na mesma velocidade que poluição ou temperatura) — marcar isso no dicionário
de dados e no README, nunca apresentar como "dado de 2024".

Saída:
  dados_brutos/ibge_entorno_bairro_BR.csv      (nacional, como baixado)
  dados_brutos/ibge_entorno_bairro_rj.csv      (filtrado para o Rio de Janeiro)
"""

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

URL = (
    "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/"
    "Agregados_por_Setores_Censitarios_Caracteristicas_urbanisticas_do_entorno_dos_domicilios/"
    "Agregados_por_Bairro_csv/Agregados_por_bairros_entorno_domic%C3%ADlios_BR.zip"
)

MUNICIPIO_RJ_COD = "3304557"
MUNICIPIO_RJ_NOME = "RIO DE JANEIRO"

OUT_DIR = Path(__file__).resolve().parent.parent / "dados_brutos"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Baixando pacote do IBGE (características urbanísticas do entorno, por bairro)...")
    resp = requests.get(URL, timeout=120)
    resp.raise_for_status()

    zf = zipfile.ZipFile(io.BytesIO(resp.content))
    csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
    if not csv_names:
        raise RuntimeError(f"Nenhum CSV encontrado dentro do zip. Conteúdo: {zf.namelist()}")
    csv_name = csv_names[0]
    print(f"Arquivo dentro do zip: {csv_name}")

    with zf.open(csv_name) as f:
        # CSVs do IBGE costumam vir em latin1, separados por ';'
        df = pd.read_csv(f, sep=";", encoding="latin1", low_memory=False)

    print(f"Total de linhas (Brasil): {len(df)}")
    print(f"Colunas: {list(df.columns)}")

    raw_out = OUT_DIR / "ibge_entorno_bairro_BR.csv"
    df.to_csv(raw_out, index=False, encoding="utf-8-sig")
    print(f"Base nacional salva em {raw_out}")

    # Tenta localizar a coluna de código ou nome do município/bairro para filtrar o RJ.
    col_cod_mun = next((c for c in df.columns if c.upper() in ("CD_MUN", "COD_MUNICIPIO", "CD_MUNICIPIO", "CD_BAIRRO")), None)
    col_nome_mun = next((c for c in df.columns if "MUN" in c.upper() and "NOME" in c.upper()), None)

    df_rj = None
    if col_cod_mun is not None:
        df_rj = df[df[col_cod_mun].astype(str).str.startswith(MUNICIPIO_RJ_COD)]
    elif col_nome_mun is not None:
        df_rj = df[df[col_nome_mun].astype(str).str.upper().str.contains(MUNICIPIO_RJ_NOME)]

    if df_rj is not None and len(df_rj) > 0:
        rj_out = OUT_DIR / "ibge_entorno_bairro_rj.csv"
        df_rj.to_csv(rj_out, index=False, encoding="utf-8-sig")
        print(f"Filtrado para o Rio de Janeiro: {len(df_rj)} linhas salvas em {rj_out}")
    else:
        print(
            "AVISO: não foi possível identificar automaticamente a coluna de município. "
            "Abra ibge_entorno_bairro_BR.csv, confira o nome exato da coluna de "
            "código/nome do município e filtre manualmente (código do Rio de Janeiro: "
            f"{MUNICIPIO_RJ_COD})."
        )


if __name__ == "__main__":
    main()
