# Dicionário de Dados — Projeto Data Flora (Arborização, Saúde Arbórea e Qualidade do Ar RJ)

**Versão:** 1.0  
**Data:** 11/09/2026  
**Recorte Temporal:** Ano de 2024  
**Unidade Territorial:** Regiões Administrativas (RA) do Município do Rio de Janeiro correspondentes às 8 estações fixas do MonitorAr  

---

## 1. Classificação da Natureza dos Dados

Para garantir transparência metodológica e rigor estatístico, cada variável do projeto é classificada em uma de quatro naturezas:

1. **Dado Real (2024):** Medição empírica primária coletada no ano de 2024 por órgãos oficiais (ex.: medições horárias de poluentes e meteorologia do MonitorAr-Rio, pontuações do IPS Rio 2024).
2. **Dado Proxy (Censo 2022 para 2024):** Dado empírico censitário coletado pelo IBGE no Censo Demográfico de 2022, adotado como aproximação estrutural estável para 2024 (a cobertura arbórea de vias urbanas não varia bruscamente em curtos intervalos temporais).
3. **Métrica Derivada / Sintética (2024):** Indicador modelado matematicamente a partir de variáveis reais exclusivamente ambientais de 2024 (ex.: **Índice de Saúde Arbórea — ISA**, derivadas numéricas e integrais de exposição acumulada). Renda e IPS nunca integram a fórmula para prevenir circularidade analítica.
4. **Flag de Qualidade / Rastreabilidade:** Variável booleana ou categórica que documenta a integridade, presença de valores ausentes, detecção de outliers ou processos de imputação.

---

## 2. Dicionário das Bases Brutas (Entrada)

### 2.1 MonitorAr-Rio (`dados_brutos/monitorar_horario_2024.csv`)
* **Fonte:** Secretaria Municipal do Ambiente e Clima (SMAC / PCRJ) via ArcGIS FeatureServer
* **Granularidade:** Estação $\times$ Registro Horário (70.272 linhas em 2024)

| Coluna | Tipo | Unidade | Natureza | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `objectid` | Inteiro | — | Real (2024) | Identificador sequencial único do registro no banco ArcGIS. |
| `data` | Datetime | ISO 8601 / Epoch | Real (2024) | Data e hora da medição (padronizado GMT-3 desde nov/2023). |
| `codnum` | Inteiro | — | Real (2024) | Código numérico da estação de monitoramento. |
| `estação` | Texto | — | Real (2024) | Sigla da estação (`AV`, `BG`, `CA`, `CG`, `IR`, `PG`, `SC`, `SP`). |
| `chuva` | Float | mm | Real (2024) | Precipitação pluviométrica acumulada na hora. |
| `pres` | Float | mbar / hPa | Real (2024) | Pressão atmosférica local. |
| `rs` | Float | W/m² | Real (2024) | Radiação solar global. |
| `temp` | Float | °C | Real (2024) | Temperatura do ar na estação. |
| `ur` | Float | % | Real (2024) | Umidade relativa do ar. |
| `dir_vento` | Float | Graus (°) | Real (2024) | Direção predominante do vento (0° a 360°). |
| `vel_vento` | Float | m/s | Real (2024) | Velocidade do vento. |
| `pm10` | Float | µg/m³ | Real (2024) | Concentração horária de Partículas Inaláveis ($\le 10\,\mu\text{m}$). |
| `pm2_5` | Float | µg/m³ | Real (2024) | Concentração horária de Partículas Respiráveis Finas ($\le 2.5\,\mu\text{m}$). |
| `o3` | Float | µg/m³ | Real (2024) | Concentração horária de Ozônio troposférico. |
| `no2` | Float | µg/m³ | Real (2024) | Concentração horária de Dióxido de Nitrogênio. |
| `co` | Float | ppm | Real (2024) | Concentração horária de Monóxido de Carbono. |
| `so2` | Float | µg/m³ | Real (2024) | Concentração horária de Dióxido de Enxofre. |
| `lat` / `lon` | Float | Graus Decimais | Real | Coordenadas geográficas WGS84 da estação fixa. |

---

### 2.2 IBGE Censo 2022 — Entorno dos Domicílios (`dados_brutos/ibge_entorno_bairro_rj.csv`)
* **Fonte:** IBGE (Censo Demográfico 2022 — Agregados por Bairro)
* **Granularidade:** Bairro do Município do Rio de Janeiro (162 bairros)

