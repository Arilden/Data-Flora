# Plano de Desenvolvimento — Arborização, Saúde Arbórea e Qualidade do Ar no Rio de Janeiro

**Versão:** 3.0 — 11/09/2026
**Prazo de execução:** 5 dias
**Recorte temporal:** ano de **2024**

---

## 0. Objetivo

Construir uma massa de dados (real + derivada) sobre as regiões do município do Rio de Janeiro
que permita aplicar, com dado de verdade e não com exemplo de sala:

- amostragem (simples e estratificada)
- preparação e limpeza de dados
- limites e derivadas (taxa de variação de séries temporais)
- integrais (exposição acumulada)
- estatística descritiva
- testes de hipóteses
- correlação

**Pergunta de pesquisa:** regiões mais pobres têm menos árvores — e as árvores que têm estão em
pior estado de saúde? Qualidade do ar, calor, umidade e chuva entram como causas.

**Unidade de análise:** as 8 estações fixas do MonitorAr, cada uma mapeada para a sua Região
Administrativa (RA). Isso permite juntar ar (estação) + renda (RA) + arborização (bairro → RA).

| Estação            | RA                    |
|---------------------|-----------------------|
| Centro              | II — Centro           |
| São Cristóvão       | VII — São Cristóvão   |
| Copacabana          | V — Copacabana        |
| Tijuca              | VIII — Tijuca         |
| Irajá               | XIV — Irajá           |
| Bangu               | XVII — Bangu          |
| Campo Grande        | XVIII — Campo Grande  |
| Pedra de Guaratiba  | XXVI — Guaratiba      |

---

## 1. Decisões de escopo registradas

Esta seção documenta, com a razão de cada uma, as decisões tomadas ao longo do planejamento —
principalmente as motivadas pelo fechamento do recorte em **2024** (pedido em 11/09/2026).

| # | Decisão | Motivo | Onde impacta |
|---|---------|--------|---------------|
| D1 | Massa principal restrita a **01/01/2024–31/12/2024** (366 dias, ano bissexto) | Escopo pedido pela usuária: só 2024, não a série 2011–2026 completa | Extração MonitorAr, ISA, Excel, dashboard |
| D2 | MonitorAr filtrado direto na consulta (`where` da API), não baixado inteiro e depois cortado | Reduz de ~420 mil para ~70 mil linhas e de ~14 para ~3 requisições — mais rápido e mais barato | `scripts/01_extract_monitorar.py` |
| D3 | Sem conversão de fuso horário | O MonitorAr mudou de UTC para hora local (GMT-3) em 10/11/2023; como 2024 é inteiramente posterior a essa data, a limpeza de fuso — necessária numa janela multi-ano — deixa de ser um passo do notebook de qualidade | Simplifica notebook 02 (preparação) |
| D4 | IPS: baixar o arquivo único (traz 2016/2018/2020/2022/2024 juntos) mas usar **somente a coluna/edição 2024** ao montar a massa | O IPS é bienal — não existe uma forma de pedir "só 2024" na fonte; a série completa é mantida no bruto só para referência | `scripts/03_extract_ips.py`, notebook de preparação |
| D5 | Censo (arborização): usar a edição **2022** — a mais recente existente — como **proxy** de 2024, com marcação explícita em todo lugar | O Censo é decenal; não existe "Censo 2024". A arborização de um bairro muda pouco de um ano para o outro, o que torna 2022 uma aproximação razoável, mas isso não pode ser apresentado como dado medido em 2024 | Dicionário de dados, README, dashboard — marcar sempre como "Censo 2022, proxy para 2024" |
| D6 | Índice de Saúde Arbórea (ISA) continua **derivado**, calculado só com variáveis ambientais (calor, umidade, chuva, poluição) de 2024 — a renda/IPS não entra na fórmula | Evita raciocínio circular: se a correlação IPS × ISA aparecer depois, ela precisa emergir do dado, não da construção da métrica | Seção 2, aba "Regra_Sintese" do Excel |
| D7 | Alerta Rio (meteorologia alternativa) mantido só como plano B, sem automação | O site retorna 403 para acesso automatizado (bloqueio de scraping); o MonitorAr já traz temperatura/umidade/chuva na mesma tabela, então essa fonte é dispensável na prática | Seção 1.4 |
| D8 | Extração roda no **PC da usuária**, não no ambiente Claude na nuvem | data.rio, arcgis.com e ftp.ibge.gov.br são bloqueados pela política de rede do ambiente Claude; os scripts foram entregues prontos para rodar localmente, onde a rede é irrestrita | `README_EXECUCAO.md` |
| D9 | Arquivo de planejamento convertido de `.txt` para `.md` | Pedido da usuária, para leitura/edição mais fácil (formatação, tabelas, blocos de código) | Este arquivo |

