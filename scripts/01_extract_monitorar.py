"""
Extração — MonitorAr-Rio (qualidade do ar + meteorologia horária)
Fonte: Secretaria Municipal do Ambiente e Clima (SMAC) / Prefeitura do Rio
Serviço: ArcGIS FeatureServer (tabela 2 = dados horários das estações fixas)
  https://services1.arcgis.com/OlP4dGNtIcnD3RYf/arcgis/rest/services/
  Qualidade_do_ar_dados_horarios_2011_2018/FeatureServer/2

Período: SOMENTE O ANO DE 2024 (ajuste PERIODO_INICIO/PERIODO_FIM abaixo se precisar
de outro recorte). 2024 é bissexto: 8 estações x 24h x 366d ≈ 70 mil linhas, o que
cabe em ~3 páginas de 32.000 registros — bem mais rápido que uma janela multi-ano.
Limite do serviço: 32.000 registros por requisição -> pagina com resultOffset.
Sem chave de API. Sem limite de requisições documentado; o script já aplica
uma pausa entre páginas e retry com backoff em erros HTTP/timeout, então
não precisa ajustar nada para respeitar o servidor.

Saída: dados_brutos/monitorar_horario_2024.csv
"""

import sys
import time
from pathlib import Path

import pandas as pd
import requests

BASE_URL = (
    "https://services1.arcgis.com/OlP4dGNtIcnD3RYf/arcgis/rest/services/"
    "Qualidade_do_ar_dados_horarios_2011_2018/FeatureServer/2/query"
)

PERIODO_INICIO = "2024-01-01"
PERIODO_FIM = "2025-01-01"  # exclusivo: pega até 31/12/2024 23h

PAGE_SIZE = 32000  # maxRecordCount da camada
PAUSE_BETWEEN_PAGES = 1.0  # segundos
MAX_RETRIES = 5

OUT_PATH = Path(__file__).resolve().parent.parent / "dados_brutos" / "monitorar_horario_2024.csv"


def query_page(offset: int) -> dict:
    params = {
        "where": f"data >= DATE '{PERIODO_INICIO}' AND data < DATE '{PERIODO_FIM}'",
        "outFields": "*",
        "f": "json",
        "orderByFields": "objectid",
        "resultOffset": offset,
        "resultRecordCount": PAGE_SIZE,
        "returnGeometry": "false",
    }
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(BASE_URL, params=params, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                if "error" in data:
                    raise RuntimeError(f"Erro da API: {data['error']}")
                return data
            if resp.status_code in (429, 503):
                wait = 2 ** attempt
                print(f"  HTTP {resp.status_code}, aguardando {wait}s e tentando de novo...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
        except (requests.RequestException, ValueError) as exc:
            last_err = exc
            wait = 2 ** attempt
            print(f"  Falha ({exc}), tentativa {attempt}/{MAX_RETRIES}, aguardando {wait}s...")
            time.sleep(wait)
    raise RuntimeError(f"Não foi possível obter offset={offset} após {MAX_RETRIES} tentativas: {last_err}")


def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"Baixando MonitorAr-Rio ({PERIODO_INICIO} a {PERIODO_FIM}, exclusivo)...")

    all_rows = []
    offset = 0
    page_num = 1
    while True:
        print(f"Página {page_num} (offset={offset})...")
        data = query_page(offset)
        features = data.get("features", [])
        if not features:
            break
        rows = [f["attributes"] for f in features]
        all_rows.extend(rows)
        print(f"  {len(rows)} linhas recebidas (total acumulado: {len(all_rows)})")

        if len(rows) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
        page_num += 1
        time.sleep(PAUSE_BETWEEN_PAGES)

    if not all_rows:
        print("ATENÇÃO: nenhuma linha retornada. Confira o período e o endpoint.")
        sys.exit(1)

    df = pd.DataFrame(all_rows)

    # O campo "data" vem em epoch milissegundos (padrão ArcGIS) -> converter.
    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], unit="ms", errors="coerce")

    df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print(f"\nConcluído: {len(df)} linhas salvas em {OUT_PATH}")
    print(f"Estações encontradas: {sorted(df['estação'].dropna().unique().tolist()) if 'estação' in df.columns else 'coluna não encontrada'}")
    print(f"Período real dos dados: {df['data'].min()} a {df['data'].max()}" if "data" in df.columns else "")


if __name__ == "__main__":
    main()
