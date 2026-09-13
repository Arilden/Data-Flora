# Dicionário de Dados Gerado — Data Flora

**Gerado em:** 2026-09-12T16:13:38.742394+00:00
**Status da validação:** APROVADO_COM_RESSALVAS_CRITICAS
**Cobertura:** 8 tabelas e 226 campos

Este catálogo foi construído a partir dos arquivos atuais das camadas Bronze, Silver e Gold. Tipos, tamanhos, precisão, nulidade, cardinalidade, limites e exemplos refletem os valores observados; descrições e unidades foram confrontadas com as fontes oficiais e com as regras do projeto.

## Alertas de integridade semântica

- **CRÍTICA — IBGE-V05027:** O ETL atual calcula pct_arborizacao_2022 e qtd_domicilios_arborizados com V05027, mas o dicionário oficial informa que V05027 mede rampa para cadeirante. Os campos de arborização são V05030–V05034.
- **CRÍTICA — MONITORAR-CA-AV:** A fonte oficial identifica CA como Centro e AV como Copacabana; o ESTACOES_CONFIG do ETL atual associa AV a Centro e CA a Copacabana.

## Validação automática

- **PASSOU — Cobertura de campos:** 226/226 campos catalogados.
- **PASSOU — Unicidade tabela/campo:** 0 duplicidades.
- **PASSOU — Metadados obrigatórios:** 0 valores obrigatórios ausentes.
- **PASSOU — Semântica oficial IBGE:** V05027 e V05030–V05034 conferidos contra o dicionário oficial.
- **PASSOU — Integridade MonitorAr 2024:** 70272 registros, 8 estações e objectid único.
- **PASSOU — Recorte IBGE Rio:** 162 bairros; códigos municipais válidos.
- **PASSOU — Grão da massa Gold:** 2928 linhas, 8 regiões e 366 dias por região.

## `bronze.monitorar_horario_2024`

- Arquivo: `bronze/monitorar_horario_2024.csv`
- Grão: Estação de monitoramento × hora
- Registros: 70272
- Descrição: Medições horárias brutas de qualidade do ar e meteorologia em 2024.

| Campo | Tipo lógico | Tamanho/precisão | Nulos % | Papel | Descrição | Observações |
|---|---|---|---:|---|---|---|
| `objectid` | INTEGER | INTEGER (7 dígitos observados) | 0.0 | Chave primária | Identificador único do registro no serviço ArcGIS. | — |
| `data` | DATETIME | DATETIME (precisão até segundos) | 0.0 | Chave temporal composta | Data e hora local da medição (GMT-3 em todo o recorte de 2024). | — |
| `codnum` | INTEGER | INTEGER (1 dígitos observados) | 0.0 | Chave de referência | Código numérico da estação de monitoramento. | — |
| `estação` | STRING | VARCHAR(2) observado | 0.0 | Chave espacial composta | Sigla oficial da estação MonitorAr: AV, BG, CA, CG, IR, PG, SC ou SP. | A configuração Gold atual inverte CA e AV; não usar o nome de região sem revisar esse mapeamento. |
| `chuva` | DECIMAL | DECIMAL(19,16) observado | 22.6178 | Atributo | Precipitação pluviométrica acumulada na hora. | — |
| `pres` | DECIMAL | DECIMAL(6,2) observado | 24.5076 | Atributo | Pressão atmosférica local. | — |
| `rs` | DECIMAL | DECIMAL(20,16) observado | 47.9764 | Atributo | Radiação solar global incidente. | — |
| `temp` | DECIMAL | DECIMAL(4,2) observado | 20.4349 | Atributo | Temperatura do ar na estação. | — |
| `ur` | DECIMAL | DECIMAL(5,2) observado | 20.331 | Atributo | Umidade relativa do ar. | — |
| `dir_vento` | DECIMAL | DECIMAL(5,2) observado | 23.2582 | Atributo | Direção predominante do vento. | — |
| `vel_vento` | DECIMAL | DECIMAL(17,16) observado | 23.2283 | Atributo | Velocidade do vento. | — |
| `so2` | DECIMAL | DECIMAL(18,16) observado | 95.0692 | Atributo | Concentração horária de dióxido de enxofre (SO₂). | — |
| `no2` | DECIMAL | DECIMAL(19,16) observado | 57.8609 | Atributo | Concentração horária de dióxido de nitrogênio (NO₂). | — |
| `hcnm` | DECIMAL | DECIMAL(17,16) observado | 88.9245 | Atributo | Concentração horária de hidrocarbonetos não metano (HCNM). | — |
| `hct` | DECIMAL | DECIMAL(17,16) observado | 88.9302 | Atributo | Concentração horária de hidrocarbonetos totais (HCT). | — |
| `ch4` | DECIMAL | DECIMAL(17,16) observado | 88.9245 | Atributo | Concentração horária de metano (CH₄). | — |
| `co` | DECIMAL | DECIMAL(17,16) observado | 76.8087 | Atributo | Concentração horária de monóxido de carbono (CO). | — |
| `no` | DECIMAL | DECIMAL(19,16) observado | 57.8338 | Atributo | Concentração horária de monóxido de nitrogênio (NO). | — |
| `nox` | DECIMAL | DECIMAL(19,16) observado | 57.8267 | Atributo | Concentração horária de óxidos de nitrogênio (NO + NO₂). | — |
| `o3` | DECIMAL | DECIMAL(19,16) observado | 18.8368 | Atributo | Concentração horária de ozônio troposférico (O₃). | — |
| `pm10` | INTEGER | INTEGER (3 dígitos observados) | 25.508 | Atributo | Concentração horária de material particulado inalável PM₁₀. | — |
| `pm2_5` | INTEGER | INTEGER (3 dígitos observados) | 88.1432 | Atributo | Concentração horária de material particulado fino PM₂,₅. | — |
| `lat` | DECIMAL | DECIMAL(17,15) observado | 0.0 | Atributo | Latitude da estação no sistema WGS 84. | — |
| `lon` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Longitude da estação no sistema WGS 84. | — |
| `x_utm_sirgas2000` | DECIMAL | DECIMAL(10,4) observado | 0.0 | Atributo | Coordenada leste UTM da estação, SIRGAS 2000 / zona 23S. | — |
| `y_utm_sirgas2000` | DECIMAL | DECIMAL(11,4) observado | 0.0 | Atributo | Coordenada norte UTM da estação, SIRGAS 2000 / zona 23S. | — |

