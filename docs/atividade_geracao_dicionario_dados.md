# Atividade — Geração Automatizada do Dicionário de Dados

**Projeto:** Data Flora  
**Data da execução:** 12/09/2026  
**Script:** `scripts/06_generate_data_dictionary.py`  
**Resultado:** `APROVADO_COM_RESSALVAS_CRITICAS`

## Objetivo

Criar um catálogo técnico e semântico reproduzível para facilitar a localização, a consulta e o cruzamento dos dados do projeto. O dicionário registra o significado e o comportamento observado de cada campo, preservando a distinção entre dados reais de 2024, dados proxy do Censo 2022, métricas derivadas e flags de qualidade.

O catálogo também serve como controle de integridade: diferenças entre o significado oficial de um campo e o uso feito pelo pipeline são registradas explicitamente, em vez de serem propagadas como documentação válida.

## Escopo catalogado

Foram perfiladas as oito tabelas atualmente disponíveis nas camadas Bronze, Silver e Gold:

| Camada | Tabela | Grão |
|---|---|---|
| Bronze | `bronze.monitorar_horario_2024` | Estação × hora |
| Bronze | `bronze.ibge_entorno_bairro_BR` | Bairro do Brasil |
| Bronze | `bronze.ips_ra_2024` | Região Administrativa |
| Silver | `silver.monitorar_horario_rj_2024` | Estação × hora |
| Silver | `silver.ibge_entorno_bairro_rj` | Bairro do Rio de Janeiro |
| Silver | `silver.ips_ra_rj_2024` | Região Administrativa |
| Gold | `gold.massa_dados` | Região/estação × dia |
| Gold | `gold.massa_horaria_rj_2024` | Estação × hora |

A planilha do IPS contém diversas edições históricas. Em conformidade com o escopo fechado do projeto, somente a tabela lógica da aba `Dimensões e Componentes 2024`, efetivamente consumida pelo ETL atual, foi catalogada.

## Informações registradas por campo

Além dos itens mínimos solicitados — tabela, campo, tipo, descrição e tamanho/precisão — o script registra:

- arquivo de origem e granularidade da tabela;
- tipo físico observado e tipo lógico recomendado;
- unidade de medida e natureza do dado;
- papel de chave e orientação para cruzamentos;
- total de registros e quantidade efetivamente analisada;
- quantidade e percentual de nulos;
- cardinalidade e unicidade observada;
- valores mínimo e máximo;
- domínio para campos de baixa cardinalidade;
- exemplos de valores;
- fonte, URL oficial e observações de integridade.

Para identificadores, o tipo lógico prevalece sobre a inferência física. Por exemplo, `CD_BAIRRO` é catalogado como `STRING/VARCHAR(10)`, embora o leitor do CSV consiga representá-lo como inteiro, pois operações matemáticas sobre esse código não possuem significado e poderiam comprometer zeros à esquerda em outros recortes.

## Critério de tamanho e precisão

- Texto: maior comprimento observado, no formato `VARCHAR(n)`.
- Inteiro: maior quantidade de dígitos observada.
- Decimal: precisão total e escala observadas, no formato `DECIMAL(p,s)`.
- Booleano: `BOOLEAN (1 bit lógico)`.
- Data: padrão lógico `AAAA-MM-DD`.
- Data e hora: precisão observada até segundos.

As medidas são acompanhadas da palavra “observado” porque descrevem os arquivos atuais, não necessariamente os limites máximos permitidos pelos sistemas de origem. Por padrão, o script lê todas as linhas. Para bases futuras maiores, `--sample-size` permite uma amostra determinística com seed 42.

## Mapeamento do script

| Etapa | Elemento do script | Responsabilidade |
|---|---|---|
| 1. Inventário | `TABLE_SPECS` | Define arquivos, nomes lógicos, fontes, granularidade e escopo. |
| 2. Semântica | `MONITORAR_META`, `IBGE_META`, `IPS_META`, `GOLD_META` | Mantém descrições, unidades, natureza, chaves e alertas conhecidos. |
| 3. Leitura | `read_table()` e `read_ips()` | Lê CSV, Parquet e a estrutura específica da planilha IPS 2024. |
| 4. Perfil | `profile_field()` | Calcula tipos, precisão, nulidade, cardinalidade, limites, domínios e exemplos. |
| 5. Catálogo | `generate_catalog()` | Consolida um registro por combinação tabela/campo. |
| 6. Qualidade | `validate_catalog()` | Verifica cobertura, unicidade, metadados obrigatórios, semântica e grão. |
| 7. Publicação | `write_markdown()` e `main()` | Grava os formatos CSV, Markdown e JSON de validação. |

