"""
Organização das camadas Bronze e Silver (Arquitetura Medallion):
- Bronze: dados brutos de entrada exatamente como ingeridos
- Silver: dados filtrados, padronizados e validados exclusivamente para o Rio de Janeiro (RJ)
"""

import shutil
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT_DIR / "dados_brutos"
BRONZE_DIR = ROOT_DIR / "bronze"
SILVER_DIR = ROOT_DIR / "silver"

MUNICIPIO_RJ_COD = "3304557"


def setup_bronze():
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    print("--- Organizando Camada BRONZE ---")
    
    files_to_copy = [
        "monitorar_horario_2024.csv",
        "ibge_entorno_bairro_BR.csv",
        "ips_ra_2024.xlsx",
    ]
    
    for filename in files_to_copy:
        src = RAW_DIR / filename
        dst = BRONZE_DIR / filename
        if src.exists():
            shutil.copy2(src, dst)
            size_kb = dst.stat().st_size / 1024
            print(f"  [Bronze] {filename} copiado com sucesso ({size_kb:.1f} KB).")
        else:
            print(f"  [AVISO] {src} não encontrado.")


def setup_silver():
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    print("\n--- Organizando Camada SILVER (Filtro Rio de Janeiro) ---")
    
    # 1. IBGE Entorno: filtrar estritamente para o Rio de Janeiro (3304557)
    ibge_raw = BRONZE_DIR / "ibge_entorno_bairro_BR.csv"
    if ibge_raw.exists():
        df_ibge = pd.read_csv(ibge_raw, low_memory=False)
        # Filtrar por código do bairro iniciando com 3304557
        col_cod = next((c for c in df_ibge.columns if c.upper() in ("CD_BAIRRO", "CD_MUN", "COD_MUNICIPIO")), None)
        if col_cod:
            df_ibge_rj = df_ibge[df_ibge[col_cod].astype(str).str.startswith(MUNICIPIO_RJ_COD)].copy()
            out_ibge_rj = SILVER_DIR / "ibge_entorno_bairro_rj.csv"
            df_ibge_rj.to_csv(out_ibge_rj, index=False, encoding="utf-8-sig")
            print(f"  [Silver] IBGE Entorno RJ gerado: {len(df_ibge_rj)} bairros do Rio de Janeiro salvos em {out_ibge_rj.name}.")
    
    # 2. MonitorAr-Rio 2024: dados das 8 estações da cidade do Rio de Janeiro
    monitorar_raw = BRONZE_DIR / "monitorar_horario_2024.csv"
    if monitorar_raw.exists():
        df_mon = pd.read_csv(monitorar_raw, low_memory=False)
        out_mon_rj = SILVER_DIR / "monitorar_horario_rj_2024.csv"
        df_mon.to_csv(out_mon_rj, index=False, encoding="utf-8-sig")
        print(f"  [Silver] MonitorAr-Rio 2024 gerado: {len(df_mon)} medições horárias salvas em {out_mon_rj.name}.")
        
    # 3. IPS Rio 2024: base oficial do Rio de Janeiro
    ips_raw = BRONZE_DIR / "ips_ra_2024.xlsx"
    if ips_raw.exists():
        out_ips_rj = SILVER_DIR / "ips_ra_rj_2024.xlsx"
        shutil.copy2(ips_raw, out_ips_rj)
        print(f"  [Silver] IPS Rio 2024 gerado: salvo em {out_ips_rj.name}.")


def main():
    setup_bronze()
    setup_silver()
    print("\nConcluído com sucesso: Camadas Bronze e Silver estruturadas.")


if __name__ == "__main__":
    main()