## `bronze.ibge_entorno_bairro_BR`

- Arquivo: `bronze/ibge_entorno_bairro_BR.csv`
- Grão: Bairro do Brasil
- Registros: 17576
- Descrição: Agregados nacionais por bairro; proxy estrutural de 2022 para a análise de 2024.

| Campo | Tipo lógico | Tamanho/precisão | Nulos % | Papel | Descrição | Observações |
|---|---|---|---:|---|---|---|
| `CD_BAIRRO` | STRING | VARCHAR(10) observado | 0.0 | Chave primária | Código oficial do bairro no Censo Demográfico 2022. | — |
| `NM_BAIRRO` | STRING | VARCHAR(60) observado | 0.0 | Chave de referência | Nome oficial do bairro no Censo Demográfico 2022. | — |
| `V05000` | INTEGER | INTEGER (6 dígitos observados) | 0.0 | Atributo | Total de domicílios particulares permanentes ocupados em setor selecionado para o levantamento do entorno. | Definição conferida no dicionário oficial do IBGE. |
| `V05001` | INTEGER | INTEGER (6 dígitos observados) | 0.0 | Atributo | Domicílios em face com circulação de caminhão ou ônibus. | Definição conferida no dicionário oficial do IBGE. |
| `V05002` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face com circulação de carro de passeio ou van. | Definição conferida no dicionário oficial do IBGE. |
| `V05003` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face com circulação de pedestres, bicicletas ou motocicletas. | Definição conferida no dicionário oficial do IBGE. |
| `V05004` | INTEGER | INTEGER (2 dígitos observados) | 0.0 | Atributo | Domicílios em face com circulação por aquavia. | Definição conferida no dicionário oficial do IBGE. |
| `V05005` | INTEGER | INTEGER (4 dígitos observados) | 0.0 | Atributo | Domicílios sem declaração válida para o tipo de circulação da via (saltado). | Definição conferida no dicionário oficial do IBGE. |
| `V05006` | INTEGER | INTEGER (6 dígitos observados) | 0.0 | Atributo | Domicílios em face com via pavimentada. | Definição conferida no dicionário oficial do IBGE. |
| `V05007` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face sem via pavimentada. | Definição conferida no dicionário oficial do IBGE. |
| `V05008` | INTEGER | INTEGER (4 dígitos observados) | 0.0 | Atributo | Domicílios com pavimentação da via não declarada. | Definição conferida no dicionário oficial do IBGE. |
| `V05009` | INTEGER | INTEGER (6 dígitos observados) | 0.0 | Atributo | Domicílios em face com bueiro ou boca de lobo. | Definição conferida no dicionário oficial do IBGE. |
| `V05010` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face sem bueiro ou boca de lobo. | Definição conferida no dicionário oficial do IBGE. |
| `V05011` | INTEGER | INTEGER (4 dígitos observados) | 0.0 | Atributo | Domicílios com presença de bueiro não declarada. | Definição conferida no dicionário oficial do IBGE. |
| `V05012` | INTEGER | INTEGER (6 dígitos observados) | 0.0 | Atributo | Domicílios em face com iluminação pública. | Definição conferida no dicionário oficial do IBGE. |
| `V05013` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face sem iluminação pública. | Definição conferida no dicionário oficial do IBGE. |
| `V05014` | INTEGER | INTEGER (4 dígitos observados) | 0.0 | Atributo | Domicílios com iluminação pública não declarada. | Definição conferida no dicionário oficial do IBGE. |
| `V05015` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face com ponto de ônibus. | Definição conferida no dicionário oficial do IBGE. |
| `V05016` | INTEGER | INTEGER (6 dígitos observados) | 0.0 | Atributo | Domicílios em face sem ponto de ônibus. | Definição conferida no dicionário oficial do IBGE. |
| `V05017` | INTEGER | INTEGER (4 dígitos observados) | 0.0 | Atributo | Domicílios com presença de ponto de ônibus não declarada. | Definição conferida no dicionário oficial do IBGE. |
| `V05018` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face com via sinalizada para bicicleta. | Definição conferida no dicionário oficial do IBGE. |
| `V05019` | INTEGER | INTEGER (6 dígitos observados) | 0.0 | Atributo | Domicílios em face sem via sinalizada para bicicleta. | Definição conferida no dicionário oficial do IBGE. |
| `V05020` | INTEGER | INTEGER (4 dígitos observados) | 0.0 | Atributo | Domicílios com sinalização cicloviária não declarada. | Definição conferida no dicionário oficial do IBGE. |
| `V05021` | INTEGER | INTEGER (6 dígitos observados) | 0.0 | Atributo | Domicílios em face com calçada. | Definição conferida no dicionário oficial do IBGE. |
| `V05022` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face sem calçada. | Definição conferida no dicionário oficial do IBGE. |
| `V05023` | INTEGER | INTEGER (4 dígitos observados) | 0.0 | Atributo | Domicílios com presença de calçada não declarada. | Definição conferida no dicionário oficial do IBGE. |
| `V05024` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face com obstáculo na calçada. | Definição conferida no dicionário oficial do IBGE. |
| `V05025` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face sem obstáculo na calçada. | Definição conferida no dicionário oficial do IBGE. |
| `V05026` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios com obstáculo na calçada não declarado. | Definição conferida no dicionário oficial do IBGE. |
| `V05027` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face com rampa para cadeirante. | Definição conferida no dicionário oficial do IBGE. Atenção: o ETL atual usa este campo como arborização, mas ele mede rampa para cadeirante. |
| `V05028` | INTEGER | INTEGER (6 dígitos observados) | 0.0 | Atributo | Domicílios em face sem rampa para cadeirante. | Definição conferida no dicionário oficial do IBGE. |
| `V05029` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios com presença de rampa para cadeirante não declarada. | Definição conferida no dicionário oficial do IBGE. |
| `V05030` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face sem árvores. | Definição conferida no dicionário oficial do IBGE. |
| `V05031` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face com 1 a 2 árvores. | Definição conferida no dicionário oficial do IBGE. |
| `V05032` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face com 3 a 4 árvores. | Definição conferida no dicionário oficial do IBGE. |
| `V05033` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face com 5 ou mais árvores. | Definição conferida no dicionário oficial do IBGE. |
| `V05034` | INTEGER | INTEGER (4 dígitos observados) | 0.0 | Atributo | Domicílios com arborização não declarada (saltado). | Definição conferida no dicionário oficial do IBGE. |

