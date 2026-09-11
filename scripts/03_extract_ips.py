"""
Extração — IPS Rio (Índice de Progresso Social por Região Administrativa)
Fonte: Instituto Pereira Passos (IPP) / data.rio
Página do item: https://www.data.rio/documents/918dd39478594792a9cfa7080b84c0b5
Arquivo: Excel único com as edições 2016/2018/2020/2022/2024, sem paginação,
sem limite de requisições — é um download único.

Este projeto usa o recorte de 2024: o arquivo baixado traz todas as edições,
mas ao processar (notebook de preparação), usar SOMENTE a coluna/edição 2024
(a mais recente) — as demais ficam no arquivo só para referência.

Saída: dados_brutos/ips_ra_2024.xlsx
"""

from pathlib import Path

import requests

ITEM_ID = "918dd39478594792a9cfa7080b84c0b5"
DOWNLOAD_URL = f"https://www.arcgis.com/sharing/rest/content/items/{ITEM_ID}/data"
PAGINA_MANUAL = f"https://www.data.rio/documents/{ITEM_ID}"

OUT_PATH = Path(__file__).resolve().parent.parent / "dados_brutos" / "ips_ra_2024.xlsx"


def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    print("Baixando base do IPS Rio (Índice de Progresso Social por RA)...")
    try:
        resp = requests.get(DOWNLOAD_URL, timeout=60)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "")
        if "html" in content_type.lower():
            raise RuntimeError("O servidor devolveu uma página HTML em vez do arquivo .xlsx")
        OUT_PATH.write_bytes(resp.content)
        print(f"Concluído: arquivo salvo em {OUT_PATH} ({len(resp.content) / 1024:.0f} KB)")
    except Exception as exc:
        print(f"Falha no download automático ({exc}).")
        print(f"Baixe manualmente em: {PAGINA_MANUAL}")
        print(f"E salve o arquivo como: {OUT_PATH}")


if __name__ == "__main__":
    main()
