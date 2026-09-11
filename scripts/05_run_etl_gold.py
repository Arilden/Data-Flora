"""
Pipeline de ETL: Camada Silver -> Camada Gold
Gera:
1. gold/massa_horaria_rj_2024.parquet (70.272 registros horários validados)
2. gold/massa_dados.csv (2.928 registros diários com derivadas, integrais, ISA, IPS e Censo)
"""

import unicodedata
from pathlib import Path
import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
SILVER_DIR = ROOT_DIR / "silver"
GOLD_DIR = ROOT_DIR / "gold"

ESTACOES_CONFIG = {
    "AV": {
        "regiao": "Centro",
        "ra_codigo": "II",
        "ra_nome": "II — Centro",
        "ra_ips_key": "II CENTRO",
        "bairros_censo": ["Centro"],
        "lat": -22.9068,
        "lon": -43.1812,
    },
    "SC": {
        "regiao": "São Cristóvão",
        "ra_codigo": "VII",
        "ra_nome": "VII — São Cristóvão",
        "ra_ips_key": "VII SAO CRISTOVAO",
        "bairros_censo": ["São Cristóvão", "Mangueira", "Benfica", "Vasco da Gama"],
        "lat": -22.8967,
        "lon": -43.2217,
    },
    "CA": {
        "regiao": "Copacabana",
        "ra_codigo": "V",
        "ra_nome": "V — Copacabana",
        "ra_ips_key": "V COPACABANA",
        "bairros_censo": ["Copacabana", "Leme"],
        "lat": -22.9698,
        "lon": -43.1868,
    },
    "SP": {
        "regiao": "Tijuca",
        "ra_codigo": "VIII",
        "ra_nome": "VIII — Tijuca",
        "ra_ips_key": "VIII TIJUCA",
        "bairros_censo": ["Tijuca", "Alto da Boa Vista", "Praça da Bandeira"],
        "lat": -22.9247,
        "lon": -43.2328,
    },
    "IR": {
        "regiao": "Irajá",
        "ra_codigo": "XIV",
        "ra_nome": "XIV — Irajá",
        "ra_ips_key": "XIV IRAJA",
        "bairros_censo": ["Irajá", "Vicente de Carvalho", "Vila Kosmos", "Vila da Penha", "Vista Alegre", "Colégio"],
        "lat": -22.8317,
        "lon": -43.3283,
    },
    "BG": {
        "regiao": "Bangu",
        "ra_codigo": "XVII",
        "ra_nome": "XVII — Bangu",
        "ra_ips_key": "XVII BANGU",
        "bairros_censo": ["Bangu", "Padre Miguel", "Senador Camará", "Gericinó"],
        "lat": -22.8804,
        "lon": -43.4651,
    },
    "CG": {
        "regiao": "Campo Grande",
        "ra_codigo": "XVIII",
        "ra_nome": "XVIII — Campo Grande",
        "ra_ips_key": "XVIII CAMPO GRANDE",
        "bairros_censo": ["Campo Grande", "Cosmos", "Inhoaíba", "Senador Vasconcelos", "Santíssimo"],
        "lat": -22.9038,
        "lon": -43.5592,
    },
    "PG": {
        "regiao": "Pedra de Guaratiba",
        "ra_codigo": "XXVI",
        "ra_nome": "XXVI — Guaratiba",
        "ra_ips_key": "XXVI GUARATIBA",
        "bairros_censo": ["Guaratiba", "Barra de Guaratiba", "Pedra de Guaratiba"],
        "lat": -22.9961,
        "lon": -43.6339,
    },
}


def normalize_str(s):
    if not isinstance(s, str):
        return ""
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").upper().strip()