## `bronze.ips_ra_2024`

- Arquivo: `bronze/ips_ra_2024.xlsx`
- Grão: Região Administrativa do Rio de Janeiro
- Registros: 32
- Descrição: Dimensões e componentes do IPS por RA na edição 2024.

| Campo | Tipo lógico | Tamanho/precisão | Nulos % | Papel | Descrição | Observações |
|---|---|---|---:|---|---|---|
| `ra_nome` | STRING | VARCHAR(23) observado | 0.0 | Chave espacial | Código romano e nome da Região Administrativa. | — |
| `ips_geral` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Índice de Progresso Social geral da RA. | — |
| `dim_necessidades` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota da dimensão Necessidades Humanas Básicas. | — |
| `nutricao` | DECIMAL | DECIMAL(11,9) observado | 0.0 | Atributo | Nota do componente Nutrição e Cuidados Médicos Básicos. | — |
| `agua_saneamento` | DECIMAL | DECIMAL(12,9) observado | 0.0 | Atributo | Nota do componente Água e Saneamento. | — |
| `moradia` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota do componente Moradia. | — |
| `seguranca` | DECIMAL | DECIMAL(11,8) observado | 0.0 | Atributo | Nota do componente Segurança Pessoal. | — |
| `dim_bem_estar` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota da dimensão Fundamentos do Bem-Estar. | — |
| `acesso_conhecimento` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota do componente Acesso ao Conhecimento Básico. | — |
| `acesso_info` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota do componente Acesso à Informação. | — |
| `saude_bem_estar` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota do componente Saúde e Bem-Estar. | — |
| `meio_ambiente` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota do componente Qualidade do Meio Ambiente. | — |
| `dim_oportunidades` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota da dimensão Oportunidades. | — |
| `direitos` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota do componente Direitos Individuais. | — |
| `liberdade` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota do componente Liberdades Individuais. | — |
| `inclusao` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota do componente Tolerância e Inclusão. | — |
| `ensino_superior` | DECIMAL | DECIMAL(11,9) observado | 0.0 | Atributo | Nota do componente Acesso à Educação Superior. | — |

## `silver.monitorar_horario_rj_2024`