---

## 2. Fontes de dados

### 2.1 MonitorAr-Rio — qualidade do ar + meteorologia horária (real) — fonte principal, ano 2024

- **Órgão:** Secretaria Municipal do Ambiente e Clima (SMAC) / Prefeitura do Rio
- **Página:** https://www.data.rio/datasets/5b1bf5c3e5114564bbf9b7a372b85e17_2
- **Cobertura da série completa:** 2011 a 2026, horário, 8 estações fixas + campanhas móveis —
  neste projeto, filtrar apenas 01/01/2024 a 31/12/2024 (decisão D1/D2).
- **Serviço ArcGIS (REST):**
  `https://services1.arcgis.com/OlP4dGNtIcnD3RYf/arcgis/rest/services/Qualidade_do_ar_dados_horarios_2011_2018/FeatureServer`
  (o nome "2011_2018" é legado; a tabela vai até 2026)
  - Layer 0 = estações (lat/lon, código) → usar para o mapa
  - Tabela 2 = dados horários das estações fixas → **massa principal**
  - Tabela 3 = dados horários das campanhas móveis → ignorar

- **Campos da Tabela 2:** `objectid, data, codnum, estação, chuva, pres, rs, temp, ur, dir_vento, vel_vento, so2, no2, hcnm, hct, ch4, co, no, nox, o3, pm10, pm2_5, lat, lon, x_utm_sirgas2000, y_utm_sirgas2000`

  Temperatura (`temp`), umidade relativa (`ur`) e chuva já estão na mesma tabela — não é
  preciso uma fonte meteorológica separada (Alerta Rio fica só como plano B, decisão D7).

**Extração:**

```
Endpoint: <FeatureServer>/2/query
where             = data >= DATE '2024-01-01' AND data < DATE '2025-01-01'
outFields         = *
f                 = json
orderByFields     = objectid
resultOffset      = N        (paginação)
resultRecordCount = 32000
```

**Limites:**
- `maxRecordCount` da camada = 32.000 registros por requisição → paginar com `resultOffset`.
- Volume esperado em 2024: 8 estações × 24 h × 366 dias (bissexto) ≈ 70.300 linhas → cabe em
  3 requisições (32.000 + 32.000 + ~6.300).
- ArcGIS Online não publica um rate limit numérico; aplica throttling em rajadas. Regra prática:
  1 requisição por vez, pausa de 1 s entre páginas, retry com backoff (2 s, 4 s, 8 s) em HTTP
  429/503. Rodar uma vez, salvar em CSV, nunca re-baixar a cada execução do notebook.
- Alternativa sem código: botão "Download" > CSV na página do data.rio (traz todos os anos,
  sem filtro — filtrar 2024 no pandas depois).

**Saída:** `dados_brutos/monitorar_horario_2024.csv`

**Extra da mesma fonte (opcional, para validação):** IQAr diário 2017–2024 e "Valores máximos,
médias anuais e validade dos dados 2011–2024" em
https://ambienteclima.prefeitura.rio/monitorar-2026-dados/ — usar só a linha de 2024 para
conferir as médias calculadas.

### 2.2 IPS Rio — Índice de Progresso Social por RA (real) — edição 2024

- **Órgão:** Instituto Pereira Passos (IPP)
- **Base de dados:** https://www.data.rio/documents/918dd39478594792a9cfa7080b84c0b5
  ("Base de dados do IPS por Regiões Administrativas — 2016/2018/2020/2022/2024")
- **Resumo executivo 2024:** https://www.data.rio/documents/8027e843895d467da91a7a8c747fd524
- **Formato:** planilha XLSX — download manual único, sem API, sem rate limit.
- A planilha traz todas as edições (2016 a 2024) juntas; **usar somente a edição 2024**
  (decisão D4) — as demais ficam no bruto só para referência.