def load_ibge_arborizacao():
    ibge_path = SILVER_DIR / "ibge_entorno_bairro_rj.csv"
    df_ibge = pd.read_csv(ibge_path, low_memory=False)
    df_ibge["NM_NORM"] = df_ibge["NM_BAIRRO"].apply(normalize_str)

    ra_arborizacao = {}
    for est_code, cfg in ESTACOES_CONFIG.items():
        bairros_norm = [normalize_str(b) for b in cfg["bairros_censo"]]
        sub = df_ibge[df_ibge["NM_NORM"].isin(bairros_norm)]
        total_dom = sub["V05000"].sum()
        dom_arb = sub["V05027"].sum()
        pct_arb = (dom_arb / total_dom * 100) if total_dom > 0 else 0.0
        ra_arborizacao[est_code] = {
            "total_domicilios": int(total_dom),
            "qtd_domicilios_arborizados": int(dom_arb),
            "pct_arborizacao_2022": round(pct_arb, 2),
        }
    return ra_arborizacao


def load_ips_data():
    ips_path = SILVER_DIR / "ips_ra_rj_2024.xlsx"
    df_raw = pd.read_excel(ips_path, sheet_name="Dimensões e Componentes 2024", header=None)
    df_data = df_raw.iloc[8:41].copy()

    cols = [
        "ra_nome", "ips_geral", "dim_necessidades", "nutricao", "agua_saneamento", "moradia", "seguranca",
        "dim_bem_estar", "acesso_conhecimento", "acesso_info", "saude_bem_estar", "meio_ambiente",
        "dim_oportunidades", "direitos", "liberdade", "inclusao", "ensino_superior"
    ]
    df_data.columns = cols
    df_data["ra_norm"] = df_data["ra_nome"].apply(normalize_str)

    ips_dict = {}
    for est_code, cfg in ESTACOES_CONFIG.items():
        target = cfg["ra_ips_key"]
        match = df_data[df_data["ra_norm"] == target]
        if not match.empty:
            r = match.iloc[0]
            ips_dict[est_code] = {
                "ips_2024": round(float(r["ips_geral"]), 2),
                "ips_dim_necessidades": round(float(r["dim_necessidades"]), 2),
                "ips_dim_bem_estar": round(float(r["dim_bem_estar"]), 2),
                "ips_dim_oportunidades": round(float(r["dim_oportunidades"]), 2),
                "ips_comp_meio_ambiente": round(float(r["meio_ambiente"]), 2),
                "ips_dim_moradia": round(float(r["moradia"]), 2),
            }
        else:
            raise ValueError(f"RA {target} não encontrada no arquivo do IPS.")
    return ips_dict


def clean_hourly_monitorar():
    mon_path = SILVER_DIR / "monitorar_horario_rj_2024.csv"
    df = pd.read_csv(mon_path, low_memory=False)
    df["data"] = pd.to_datetime(df["data"])

    # Limpeza de limites físicos
    df.loc[(df["temp"] < -5) | (df["temp"] > 50), "temp"] = np.nan
    df.loc[(df["ur"] < 0) | (df["ur"] > 100), "ur"] = np.nan
    df.loc[df["chuva"] < 0, "chuva"] = np.nan

    pollutants = ["pm10", "pm2_5", "o3", "no2", "co", "so2"]
    for p in pollutants:
        if p in df.columns:
            df.loc[df[p] < 0, p] = np.nan

    # Exportar Parquet na camada Gold
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    out_parquet = GOLD_DIR / "massa_horaria_rj_2024.parquet"
    df.to_parquet(out_parquet, index=False, engine="pyarrow")
    print(f"[Gold] Massa horária salva em {out_parquet.name} ({len(df)} registros)")

    return df