- Arquivo: `silver/monitorar_horario_rj_2024.csv`
- Grão: Estação de monitoramento × hora
- Registros: 70272
- Descrição: Medições horárias de 2024 disponibilizadas na camada Silver do projeto.

| Campo | Tipo lógico | Tamanho/precisão | Nulos % | Papel | Descrição | Observações |
|---|---|---|---:|---|---|---|
| `objectid` | INTEGER | INTEGER (7 dígitos observados) | 0.0 | Chave primária | Identificador único do registro no serviço ArcGIS. | — |
| `data` | DATETIME | DATETIME (precisão até segundos) | 0.0 | Chave temporal composta | Data e hora local da medição (GMT-3 em todo o recorte de 2024). | — |
| `codnum` | INTEGER | INTEGER (1 dígitos observados) | 0.0 | Chave de referência | Código numérico da estação de monitoramento. | — |
| `estação` | STRING | VARCHAR(2) observado | 0.0 | Chave espacial composta | Sigla oficial da estação MonitorAr: AV, BG, CA, CG, IR, PG, SC ou SP. | A configuração Gold atual inverte CA e AV; não usar o nome de região sem revisar esse mapeamento. |
| `chuva` | DECIMAL | DECIMAL(19,16) observado | 22.6178 | Atributo | Precipitação pluviométrica acumulada na hora. | — |
| `pres` | DECIMAL | DECIMAL(6,2) observado | 24.5076 | Atributo | Pressão atmosférica local. | — |
| `rs` | DECIMAL | DECIMAL(20,16) observado | 47.9764 | Atributo | Radiação solar global incidente. | — |
| `temp` | DECIMAL | DECIMAL(4,2) observado | 20.4349 | Atributo | Temperatura do ar na estação. | — |
| `ur` | DECIMAL | DECIMAL(5,2) observado | 20.331 | Atributo | Umidade relativa do ar. | — |
| `dir_vento` | DECIMAL | DECIMAL(5,2) observado | 23.2582 | Atributo | Direção predominante do vento. | — |
| `vel_vento` | DECIMAL | DECIMAL(17,16) observado | 23.2283 | Atributo | Velocidade do vento. | — |
| `so2` | DECIMAL | DECIMAL(18,16) observado | 95.0692 | Atributo | Concentração horária de dióxido de enxofre (SO₂). | — |
| `no2` | DECIMAL | DECIMAL(19,16) observado | 57.8609 | Atributo | Concentração horária de dióxido de nitrogênio (NO₂). | — |
| `hcnm` | DECIMAL | DECIMAL(17,16) observado | 88.9245 | Atributo | Concentração horária de hidrocarbonetos não metano (HCNM). | — |
| `hct` | DECIMAL | DECIMAL(17,16) observado | 88.9302 | Atributo | Concentração horária de hidrocarbonetos totais (HCT). | — |
| `ch4` | DECIMAL | DECIMAL(17,16) observado | 88.9245 | Atributo | Concentração horária de metano (CH₄). | — |
| `co` | DECIMAL | DECIMAL(17,16) observado | 76.8087 | Atributo | Concentração horária de monóxido de carbono (CO). | — |
| `no` | DECIMAL | DECIMAL(19,16) observado | 57.8338 | Atributo | Concentração horária de monóxido de nitrogênio (NO). | — |
| `nox` | DECIMAL | DECIMAL(19,16) observado | 57.8267 | Atributo | Concentração horária de óxidos de nitrogênio (NO + NO₂). | — |
| `o3` | DECIMAL | DECIMAL(19,16) observado | 18.8368 | Atributo | Concentração horária de ozônio troposférico (O₃). | — |
| `pm10` | INTEGER | INTEGER (3 dígitos observados) | 25.508 | Atributo | Concentração horária de material particulado inalável PM₁₀. | — |
| `pm2_5` | INTEGER | INTEGER (3 dígitos observados) | 88.1432 | Atributo | Concentração horária de material particulado fino PM₂,₅. | — |
| `lat` | DECIMAL | DECIMAL(17,15) observado | 0.0 | Atributo | Latitude da estação no sistema WGS 84. | — |
| `lon` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Longitude da estação no sistema WGS 84. | — |
| `x_utm_sirgas2000` | DECIMAL | DECIMAL(10,4) observado | 0.0 | Atributo | Coordenada leste UTM da estação, SIRGAS 2000 / zona 23S. | — |
| `y_utm_sirgas2000` | DECIMAL | DECIMAL(11,4) observado | 0.0 | Atributo | Coordenada norte UTM da estação, SIRGAS 2000 / zona 23S. | — |

## `silver.ibge_entorno_bairro_rj`

- Arquivo: `silver/ibge_entorno_bairro_rj.csv`
- Grão: Bairro do município do Rio de Janeiro
- Registros: 162
- Descrição: Agregados por bairro filtrados para o Rio; proxy estrutural de 2022.