- Usar: IPS geral 2024 + as 3 dimensões + componentes relevantes (ex.: "Qualidade do meio
  ambiente", "Moradia", "Saúde e bem-estar").
- Alternativa via SQL (Base dos Dados / BigQuery) cobre só 2016–2020, **não usar** como fonte
  principal aqui.

**Saída:** `dados_brutos/ips_ra_2024.xlsx`

### 2.3 IBGE Censo 2022 — Características urbanísticas do entorno dos domicílios (real, usado como proxy)

> **Importante (decisão D5):** o Censo é decenal, não existe "Censo 2024". A edição 2022 entra
> na massa de 2024 como a melhor aproximação disponível — precisa aparecer marcada como proxy
> em todo lugar (dicionário, README, dashboard).

- **Variável-chave:** existência de arborização no entorno do domicílio (sim/não, agregado).
  Também: iluminação, pavimentação, bueiro/boca de lobo, esgoto a céu aberto.
- **Página:** https://www.ibge.gov.br/geociencias/organizacao-do-territorio/tipologias-do-territorio/24702-caracteristicas-urbanisticas-do-entorno-dos-domicilios.html
- **FTP** (HTTP simples, sem autenticação, sem rate limit):
  `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios_Caracteristicas_urbanisticas_do_entorno_dos_domicilios/Agregados_por_Bairro_csv/`
  Arquivo: `Agregados_por_bairros_entorno_domicílios_BR.zip`
  Dicionário: `dicionarios_de_dados_entorno.zip` (26 KB, pasta acima)
- Usar a agregação **por bairro** (evita join espacial). Filtrar município `3304557`.
- Depois: bairro → RA usando a tabela oficial de bairros do data.rio.
- Métrica derivada: `pct_arborizacao = domicílios com arborização / domicílios total`, por RA.
- Bônus: pasta `Favelas_e_comunidades_urbanas_Caracteristicas_do_entorno` no mesmo FTP — mesmo
  indicador só para favelas, reforça a leitura de desigualdade.

**Saída:** `dados_brutos/ibge_entorno_bairro_rj.csv`

### 2.4 Alerta Rio — meteorologia (real) — plano B (decisão D7)

https://www.sistema-alerta-rio.com.br/download/dados-meteorologicos/ — download por formulário
(estação + período), sem API. Bloqueia acesso automatizado (403 para clientes não-navegador) —
só usar manualmente, se necessário, filtrando 2024.

### 2.5 Limites administrativos (real)

data.rio: "Limite de Bairros" e "Regiões Administrativas" (ArcGIS Hub, GeoJSON/CSV) —
https://www.data.rio/search?q=bairros — export único, sem rate limit, não muda com o ano.

### 2.6 O que não existe como dado aberto

Não há inventário arbóreo público com estado fitossanitário por RA (a Fundação Parques e
Jardins não publica isso em dados abertos). Por isso a saúde arbórea é **derivada** — ver
seção 3.

---

## 3. Dado derivado: Índice de Saúde Arbórea (ISA) — ano 2024

**Princípio (decisão D6):** a saúde é função só de variáveis ambientais reais medidas na região
em 2024. A renda não entra na fórmula. Se a correlação renda × saúde aparecer, ela emerge do
dado (regiões pobres têm de fato mais calor, menos umidade e mais PM10 em 2024), não da
construção da métrica — isso evita raciocínio circular e precisa ser dito na apresentação.

**Cálculo por região e por mês de 2024** (a partir do MonitorAr horário já limpo, 12 meses):

```
estresse_calor    = nº de horas com temp > 32 °C no mês
estresse_seco     = nº de horas com ur < 40 %
estresse_chuva    = nº de dias com chuva acumulada > 50 mm (proxy de alagamento)
estresse_poluicao = média mensal de PM10 (µg/m³)
```

Normalizar cada estresse para 0–1 (min-max sobre as 8 regiões × 12 meses de 2024).

```
ISA_bruto = 100 − (30·calor + 20·seco + 20·chuva + 30·poluicao)
ISA       = ISA_bruto + ruído ~ N(0, 3), seed = 42, truncado em [0, 100]
```

Pesos e limiares ficam documentados na aba "Regra_Sintese" do Excel e numa célula markdown do
notebook. O ruído existe para o dado não ser uma função determinística (senão a correlação com
os próprios insumos seria 1,0 por definição). Marcar a coluna como "derivado" no dicionário.

Opcional: classe categórica (Boa ≥ 70, Regular 50–69, Ruim < 50) para gráficos e testes
qui-quadrado.

---

## 4. Mapeamento método → dado

| Método | Dado usado | Onde |
|--------|-----------|------|
| Preparação/limpeza | MonitorAr horário 2024: nulos por estação/poluente, outliers (IQR), duplicatas, faixas válidas | notebook 01 + aba Limpeza |
| Amostragem | Amostra aleatória simples (n=1000) e estratificada por região (n=125/região) da massa horária 2024; comparar média amostral vs. populacional de PM10/temp | notebook 02 + aba Amostra |
| Estatística descritiva | Média, mediana, desvio, quartis, assimetria de cada poluente + temp + ur + ISA, por região, em 2024 | aba Descritiva |
| Limites e derivadas | d(PM10)/dt e d(temp)/dt na série diária de 2024 (`np.gradient`) → picos de variação, dias de maior aceleração | aba Derivadas |
| Integrais | ∫ PM2.5 dt ao longo de 2024 (`np.trapz`) = exposição acumulada anual por região; ranking de regiões | aba Integrais |
| Testes de hipóteses | H1: ISA médio 2024 difere entre regiões de IPS 2024 alto vs. baixo (t de Welch / Mann-Whitney); H2: `pct_arborizacao` difere entre esses grupos; H3: ANOVA de PM10 2024 entre as 8 regiões | aba Hipoteses |
| Correlação | Pearson + Spearman: IPS 2024, `pct_arborizacao`, PM10, PM2.5, temp, ur, ISA (2024) — matriz + heatmap | aba Correlacao |

---

## 5. Estrutura da massa final (`massa_dados.csv` → aba "Massa" do Excel)

Grão: região × dia de 2024 → 8 regiões × 366 dias = **2.928 linhas**. Colunas:

```
data, mes, regiao, ra_codigo, ra_nome, lat, lon,
pm10, pm2_5, o3, no2, co, so2 (médias diárias), pm10_max, o3_max,
temp_media, temp_max, ur_media, ur_min, chuva_dia,
ips_2024, ips_dim_ambiente, ips_dim_moradia (constantes por RA, edição 2024),
pct_arborizacao_2022 (constante por RA, proxy Censo 2022 para 2024),
isa (derivado, 2024), isa_classe (derivado),
flag_missing_pm10, flag_outlier_pm10 (rastreabilidade da limpeza)
```

A massa horária completa de 2024 (~70 mil linhas) fica em CSV/Parquet e vai para o SkyFlora.

---

## 6. Entregáveis

- [a] `dados_brutos/` — CSV/XLSX exatamente como baixados (não editar)
- [b] `scripts/01_extract_monitorar.py`, `02_extract_ibge_entorno.py`, `03_extract_ips.py`
- [c] `02_preparacao_qualidade.ipynb` — limpeza, nulos, outliers, join, ISA, relatório de qualidade
- [d] `03_analise.ipynb` — amostragem, descritiva, derivadas, integrais, hipóteses, correlação
- [e] `massa_dados.csv` (2.928 linhas) + `massa_horaria_2024.parquet` (~70 mil linhas)
- [f] `arborizacao_rj_2024.xlsx` — abas: Massa, Dicionario, Fontes, Regra_Sintese, Amostra,
      Limpeza, Descritiva, Derivadas, Integrais, Hipoteses, Correlacao (fórmulas nativas:
      MÉDIA, DESVPAD.A, CORREL, TESTE.T, QUARTIL)
- [g] Google Sheets com a aba Massa → fonte do Looker Studio
- [h] Dashboard Looker Studio: (1) barras IPS 2024 × `pct_arborizacao` por RA; (2) série temporal
      2024 de poluentes com filtro de região; (3) dispersão IPS × ISA; (4) exposição acumulada
      anual (integral) por região; notas de rodapé "ISA é índice derivado" e "arborização:
      Censo 2022, usado como proxy"
- [i] `README.md` — contexto, fontes (real vs. derivado/proxy), como rodar, achados
- [j] Bônus SkyFlora: notebook PySpark bronze (massa horária 2024) → silver (limpa) → gold
      (região×mês 2024)

---

## 7. Cronograma (5 dias)

| Dia | Foco |
|-----|------|
| 1 | Extração: rodar os 3 scripts (MonitorAr 2024 paginado — cabe em 3 páginas —, IPS XLSX, IBGE entorno por bairro). Escrever dicionário de dados e fechar a regra do ISA antes de gerar qualquer número. |
| 2 | Preparação e qualidade (notebook 02): relatório de completude por estação/poluente em 2024, join, ISA. Gerar `massa_dados.csv`. |
| 3 | Análise (notebook 03) e montagem do Excel com uma aba por método. |
| 4 | Google Sheets + Looker Studio. |
| 5 | Rodar tudo do zero, conferir Excel × Python, README. Só depois: SkyFlora bronze. |

---

## 8. Riscos e mitigação

- **Buracos de dados em 2024:** se alguma estação do MonitorAr tiver falhas grandes justamente
  em 2024, **não trocar de ano** — registrar a taxa de missing por estação/mês como achado do
  relatório de qualidade (é um resultado legítimo, não um defeito a esconder).
- **pm2_5 incompleto:** não existe em todas as estações. A integral de exposição usa PM10 onde
  PM2.5 faltar, com a coluna sinalizada.
- **Join bairro → RA:** o IPS é por RA e o Censo é por bairro; usar a tabela oficial de bairros
  do data.rio, não fazer o mapeamento manualmente.
- **ISA é derivado (2024):** aparece assim em todo lugar — dicionário, Excel, dashboard, README.
  Nunca chamar de "dado real".
- **Arborização é proxy (Censo 2022, não 2024):** marcada como tal em todo lugar que aparecer,
  com o ano explícito ao lado.
- **Alerta Rio bloqueia scraping (403):** não gastar tempo automatizando; só usar se necessário,
  baixando manualmente e já filtrando 2024.