| Coluna | Tipo | Unidade | Natureza | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `CD_BAIRRO` | Texto | — | Proxy (2022) | Código do Bairro IBGE (inicia com `3304557` para o RJ). |
| `NM_BAIRRO` | Texto | — | Proxy (2022) | Nome oficial do bairro no município do Rio de Janeiro. |
| `V05000` | Inteiro | Domicílios | Proxy (2022) | Total de domicílios particulares permanentes ocupados no bairro. |
| `V05027` | Inteiro | Domicílios | Proxy (2022) | Domicílios com presença de arborização no entorno imediato. |
| `V05028` | Inteiro | Domicílios | Proxy (2022) | Domicílios sem presença de arborização no entorno imediato. |
| `V05001` / `V05002` | Inteiro | Domicílios | Proxy (2022) | Domicílios com pavimentação e iluminação pública. |
| `V05005` / `V05006` | Inteiro | Domicílios | Proxy (2022) | Domicílios com bueiro/boca de lobo e esgoto a céu aberto. |

---

### 2.3 IPS Rio 2024 (`dados_brutos/ips_ra_2024.xlsx`)
* **Fonte:** Instituto Pereira Passos (IPP / Prefeitura do Rio)
* **Granularidade:** Região Administrativa (RA) — Edição 2024

| Coluna | Tipo | Escala | Natureza | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `COD_RA` | Texto | — | Real (2024) | Código oficial em algarismo romano ou número da Região Administrativa. |
| `NOME_RA` | Texto | — | Real (2024) | Nome da Região Administrativa do Rio de Janeiro. |
| `IPS_2024` | Float | 0 a 100 | Real (2024) | Índice de Progresso Social Geral consolidado na edição 2024. |
| `DIM_NECESSIDADES` | Float | 0 a 100 | Real (2024) | Dimensão 1: Necessidades Humanas Básicas (Nutrição, Água, Saneamento, Moradia, Segurança). |
| `DIM_BEM_ESTAR` | Float | 0 a 100 | Real (2024) | Dimensão 2: Fundamentos do Bem-Estar (Educação Básica, Informação, Saúde/Bem-Estar, Meio Ambiente). |
| `DIM_OPORTUNIDADES` | Float | 0 a 100 | Real (2024) | Dimensão 3: Oportunidades (Direitos Individuais, Liberdade, Inclusão, Acesso ao Ensino Superior). |
| `COMP_MEIO_AMBIENTE` | Float | 0 a 100 | Real (2024) | Componente específico de Qualidade do Meio Ambiente do IPS. |

---

## 3. Dicionário da Massa de Dados Consolidada (`massa_dados.csv` e Excel Aba "Massa")

* **Granularidade Final:** Região Administrativa $\times$ Dia do Ano de 2024 (8 regiões $\times$ 366 dias = **2.928 linhas**).