| Campo | Tipo lógico | Tamanho/precisão | Nulos % | Papel | Descrição | Observações |
|---|---|---|---:|---|---|---|
| `CD_BAIRRO` | STRING | VARCHAR(10) observado | 0.0 | Chave primária | Código oficial do bairro no Censo Demográfico 2022. | — |
| `NM_BAIRRO` | STRING | VARCHAR(30) observado | 0.0 | Chave de referência | Nome oficial do bairro no Censo Demográfico 2022. | — |
| `V05000` | INTEGER | INTEGER (6 dígitos observados) | 0.0 | Atributo | Total de domicílios particulares permanentes ocupados em setor selecionado para o levantamento do entorno. | Definição conferida no dicionário oficial do IBGE. |
| `V05001` | INTEGER | INTEGER (6 dígitos observados) | 0.0 | Atributo | Domicílios em face com circulação de caminhão ou ônibus. | Definição conferida no dicionário oficial do IBGE. |
| `V05002` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face com circulação de carro de passeio ou van. | Definição conferida no dicionário oficial do IBGE. |
| `V05003` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face com circulação de pedestres, bicicletas ou motocicletas. | Definição conferida no dicionário oficial do IBGE. |
| `V05004` | INTEGER | INTEGER (2 dígitos observados) | 0.0 | Atributo | Domicílios em face com circulação por aquavia. | Definição conferida no dicionário oficial do IBGE. |
| `V05005` | INTEGER | INTEGER (4 dígitos observados) | 0.0 | Atributo | Domicílios sem declaração válida para o tipo de circulação da via (saltado). | Definição conferida no dicionário oficial do IBGE. |
| `V05006` | INTEGER | INTEGER (6 dígitos observados) | 0.0 | Atributo | Domicílios em face com via pavimentada. | Definição conferida no dicionário oficial do IBGE. |
| `V05007` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face sem via pavimentada. | Definição conferida no dicionário oficial do IBGE. |
| `V05008` | INTEGER | INTEGER (4 dígitos observados) | 0.0 | Atributo | Domicílios com pavimentação da via não declarada. | Definição conferida no dicionário oficial do IBGE. |
| `V05009` | INTEGER | INTEGER (6 dígitos observados) | 0.0 | Atributo | Domicílios em face com bueiro ou boca de lobo. | Definição conferida no dicionário oficial do IBGE. |
| `V05010` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face sem bueiro ou boca de lobo. | Definição conferida no dicionário oficial do IBGE. |
| `V05011` | INTEGER | INTEGER (4 dígitos observados) | 0.0 | Atributo | Domicílios com presença de bueiro não declarada. | Definição conferida no dicionário oficial do IBGE. |
| `V05012` | INTEGER | INTEGER (6 dígitos observados) | 0.0 | Atributo | Domicílios em face com iluminação pública. | Definição conferida no dicionário oficial do IBGE. |
| `V05013` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face sem iluminação pública. | Definição conferida no dicionário oficial do IBGE. |
| `V05014` | INTEGER | INTEGER (4 dígitos observados) | 0.0 | Atributo | Domicílios com iluminação pública não declarada. | Definição conferida no dicionário oficial do IBGE. |
| `V05015` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face com ponto de ônibus. | Definição conferida no dicionário oficial do IBGE. |
| `V05016` | INTEGER | INTEGER (6 dígitos observados) | 0.0 | Atributo | Domicílios em face sem ponto de ônibus. | Definição conferida no dicionário oficial do IBGE. |
| `V05017` | INTEGER | INTEGER (4 dígitos observados) | 0.0 | Atributo | Domicílios com presença de ponto de ônibus não declarada. | Definição conferida no dicionário oficial do IBGE. |
| `V05018` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face com via sinalizada para bicicleta. | Definição conferida no dicionário oficial do IBGE. |
| `V05019` | INTEGER | INTEGER (6 dígitos observados) | 0.0 | Atributo | Domicílios em face sem via sinalizada para bicicleta. | Definição conferida no dicionário oficial do IBGE. |
| `V05020` | INTEGER | INTEGER (4 dígitos observados) | 0.0 | Atributo | Domicílios com sinalização cicloviária não declarada. | Definição conferida no dicionário oficial do IBGE. |
| `V05021` | INTEGER | INTEGER (6 dígitos observados) | 0.0 | Atributo | Domicílios em face com calçada. | Definição conferida no dicionário oficial do IBGE. |
| `V05022` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face sem calçada. | Definição conferida no dicionário oficial do IBGE. |
| `V05023` | INTEGER | INTEGER (4 dígitos observados) | 0.0 | Atributo | Domicílios com presença de calçada não declarada. | Definição conferida no dicionário oficial do IBGE. |
| `V05024` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face com obstáculo na calçada. | Definição conferida no dicionário oficial do IBGE. |
| `V05025` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face sem obstáculo na calçada. | Definição conferida no dicionário oficial do IBGE. |
| `V05026` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios com obstáculo na calçada não declarado. | Definição conferida no dicionário oficial do IBGE. |
| `V05027` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face com rampa para cadeirante. | Definição conferida no dicionário oficial do IBGE. Atenção: o ETL atual usa este campo como arborização, mas ele mede rampa para cadeirante. |
| `V05028` | INTEGER | INTEGER (6 dígitos observados) | 0.0 | Atributo | Domicílios em face sem rampa para cadeirante. | Definição conferida no dicionário oficial do IBGE. |
| `V05029` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios com presença de rampa para cadeirante não declarada. | Definição conferida no dicionário oficial do IBGE. |
| `V05030` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face sem árvores. | Definição conferida no dicionário oficial do IBGE. |
| `V05031` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face com 1 a 2 árvores. | Definição conferida no dicionário oficial do IBGE. |
| `V05032` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face com 3 a 4 árvores. | Definição conferida no dicionário oficial do IBGE. |
| `V05033` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Domicílios em face com 5 ou mais árvores. | Definição conferida no dicionário oficial do IBGE. |
| `V05034` | INTEGER | INTEGER (4 dígitos observados) | 0.0 | Atributo | Domicílios com arborização não declarada (saltado). | Definição conferida no dicionário oficial do IBGE. |