O script interrompe com código de saída diferente de zero se qualquer validação estrutural falhar. Ressalvas semânticas preexistentes são publicadas como alertas críticos, sem impedir a geração do catálogo que as documenta.

## Arquivos produzidos

- `docs/dicionario_dados_gerado.csv`: catálogo completo e adequado para filtros, importação em Excel/Power BI ou processamento automatizado.
- `docs/dicionario_dados_gerado.md`: versão legível, organizada por tabela.
- `docs/validacao_dicionario_dados.json`: evidências estruturadas dos testes e alertas da execução.
- `docs/atividade_geracao_dicionario_dados.md`: este registro da atividade.

Os arquivos gerados complementam o documento metodológico manual `docs/dicionario_de_dados.md`; não o sobrescrevem.

## Execução realizada

Com as dependências de `requirements.txt` instaladas, a execução padrão é:

```powershell
python scripts/06_generate_data_dictionary.py
```

Para limitar o perfil a uma amostra reproduzível por tabela:

```powershell
python scripts/06_generate_data_dictionary.py --sample-size 10000
```

Nesta atividade foi usada a execução completa, sem limite de amostra.

## Resultado da validação

Foram catalogados **226 campos em 8 tabelas**, sem duplicidades de `nome_tabela + nome_campo` e sem ausência nos metadados obrigatórios.

| Verificação | Resultado | Evidência |
|---|---|---|
| Cobertura de campos | PASSOU | 226 de 226 campos catalogados |
| Unicidade tabela/campo | PASSOU | Nenhuma duplicidade |
| Metadados obrigatórios | PASSOU | Nenhuma lacuna |
| Semântica oficial IBGE | PASSOU | `V05027` e `V05030`–`V05034` conferidos |
| Integridade MonitorAr 2024 | PASSOU | 70.272 registros, 8 estações e `objectid` único |
| Recorte IBGE Rio | PASSOU | 162 bairros com prefixo municipal `3304557` |
| Grão da massa Gold | PASSOU | 2.928 linhas, 8 regiões e 366 dias por região |

## Ressalvas críticas encontradas

### 1. Campo de arborização do IBGE usado incorretamente

O dicionário oficial do IBGE define:

- `V05027`: domicílios em face com rampa para cadeirante;
- `V05030`: domicílios em face sem árvores;
- `V05031`: domicílios em face com 1 a 2 árvores;
- `V05032`: domicílios em face com 3 a 4 árvores;
- `V05033`: domicílios em face com 5 ou mais árvores;
- `V05034`: arborização não declarada/saltada.

O ETL atual usa `V05027` para preencher `qtd_domicilios_arborizados` e calcular `pct_arborizacao_2022`. Portanto, as duas colunas Gold estão rotuladas como arborização, mas atualmente representam presença de rampa para cadeirante.

Uma regra de arborização coerente com as categorias oficiais deverá considerar, após validação metodológica, `V05031 + V05032 + V05033` como numerador e excluir `V05034` do denominador declarado. Nenhuma alteração foi feita no ETL nesta atividade.

### 2. Códigos de Centro e Copacabana invertidos

A fonte oficial MonitorAr identifica:

- `CA`: Largo da Carioca / Centro;
- `AV`: Praça Cardeal Arcoverde / Copacabana.

O `ESTACOES_CONFIG` do ETL atual associa `AV` a Centro e `CA` a Copacabana. Isso pode atribuir medições, coordenadas, IPS e dados censitários à região errada. O problema foi registrado no dicionário e no relatório de validação, mas não foi corrigido por estar fora do escopo desta atividade.

## Próxima ação recomendada

Antes das análises estatísticas, corrigir de forma controlada as duas regras do ETL, regenerar Silver/Gold quando aplicável e executar novamente o gerador do dicionário. Essa sequência evita que cruzamentos territorialmente invertidos ou um indicador de acessibilidade rotulado como arborização contaminem as conclusões do projeto.

## Fontes usadas na conferência semântica

- MonitorAr-Rio / SMAC-PCRJ: `https://services1.arcgis.com/OlP4dGNtIcnD3RYf/arcgis/rest/services/Qualidade_do_ar_dados_horarios_2011_2018/FeatureServer/2`
- Dicionários oficiais do Censo 2022 — entorno dos domicílios: `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios_Caracteristicas_urbanisticas_do_entorno_dos_domicilios/dicionarios_de_dados_entorno.zip`
- IPS Rio 2024 / data.rio: `https://www.data.rio/documents/918dd39478594792a9cfa7080b84c0b5`