def calculate_isa(df_hourly, df_daily_agg):
    print("Calculando estressores e sintetizando o ISA 2024...")
    df_hourly["mes"] = df_hourly["data"].dt.month

    # 1. Estresse Térmico: horas com temp > 32
    calor_df = df_hourly[df_hourly["temp"] > 32].groupby(["estação", "mes"]).size().rename("horas_calor")

    # 2. Estresse Hídrico: horas com ur < 40
    seco_df = df_hourly[df_hourly["ur"] < 40].groupby(["estação", "mes"]).size().rename("horas_seco")

    # 3. Estresse de Alagamento: dias no mês com chuva_dia > 50
    chuva_df = df_daily_agg[df_daily_agg["chuva_dia"] > 50].groupby(["estação", "mes"]).size().rename("dias_chuva_extrema")

    # 4. Estresse de Poluição: média de PM10 no mês
    pol_df = df_hourly.groupby(["estação", "mes"])["pm10"].mean().rename("pm10_mensal")

    # Criar grid completo de 8 estações x 12 meses
    estacoes = list(ESTACOES_CONFIG.keys())
    meses = list(range(1, 13))
    grid = pd.MultiIndex.from_product([estacoes, meses], names=["estação", "mes"]).to_frame().reset_index(drop=True)

    stress = grid.merge(calor_df, on=["estação", "mes"], how="left").fillna(0)
    stress = stress.merge(seco_df, on=["estação", "mes"], how="left").fillna(0)
    stress = stress.merge(chuva_df, on=["estação", "mes"], how="left").fillna(0)
    stress = stress.merge(pol_df, on=["estação", "mes"], how="left")

    # Se alguma estação/mês não tiver medição de PM10 (ex: SC), usar a média global mensal
    stress["pm10_mensal"] = stress["pm10_mensal"].fillna(stress.groupby("mes")["pm10_mensal"].transform("mean")).fillna(stress["pm10_mensal"].mean())

    # Normalização Min-Max dos 4 estressores [0, 1]
    for col in ["horas_calor", "horas_seco", "dias_chuva_extrema", "pm10_mensal"]:
        min_v = stress[col].min()
        max_v = stress[col].max()
        stress[f"norm_{col}"] = (stress[col] - min_v) / (max_v - min_v) if max_v > min_v else 0.0

    # Fórmula do ISA: 100 - (30*calor + 20*seco + 20*chuva + 30*poluicao) + ruído
    np.random.seed(42)
    isa_bruto = 100.0 - (
        30.0 * stress["norm_horas_calor"]
        + 20.0 * stress["norm_horas_seco"]
        + 20.0 * stress["norm_dias_chuva_extrema"]
        + 30.0 * stress["norm_pm10_mensal"]
    )
    noise = np.random.normal(0, 3.0, size=len(stress))
    stress["isa"] = np.clip(isa_bruto + noise, 0.0, 100.0).round(2)

    # Classificação categórica
    stress["isa_classe"] = pd.cut(
        stress["isa"],
        bins=[-np.inf, 50.0, 70.0, np.inf],
        labels=["Ruim", "Regular", "Boa"],
        right=False,
    )

    return stress[["estação", "mes", "isa", "isa_classe"]]