## `silver.ips_ra_rj_2024`

- Arquivo: `silver/ips_ra_rj_2024.xlsx`
- Grão: Região Administrativa do Rio de Janeiro
- Registros: 32
- Descrição: Dimensões e componentes do IPS por RA na edição 2024.

| Campo | Tipo lógico | Tamanho/precisão | Nulos % | Papel | Descrição | Observações |
|---|---|---|---:|---|---|---|
| `ra_nome` | STRING | VARCHAR(23) observado | 0.0 | Chave espacial | Código romano e nome da Região Administrativa. | — |
| `ips_geral` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Índice de Progresso Social geral da RA. | — |
| `dim_necessidades` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota da dimensão Necessidades Humanas Básicas. | — |
| `nutricao` | DECIMAL | DECIMAL(11,9) observado | 0.0 | Atributo | Nota do componente Nutrição e Cuidados Médicos Básicos. | — |
| `agua_saneamento` | DECIMAL | DECIMAL(12,9) observado | 0.0 | Atributo | Nota do componente Água e Saneamento. | — |
| `moradia` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota do componente Moradia. | — |
| `seguranca` | DECIMAL | DECIMAL(11,8) observado | 0.0 | Atributo | Nota do componente Segurança Pessoal. | — |
| `dim_bem_estar` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota da dimensão Fundamentos do Bem-Estar. | — |
| `acesso_conhecimento` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota do componente Acesso ao Conhecimento Básico. | — |
| `acesso_info` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota do componente Acesso à Informação. | — |
| `saude_bem_estar` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota do componente Saúde e Bem-Estar. | — |
| `meio_ambiente` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota do componente Qualidade do Meio Ambiente. | — |
| `dim_oportunidades` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota da dimensão Oportunidades. | — |
| `direitos` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota do componente Direitos Individuais. | — |
| `liberdade` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota do componente Liberdades Individuais. | — |
| `inclusao` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Nota do componente Tolerância e Inclusão. | — |
| `ensino_superior` | DECIMAL | DECIMAL(11,9) observado | 0.0 | Atributo | Nota do componente Acesso à Educação Superior. | — |

## `gold.massa_dados`

- Arquivo: `gold/massa_dados.csv`
- Grão: Região Administrativa/estação × dia de 2024
- Registros: 2928
- Descrição: Massa diária integrada para análises socioambientais.

