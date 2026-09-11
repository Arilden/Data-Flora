# ANTIGRAVITY.md

Contexto e diretrizes operacionais para o agente **Antigravity** (Google DeepMind) atuando no repositório **Data Flora**.

---

## 1. Sobre o Projeto

Este é um projeto avançado de engenharia e análise estatística de dados socioambientais: investigação da relação entre **distribuição da arborização urbana**, **saúde vegetal/arbórea (estimada)**, **qualidade do ar** e **estratificação socioeconômica** nas regiões do município do Rio de Janeiro.

* **Pergunta Central:** Regiões de menor nível socioeconômico possuem menos árvores — e as árvores presentes encontram-se sob pior estado de saúde e maior estresse ambiental?
* **Recorte Temporal Estrito:** **Ano de 2024** (01/01/2024 a 31/12/2024 — 366 dias, ano bissexto).
* **Unidade Territorial de Análise:** As 8 estações fixas de monitoramento do **MonitorAr-Rio**, mapeadas para as suas respectivas Regiões Administrativas (RA):
  * `AV`: II — Centro
  * `SC`: VII — São Cristóvão
  * `CA`: V — Copacabana
  * `SP`: VIII — Tijuca
  * `IR`: XIV — Irajá
  * `BG`: XVII — Bangu
  * `CG`: XVIII — Campo Grande
  * `PG`: XXVI — Guaratiba

---

## 2. Fontes de Verdade e Documentação Obrigatória

Antes de executar alterações ou análises, consulte os documentos normativos na pasta [`docs/`](file:///C:/Users/Victor%20Guida/Documents/1_FIAP/Data%20Flora/docs):

1. [`docs/plano_arborizacao_rj.md`](file:///C:/Users/Victor%20Guida/Documents/1_FIAP/Data%20Flora/docs/plano_arborizacao_rj.md) — Plano de desenvolvimento completo (v3.1), pipeline estatístico (amostragem, descritiva, derivadas, integrais, testes de hipóteses, correlação), estrutura do dashboard e decisões de escopo registradas.
2. [`docs/dicionario_de_dados.md`](file:///C:/Users/Victor%20Guida/Documents/1_FIAP/Data%20Flora/docs/dicionario_de_dados.md) e [`docs/dicionario_de_dados.csv`](file:///C:/Users/Victor%20Guida/Documents/1_FIAP/Data%20Flora/docs/dicionario_de_dados.csv) — Catálogo com as 72 variáveis tipadas, unidades de medida e classificação de natureza.
3. [`docs/especificacao_etl_silver_gold.md`](file:///C:/Users/Victor%20Guida/Documents/1_FIAP/Data%20Flora/docs/especificacao_etl_silver_gold.md) — Raciocínio matemático, fórmulas de limpeza, interpolação, derivadas discretas, regra dos trapézios e formulação do ISA.

---

## 3. Regras Invioláveis de Escopo e Metodologia

* **Recorte Fechado em 2024:** Não expandir para outros anos sem solicitação explícita.
* **Índice de Saúde Arbórea (ISA) é Métrica Derivada:** Calculado unicamente a partir de estressores microclimáticos reais de 2024 ($E_{\text{calor}}, E_{\text{seco}}, E_{\text{chuva}}, E_{\text{poluicao}}$). **Renda e IPS nunca entram na fórmula**, prevenindo correlação circular. Deve ser sempre identificado como *dado derivado*.
* **Arborização é Dado Proxy (Censo IBGE 2022):** Como não existe Censo em 2024, os dados do Censo 2022 entram como *proxy estrutural*. Deve ser sempre rotulado explicitamente como tal.
* **Arquitetura Medallion Rigorosa:** Todos os dados processados residem em `bronze/`, `silver/` e `gold/`. **Não criar ou duplicar arquivos de dados na raiz do repositório**.

---

## 4. Estrutura de Diretórios

```
Data-Flora/
├── bronze/                 # Dados brutos ingeridos exatamente como vieram da fonte
│   ├── monitorar_horario_2024.csv
│   ├── ibge_entorno_bairro_BR.csv
│   └── ips_ra_2024.xlsx
├── silver/                 # Dados filtrados, validados e padronizados para o Rio de Janeiro
│   ├── monitorar_horario_rj_2024.csv
│   ├── ibge_entorno_bairro_rj.csv
│   └── ips_ra_rj_2024.xlsx
├── gold/                   # Massas analíticas consolidadas prontas para consumo
│   ├── massa_dados.csv     # Grão diário: 8 regiões × 366 dias = 2.928 linhas × 40 colunas
│   └── massa_horaria_rj_2024.parquet # Série horária completa limpa (70.272 linhas)
├── docs/                   # Documentação técnica, dicionários e especificações
│   ├── plano_arborizacao_rj.md
│   ├── dicionario_de_dados.md
│   ├── dicionario_de_dados.csv
│   └── especificacao_etl_silver_gold.md
├── scripts/                # Automação de extração e pipelines de ETL
│   ├── 01_extract_monitorar.py
│   ├── 02_extract_ibge_entorno.py
│   ├── 03_extract_ips.py
│   ├── 04_organize_bronze_silver.py
│   └── 05_run_etl_gold.py
├── requirements.txt        # Dependências Python do projeto
├── README_EXECUCAO.md      # Instruções de reprodução da extração
├── CLAUDE.md               # Contexto para agentes legados
└── ANTIGRAVITY.md          # Este arquivo (Diretrizes do agente Antigravity)
```

---

## 5. Pipeline de Execução dos Scripts

Para reproduzir a extração e o processamento de dados do zero:

```powershell
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Extração das fontes públicas primárias
python scripts/01_extract_monitorar.py
python scripts/02_extract_ibge_entorno.py
python scripts/03_extract_ips.py

# 3. Organização e filtragem Bronze -> Silver (Rio de Janeiro)
python scripts/04_organize_bronze_silver.py

# 4. Pipeline de Engenharia & Métricas Estatísticas Silver -> Gold
python scripts/05_run_etl_gold.py
```