def build_gold_daily_dataset():
    df_hourly = clean_hourly_monitorar()
    ibge_dict = load_ibge_arborizacao()
    ips_dict = load_ips_data()

    print("Agregando dados horários para o grão diário...")
    df_hourly["data_dia"] = df_hourly["data"].dt.date
    df_hourly["mes"] = df_hourly["data"].dt.month

    # Agregações diárias
    daily_rows = []
    dates_2024 = pd.date_range("2024-01-01", "2024-12-31", freq="D")

    for est_code, cfg in ESTACOES_CONFIG.items():
        est_df = df_hourly[df_hourly["estação"] == est_code]
        
        # Limite de outlier para PM10 por IQR na estação
        pm10_series = est_df["pm10"].dropna()
        if len(pm10_series) > 10:
            q1, q3 = np.percentile(pm10_series, [25, 75])
            iqr = q3 - q1
            pm10_upper = q3 + 1.5 * iqr
        else:
            pm10_upper = 999.0

        for cur_dt in dates_2024:
            cur_date = cur_dt.date()
            day_sub = est_df[est_df["data_dia"] == cur_date]

            # Médias e extremos
            def get_mean(series, min_count=12):
                v = series.dropna()
                return round(float(v.mean()), 2) if len(v) >= min_count else np.nan

            def get_max(series):
                v = series.dropna()
                return round(float(v.max()), 2) if len(v) > 0 else np.nan

            def get_min(series):
                v = series.dropna()
                return round(float(v.min()), 2) if len(v) > 0 else np.nan

            pm10_m = get_mean(day_sub["pm10"])
            pm10_mx = get_max(day_sub["pm10"])
            flag_missing_pm10 = 1 if np.isnan(pm10_m) else 0
            flag_outlier_pm10 = 1 if (pm10_mx is not np.nan and pm10_mx > pm10_upper) else 0

            pm2_5_m = get_mean(day_sub["pm2_5"], min_count=6)
            o3_m = get_mean(day_sub["o3"])
            o3_mx = get_max(day_sub["o3"])
            no2_m = get_mean(day_sub["no2"])
            co_m = get_mean(day_sub["co"])
            so2_m = get_mean(day_sub["so2"])

            temp_m = get_mean(day_sub["temp"])
            temp_mx = get_max(day_sub["temp"])
            temp_mn = get_min(day_sub["temp"])
            ur_m = get_mean(day_sub["ur"])
            ur_mn = get_min(day_sub["ur"])
            chuva_d = round(float(day_sub["chuva"].sum(min_count=1)), 2)
            if np.isnan(chuva_d):
                chuva_d = 0.0

            daily_rows.append({
                "data": cur_dt.strftime("%Y-%m-%d"),
                "mes": cur_dt.month,
                "dia_ano": cur_dt.dayofyear,
                "estação": est_code,
                "regiao": cfg["regiao"],
                "ra_codigo": cfg["ra_codigo"],
                "ra_nome": cfg["ra_nome"],
                "lat": cfg["lat"],
                "lon": cfg["lon"],
                "pm10_media": pm10_m,
                "pm10_max": pm10_mx,
                "pm2_5_media": pm2_5_m,
                "o3_media": o3_m,
                "o3_max": o3_mx,
                "no2_media": no2_m,
                "co_media": co_m,
                "so2_media": so2_m,
                "temp_media": temp_m,
                "temp_max": temp_mx,
                "temp_min": temp_mn,
                "ur_media": ur_m,
                "ur_min": ur_mn,
                "chuva_dia": chuva_d,
                "flag_missing_pm10": flag_missing_pm10,
                "flag_outlier_pm10": flag_outlier_pm10,
            })

    df_daily = pd.DataFrame(daily_rows)

    # Imputação temporal suave para preencher lacunas de cálculo contínuo
    print("Aplicando interpolação e calculando flags de rastreabilidade...")
    df_daily["flag_imputado"] = 0
    interpolated_cols = ["pm10_media", "temp_media", "ur_media", "o3_media"]
    
    for est_code in ESTACOES_CONFIG.keys():
        mask = df_daily["estação"] == est_code
        for c in interpolated_cols:
            is_na = df_daily.loc[mask, c].isna()
            df_daily.loc[mask & is_na, "flag_imputado"] = 1
            # Interpolar linearmente e preencher bordas com média da estação
            df_daily.loc[mask, c] = df_daily.loc[mask, c].interpolate(method="linear").bfill().ffill()

    # Cálculo Diferencial (Derivadas) e Integral (Trapézios)
    print("Calculando derivadas instantâneas e integrais de exposição acumulada...")
    df_daily["derivada_pm10"] = 0.0
    df_daily["derivada_temp"] = 0.0
    df_daily["integral_acumulada_pm10"] = 0.0
    df_daily["integral_acumulada_pm2_5"] = 0.0

    for est_code in ESTACOES_CONFIG.keys():
        idx = df_daily[df_daily["estação"] == est_code].index
        pm10_vals = df_daily.loc[idx, "pm10_media"].values
        temp_vals = df_daily.loc[idx, "temp_media"].values

        # Derivadas discretas por gradiente central
        df_daily.loc[idx, "derivada_pm10"] = np.gradient(pm10_vals).round(2)
        df_daily.loc[idx, "derivada_temp"] = np.gradient(temp_vals).round(2)

        # Integrais acumuladas (Regra dos Trapézios acumulada)
        integ_pm10 = np.zeros(len(pm10_vals))
        for i in range(1, len(pm10_vals)):
            integ_pm10[i] = integ_pm10[i - 1] + 0.5 * (pm10_vals[i - 1] + pm10_vals[i])
        df_daily.loc[idx, "integral_acumulada_pm10"] = np.round(integ_pm10, 2)

        # Para PM2.5 (Irajá), preencher integral onde houver dados
        pm2_5_vals = df_daily.loc[idx, "pm2_5_media"].fillna(0).values
        integ_pm2_5 = np.zeros(len(pm2_5_vals))
        for i in range(1, len(pm2_5_vals)):
            integ_pm2_5[i] = integ_pm2_5[i - 1] + 0.5 * (pm2_5_vals[i - 1] + pm2_5_vals[i])
        df_daily.loc[idx, "integral_acumulada_pm2_5"] = np.round(integ_pm2_5, 2) if est_code == "IR" else np.nan

    # Enriquecimento com IPS 2024 e Censo 2022
    for est_code, data in ips_dict.items():
        mask = df_daily["estação"] == est_code
        for k, v in data.items():
            df_daily.loc[mask, k] = v

    for est_code, data in ibge_dict.items():
        mask = df_daily["estação"] == est_code
        for k, v in data.items():
            df_daily.loc[mask, k] = v

    # Cálculo do ISA 2024 e merge
    isa_df = calculate_isa(df_hourly, df_daily)
    df_daily = df_daily.merge(isa_df, on=["estação", "mes"], how="left")

    # Reordenar colunas conforme especificação do Dicionário de Dados
    final_cols = [
        "data", "mes", "dia_ano", "regiao", "ra_codigo", "ra_nome", "lat", "lon",
        "pm10_media", "pm10_max", "pm2_5_media", "o3_media", "o3_max", "no2_media", "co_media", "so2_media",
        "temp_media", "temp_max", "temp_min", "ur_media", "ur_min", "chuva_dia",
        "derivada_pm10", "derivada_temp", "integral_acumulada_pm10", "integral_acumulada_pm2_5",
        "ips_2024", "ips_dim_necessidades", "ips_dim_bem_estar", "ips_dim_oportunidades", "ips_comp_meio_ambiente", "ips_dim_moradia",
        "pct_arborizacao_2022", "qtd_domicilios_arborizados", "total_domicilios",
        "isa", "isa_classe",
        "flag_missing_pm10", "flag_outlier_pm10", "flag_imputado"
    ]

    df_daily = df_daily[final_cols]

    out_csv = GOLD_DIR / "massa_dados.csv"
    df_daily.to_csv(out_csv, index=False, encoding="utf-8-sig")
    print(f"\n[Gold] Massa diária consolidada salva em {out_csv} ({len(df_daily)} linhas x {len(df_daily.columns)} colunas)")

    # Validação rápida de integridade
    print("\n--- Validação da Camada Gold ---")
    print(f"Total de linhas esperado: 2928 | Obtido: {len(df_daily)}")
    print("Contagem de linhas por Região:\n", df_daily["regiao"].value_counts())
    print("\nResumo do ISA por Região:\n", df_daily.groupby("regiao")[["isa", "pct_arborizacao_2022", "ips_2024"]].mean().round(2))


def main():
    print("=== INICIANDO PIPELINE DE ETL SILVER -> GOLD ===")
    build_gold_daily_dataset()
    print("\n=== PIPELINE FINALIZADO COM SUCESSO ===")


if __name__ == "__main__":
    main()