| Coluna | Tipo | Unidade | Natureza | Regra de Cálculo / Origem |
| :--- | :--- | :--- | :--- | :--- |
| `data` | Date | `AAAA-MM-DD` | Real (2024) | Data do calendário civil de 2024 (`2024-01-01` a `2024-12-31`). |
| `mes` | Inteiro | 1 a 12 | Real (2024) | Mês do ano correspondente. |
| `dia_ano` | Inteiro | 1 a 366 | Real (2024) | Dia sequencial no ano bissexto de 2024. |
| `regiao` | Texto | — | Real (2024) | Nome amigável da estação/região (Centro, Copacabana, Tijuca, etc.). |
| `ra_codigo` | Texto | — | Real | Código oficial da Região Administrativa (ex.: `II`, `V`, `VIII`, etc.). |
| `ra_nome` | Texto | — | Real | Denominação oficial da Região Administrativa. |
| `lat` / `lon` | Float | Graus | Real | Coordenadas da estação de referência da região. |
| `pm10_media` | Float | µg/m³ | Real (2024) | Média aritmética diária das 24 horas de $\text{PM}_{10}$. |
| `pm10_max` | Float | µg/m³ | Real (2024) | Valor máximo horário registrado de $\text{PM}_{10}$ no dia. |
| `pm2_5_media` | Float | µg/m³ | Real (2024) | Média aritmética diária das 24 horas de $\text{PM}_{2.5}$. |
| `o3_media` | Float | µg/m³ | Real (2024) | Média diária de Ozônio. |
| `o3_max` | Float | µg/m³ | Real (2024) | Máxima horária diária de Ozônio. |
| `no2_media` | Float | µg/m³ | Real (2024) | Média diária de Dióxido de Nitrogênio. |
| `co_media` | Float | ppm | Real (2024) | Média diária de Monóxido de Carbono. |
| `so2_media` | Float | µg/m³ | Real (2024) | Média diária de Dióxido de Enxofre. |
| `temp_media` | Float | °C | Real (2024) | Média diária de temperatura do ar. |
| `temp_max` | Float | °C | Real (2024) | Temperatura máxima registrada no dia. |
| `temp_min` | Float | °C | Real (2024) | Temperatura mínima registrada no dia. |
| `ur_media` | Float | % | Real (2024) | Média diária da umidade relativa do ar. |
| `ur_min` | Float | % | Real (2024) | Menor umidade relativa registrada no dia. |
| `chuva_dia` | Float | mm | Real (2024) | Precipitação total diária acumulada. |
| `derivada_pm10` | Float | µg/(m³·dia) | Derivado (2024) | Taxa instantânea de variação diária de $\text{PM}_{10}$ via diferenças finitas ($\nabla \text{PM}_{10}$). |
| `derivada_temp` | Float | °C/dia | Derivado (2024) | Taxa instantânea de variação diária da temperatura ($\nabla \text{Temp}$). |
| `integral_acumulada_pm10` | Float | µg·dia/m³ | Derivado (2024) | Exposição acumulada de $\text{PM}_{10}$ integrada até a data (Regra dos Trapézios). |
| `integral_acumulada_pm2_5` | Float | µg·dia/m³ | Derivado (2024) | Exposição acumulada de $\text{PM}_{2.5}$ integrada até a data (Regra dos Trapézios). |
| `ips_2024` | Float | 0 a 100 | Real (2024) | Índice de Progresso Social geral da RA na edição 2024. |
| `ips_dim_ambiente` | Float | 0 a 100 | Real (2024) | Pontuação do componente de Meio Ambiente no IPS 2024. |
| `ips_dim_moradia` | Float | 0 a 100 | Real (2024) | Pontuação do componente de Moradia no IPS 2024. |
| `pct_arborizacao_2022` | Float | % (0 a 1) | Proxy (2022) | Percentual de domicílios com arborização na RA ($\frac{\sum \text{V05027}}{\sum \text{V05000}}$). |
| `isa` | Float | 0 a 100 | Derivado (2024) | **Índice de Saúde Arbórea**: $100 - (30E_{\text{calor}} + 20E_{\text{seco}} + 20E_{\text{chuva}} + 30E_{\text{pol}}) + \epsilon$. |
| `isa_classe` | Texto | Categórico | Derivado (2024) | Classificação do ISA: `Boa` ($\ge 70$), `Regular` ($50\text{--}69$), `Ruim` ($< 50$). |
| `flag_missing_pm10` | Booleano | 0 ou 1 | Flag Qualidade | Indica ausência de dados brutos de $\text{PM}_{10}$ no dia. |
| `flag_outlier_pm10` | Booleano | 0 ou 1 | Flag Qualidade | Indica valor discrepante detectado pelo critério $1.5 \times \text{IQR}$. |
| `flag_imputado` | Booleano | 0 ou 1 | Flag Qualidade | Indica se o registro diário utilizou interpolação para preenchimento. |

---

## 4. Notas Metodológicas e Rastreabilidade

1. **Circularidade Proibida:** O cálculo de `isa` baseia-se unicamente nas variáveis físicas de estresse (`temp`, `ur`, `chuva`, `pm10`). As variáveis socioeconômicas (`ips_2024`, `pct_arborizacao_2022`) permanecem como variáveis explicativas independentes.
2. **Compatibilização Espacial:** Os 162 bairros do IBGE foram mapeados para as 33 Regiões Administrativas utilizando a tabela oficial de limites territoriais da PCRJ (data.rio), permitindo agregar com precisão a taxa de arborização para as 8 RAs com monitoramento do ar.
3. **Escopo Restrito:** Qualquer menção aos dados de arborização deve explicitar o uso do Censo 2022 como *proxy* estrutural para o cenário analisado em 2024.