| Campo | Tipo lógico | Tamanho/precisão | Nulos % | Papel | Descrição | Observações |
|---|---|---|---:|---|---|---|
| `data` | DATE | DATE (AAAA-MM-DD) | 0.0 | Chave temporal composta | Data civil da observação diária. | — |
| `mes` | INTEGER | INTEGER (2 dígitos observados) | 0.0 | Atributo | Número do mês da observação. | — |
| `dia_ano` | INTEGER | INTEGER (3 dígitos observados) | 0.0 | Atributo | Dia sequencial do ano bissexto de 2024 (1–366). | — |
| `regiao` | STRING | VARCHAR(18) observado | 0.0 | Chave espacial composta | Nome amigável da região atribuído à estação pelo ETL. | O ETL atual inverte Centro/Copacabana para os códigos CA/AV; revisar antes da análise. |
| `ra_codigo` | STRING | VARCHAR(5) observado | 0.0 | Chave espacial composta | Código romano da Região Administrativa atribuído pelo ETL. | Revisar as RAs associadas a CA/AV antes da análise. |
| `ra_nome` | STRING | VARCHAR(20) observado | 0.0 | Chave de referência | Código e nome oficial da Região Administrativa atribuído pelo ETL. | Revisar as RAs associadas a CA/AV antes da análise. |
| `lat` | DECIMAL | DECIMAL(6,4) observado | 0.0 | Atributo | Latitude de referência configurada para a região/estação. | — |
| `lon` | DECIMAL | DECIMAL(6,4) observado | 0.0 | Atributo | Longitude de referência configurada para a região/estação. | — |
| `pm10_media` | DECIMAL | DECIMAL(18,16) observado | 0.0 | Atributo | Média diária de PM₁₀ após regras de validade e imputação. | — |
| `pm10_max` | INTEGER | INTEGER (3 dígitos observados) | 23.1557 | Atributo | Máximo horário de PM₁₀ observado no dia. | — |
| `pm2_5_media` | DECIMAL | DECIMAL(4,2) observado | 87.8757 | Atributo | Média diária de PM₂,₅; disponível principalmente para Irajá. | — |
| `o3_media` | DECIMAL | DECIMAL(18,15) observado | 0.0 | Atributo | Média diária de ozônio troposférico. | — |
| `o3_max` | DECIMAL | DECIMAL(5,2) observado | 15.847 | Atributo | Máximo horário de ozônio troposférico observado no dia. | — |
| `no2_media` | DECIMAL | DECIMAL(5,2) observado | 56.9672 | Atributo | Média diária de dióxido de nitrogênio. | — |
| `co_media` | DECIMAL | DECIMAL(3,2) observado | 76.4344 | Atributo | Média diária de monóxido de carbono. | — |
| `so2_media` | DECIMAL | DECIMAL(4,2) observado | 94.9795 | Atributo | Média diária de dióxido de enxofre. | — |
| `temp_media` | DECIMAL | DECIMAL(17,15) observado | 0.0 | Atributo | Temperatura média diária. | — |
| `temp_max` | DECIMAL | DECIMAL(4,2) observado | 19.4672 | Atributo | Temperatura máxima horária do dia. | — |
| `temp_min` | DECIMAL | DECIMAL(4,2) observado | 19.4672 | Atributo | Temperatura mínima horária do dia. | — |
| `ur_media` | DECIMAL | DECIMAL(17,15) observado | 0.0 | Atributo | Umidade relativa média diária. | — |
| `ur_min` | DECIMAL | DECIMAL(4,2) observado | 19.3306 | Atributo | Umidade relativa mínima horária do dia. | — |
| `chuva_dia` | DECIMAL | DECIMAL(6,2) observado | 0.0 | Atributo | Precipitação total acumulada no dia. | — |
| `derivada_pm10` | DECIMAL | DECIMAL(4,2) observado | 0.0 | Atributo | Taxa diária de variação de PM₁₀ por diferenças finitas. | — |
| `derivada_temp` | DECIMAL | DECIMAL(3,2) observado | 0.0 | Atributo | Taxa diária de variação da temperatura por diferenças finitas. | — |
| `integral_acumulada_pm10` | DECIMAL | DECIMAL(7,2) observado | 0.0 | Atributo | Exposição acumulada de PM₁₀ pela regra dos trapézios. | — |
| `integral_acumulada_pm2_5` | DECIMAL | DECIMAL(6,2) observado | 87.5 | Atributo | Exposição acumulada de PM₂,₅ pela regra dos trapézios; preenchida para Irajá. | — |
| `ips_2024` | DECIMAL | DECIMAL(4,2) observado | 0.0 | Atributo | Índice de Progresso Social geral da RA na edição 2024. | — |
| `ips_dim_necessidades` | DECIMAL | DECIMAL(4,2) observado | 0.0 | Atributo | Nota da dimensão Necessidades Humanas Básicas. | — |
| `ips_dim_bem_estar` | DECIMAL | DECIMAL(4,2) observado | 0.0 | Atributo | Nota da dimensão Fundamentos do Bem-Estar. | — |
| `ips_dim_oportunidades` | DECIMAL | DECIMAL(4,2) observado | 0.0 | Atributo | Nota da dimensão Oportunidades. | — |
| `ips_comp_meio_ambiente` | DECIMAL | DECIMAL(4,2) observado | 0.0 | Atributo | Nota do componente Qualidade do Meio Ambiente. | — |
| `ips_dim_moradia` | DECIMAL | DECIMAL(4,2) observado | 0.0 | Atributo | Nota do componente Moradia. | — |
| `pct_arborizacao_2022` | DECIMAL | DECIMAL(4,2) observado | 0.0 | Atributo | Percentual rotulado como arborização no Gold, calculado atualmente como V05027/V05000 × 100. | Inconsistência crítica: V05027 mede rampa para cadeirante. Arborização oficial está em V05030–V05034; este indicador precisa ser recalculado. |
| `qtd_domicilios_arborizados` | INTEGER | INTEGER (5 dígitos observados) | 0.0 | Atributo | Quantidade rotulada como domicílios arborizados, atualmente copiada de V05027. | Inconsistência crítica: V05027 mede rampa para cadeirante; não representa domicílios arborizados. |
| `total_domicilios` | INTEGER | INTEGER (6 dígitos observados) | 0.0 | Atributo | Total de domicílios particulares permanentes ocupados nos bairros agregados da RA. | — |
| `isa` | DECIMAL | DECIMAL(4,2) observado | 0.0 | Atributo | Índice de Saúde Arbórea sintético, calculado somente com estressores ambientais de 2024. | — |
| `isa_classe` | STRING | VARCHAR(7) observado | 0.0 | Atributo | Classe do ISA: Boa, Regular ou Ruim. | — |
| `flag_missing_pm10` | BOOLEAN | BOOLEAN (1 bit lógico) | 0.0 | Atributo | Indica média diária de PM₁₀ ausente antes da imputação. | — |
| `flag_outlier_pm10` | BOOLEAN | BOOLEAN (1 bit lógico) | 0.0 | Atributo | Indica máximo horário de PM₁₀ acima do limite IQR da estação. | — |
| `flag_imputado` | BOOLEAN | BOOLEAN (1 bit lógico) | 0.0 | Atributo | Indica que ao menos uma variável diária principal foi imputada. | — |

