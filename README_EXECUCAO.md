# Como rodar a extração no seu PC

Estes scripts baixam os dados REAIS diretamente das fontes públicas
(MonitorAr-Rio, IBGE, IPS Rio), recortados para **2024**. Rode-os no seu
computador — daqui do ambiente Claude não é possível, porque os domínios do
governo (data.rio, arcgis.com, ftp.ibge.gov.br) ficam bloqueados pela política
de rede desse ambiente na nuvem.

## 1. Pré-requisitos (uma vez só)

Abra o PowerShell ou o Prompt de Comando nesta pasta (`Data-Flora`) e rode:

```
pip install -r requirements.txt
```

## 2. Rodar a extração, em ordem

```
python scripts/01_extract_monitorar.py
python scripts/02_extract_ibge_entorno.py
python scripts/03_extract_ips.py
```

O script 1 (MonitorAr) já vem filtrado só para 2024 (~70 mil linhas horárias,
8 estações) — cabe em 3 páginas de 32 mil registros, então roda em poucos
minutos.

## 3. O que esperar em `dados_brutos/`

- `monitorar_horario_2024.csv` — qualidade do ar + temperatura/umidade/chuva,
  horário, 8 estações, ano de 2024
- `ibge_entorno_bairro_BR.csv` — Censo 2022 (o mais recente que existe — não
  há Censo 2024), arborização e infraestrutura do entorno, todos os bairros
  do Brasil (arquivo de conferência)
- `ibge_entorno_bairro_rj.csv` — o mesmo, já filtrado para o Rio de Janeiro
  (se o filtro automático não achar a coluna certa, o script avisa e você
  filtra manualmente — é só abrir o CSV nacional e conferir o nome da coluna
  de município). Esse dado entra na massa de 2024 como **proxy** (a
  arborização de um bairro não muda de um ano para o outro), não como dado
  do próprio ano.
- `ips_ra_2024.xlsx` — Índice de Progresso Social por Região Administrativa.
  O arquivo baixado traz todas as edições (2016 a 2024); ao montar a massa,
  usar só a coluna/edição **2024**.

## 4. Se algum download falhar

- **MonitorAr**: se parar no meio, rode de novo — ele refaz do zero (não é
  incremental). Se der erro 429/503 muitas vezes seguidas, espere alguns
  minutos e tente de novo.
- **IPS**: se o link automático não funcionar, o script avisa e mostra o link
  da página para baixar manualmente: https://www.data.rio/documents/918dd39478594792a9cfa7080b84c0b5
- **IBGE**: o arquivo é grande (~1 MB compactado, mas o Brasil inteiro) —
  se a conexão cair, rode de novo.

## 5. Próximo passo

Depois que os 3 arquivos estiverem em `dados_brutos/`, o próximo passo do
plano (`docs/plano_arborizacao_rj.md`, seção 7, Dia 2) é o notebook de
preparação e qualidade — me avise quando quiser que eu monte ele.
