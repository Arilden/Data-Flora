# CLAUDE.md

Contexto para o Claude (ou qualquer agente de IA) trabalhando neste repositório.

## Sobre o projeto

Este é um projeto de portfólio de dados: análise da relação entre arborização, saúde arbórea
(estimada) e qualidade do ar nas regiões do município do Rio de Janeiro. A pergunta central é:
regiões mais pobres têm menos árvores — e as árvores que têm estão em pior estado de saúde?
Qualidade do ar, calor, umidade e chuva entram como causas prováveis.

O recorte temporal fechado é o **ano de 2024**. O projeto combina dado real (qualidade do ar e
meteorologia do MonitorAr-Rio, Índice de Progresso Social do IPP, arborização do Censo IBGE) com
um índice derivado (Índice de Saúde Arbórea — ISA), já que não existe inventário público do
estado fitossanitário das árvores por região.

Entregáveis previstos: um Excel com a massa de dados e as etapas de análise, notebooks Python
de preparação/qualidade e análise, um dashboard no Looker Studio, e uma integração bônus com o
projeto SkyFlora (arquitetura medallion em Databricks).

## Antes de fazer qualquer coisa neste repositório

**Leia o conteúdo da pasta `docs/` primeiro.** Em especial:

- `docs/plano_arborizacao_rj.md` — o plano de desenvolvimento completo: fontes de dados exatas
  (URLs, endpoints, limites de requisição), a regra de cálculo do índice derivado (ISA), o
  mapeamento de cada método estatístico pedido para o dado real que ele usa, a estrutura da
  massa final e — principalmente — a seção **"Decisões de escopo registradas"**, que documenta
  o porquê de cada escolha (por que só 2024, por que o Censo 2022 entra como proxy, por que o
  IPS usa só a edição 2024, etc.). Não reabra essas decisões sem que a usuária peça
  explicitamente.
- `README_EXECUCAO.md` (raiz) — como rodar os scripts de extração e o que esperar como saída.

Esses dois arquivos são a fonte de verdade do escopo. Qualquer código, notebook ou análise
gerado deve ser consistente com o que está documentado neles.

## Regras importantes que vêm do plano

- O recorte é **2024**, ponto. Não expandir a janela para outros anos sem pedido explícito.
- O **Índice de Saúde Arbórea (ISA) é um dado derivado**, calculado só a partir de variáveis
  ambientais (calor, umidade, chuva, poluição) — a renda/IPS nunca entra na fórmula, para evitar
  correlação circular. Isso precisa ficar marcado como "derivado" em qualquer lugar que apareça.
- A **arborização vem do Censo 2022** (não existe Censo 2024) e entra como **proxy** — marcar
  sempre como tal, nunca apresentar como dado de 2024.
- A extração de dados roda no PC da usuária, não neste ambiente de nuvem — os domínios das
  fontes (data.rio, arcgis.com, ftp.ibge.gov.br) são bloqueados pela política de rede daqui.

## Estrutura de pastas

```
docs/                 — plano de desenvolvimento e documentação
scripts/               — scripts de extração (Python)
dados_brutos/          — dados baixados, como vieram da fonte (não editar manualmente)
requirements.txt       — dependências Python
README_EXECUCAO.md     — como rodar a extração
```