## `gold.massa_horaria_rj_2024`

- Arquivo: `gold/massa_horaria_rj_2024.parquet`
- Grão: Estação de monitoramento × hora
- Registros: 70272
- Descrição: Massa horária validada e armazenada em formato colunar.

| Campo | Tipo lógico | Tamanho/precisão | Nulos % | Papel | Descrição | Observações |
|---|---|---|---:|---|---|---|
| `objectid` | INTEGER | INTEGER (7 dígitos observados) | 0.0 | Chave primária | Identificador único do registro no serviço ArcGIS. | — |
| `data` | DATETIME | DATETIME (precisão até segundos) | 0.0 | Chave temporal composta | Data e hora local da medição (GMT-3 em todo o recorte de 2024). | — |
| `codnum` | INTEGER | INTEGER (1 dígitos observados) | 0.0 | Chave de referência | Código numérico da estação de monitoramento. | — |
| `estação` | STRING | VARCHAR(2) observado | 0.0 | Chave espacial composta | Sigla oficial da estação MonitorAr: AV, BG, CA, CG, IR, PG, SC ou SP. | A configuração Gold atual inverte CA e AV; não usar o nome de região sem revisar esse mapeamento. |
| `chuva` | DECIMAL | DECIMAL(19,16) observado | 22.6178 | Atributo | Precipitação pluviométrica acumulada na hora. | — |
| `pres` | DECIMAL | DECIMAL(6,2) observado | 24.5076 | Atributo | Pressão atmosférica local. | — |
| `rs` | DECIMAL | DECIMAL(20,16) observado | 47.9764 | Atributo | Radiação solar global incidente. | — |
| `temp` | DECIMAL | DECIMAL(4,2) observado | 20.4349 | Atributo | Temperatura do ar na estação. | — |
| `ur` | DECIMAL | DECIMAL(5,2) observado | 20.331 | Atributo | Umidade relativa do ar. | — |
| `dir_vento` | DECIMAL | DECIMAL(5,2) observado | 23.2582 | Atributo | Direção predominante do vento. | — |
| `vel_vento` | DECIMAL | DECIMAL(17,16) observado | 23.2283 | Atributo | Velocidade do vento. | — |
| `so2` | DECIMAL | DECIMAL(18,16) observado | 95.0692 | Atributo | Concentração horária de dióxido de enxofre (SO₂). | — |
| `no2` | DECIMAL | DECIMAL(19,16) observado | 57.8609 | Atributo | Concentração horária de dióxido de nitrogênio (NO₂). | — |
| `hcnm` | DECIMAL | DECIMAL(17,16) observado | 88.9245 | Atributo | Concentração horária de hidrocarbonetos não metano (HCNM). | — |
| `hct` | DECIMAL | DECIMAL(17,16) observado | 88.9302 | Atributo | Concentração horária de hidrocarbonetos totais (HCT). | — |
| `ch4` | DECIMAL | DECIMAL(17,16) observado | 88.9245 | Atributo | Concentração horária de metano (CH₄). | — |
| `co` | DECIMAL | DECIMAL(17,16) observado | 76.8087 | Atributo | Concentração horária de monóxido de carbono (CO). | — |
| `no` | DECIMAL | DECIMAL(19,16) observado | 57.8338 | Atributo | Concentração horária de monóxido de nitrogênio (NO). | — |
| `nox` | DECIMAL | DECIMAL(19,16) observado | 57.8267 | Atributo | Concentração horária de óxidos de nitrogênio (NO + NO₂). | — |
| `o3` | DECIMAL | DECIMAL(19,16) observado | 18.8368 | Atributo | Concentração horária de ozônio troposférico (O₃). | — |
| `pm10` | INTEGER | INTEGER (3 dígitos observados) | 25.508 | Atributo | Concentração horária de material particulado inalável PM₁₀. | — |
| `pm2_5` | INTEGER | INTEGER (3 dígitos observados) | 88.1432 | Atributo | Concentração horária de material particulado fino PM₂,₅. | — |
| `lat` | DECIMAL | DECIMAL(17,15) observado | 0.0 | Atributo | Latitude da estação no sistema WGS 84. | — |
| `lon` | DECIMAL | DECIMAL(10,8) observado | 0.0 | Atributo | Longitude da estação no sistema WGS 84. | — |
| `x_utm_sirgas2000` | DECIMAL | DECIMAL(10,4) observado | 0.0 | Atributo | Coordenada leste UTM da estação, SIRGAS 2000 / zona 23S. | — |
| `y_utm_sirgas2000` | DECIMAL | DECIMAL(11,4) observado | 0.0 | Atributo | Coordenada norte UTM da estação, SIRGAS 2000 / zona 23S. | — |
