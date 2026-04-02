# Desafio Prompt Engineer

## Visão Geral

Este repositório contém a implementação do desafio de pull, otimização, push e avaliação de prompts para conversão de bugs em user stories usando LangChain e LangSmith.

## A) Técnicas Aplicadas (Fase 2)

O prompt otimizado [`prompts/bug_to_user_story_v2.yml`](prompts/bug_to_user_story_v2.yml) aplica 4 técnicas avançadas de prompt engineering para melhorar tom, consistência estrutural e completude das user stories geradas a partir de bugs.

### 1. Role Prompting

Foi definida uma persona explícita de Product Manager sênior para ancorar o modelo no vocabulário e no nível de detalhe esperados para o domínio.

Justificativa:

- O prompt v1 usava uma persona genérica de "assistente"
- A persona de Product Manager melhora o foco em valor de negócio e clareza
- Essa técnica ajuda principalmente na consistência do tom e na qualidade da user story

Exemplo prático:

```text
Você é um Product Manager sênior especializado em transformar relatos de bugs em User Stories claras e acionáveis.
```

### 2. Few-shot Learning

O prompt inclui 4 exemplos completos extraídos do dataset, cobrindo bugs simples, de integração, performance e concorrência.

Justificativa:

- O prompt v1 não tinha exemplos
- Os exemplos ensinam o formato esperado de saída
- Eles mostram como variar quantidade de critérios e quando incluir contexto técnico

Exemplo prático:

```text
Bug:
"Campo de email aceita texto sem @, permitindo cadastros inválidos."

User Story:
Como um usuário criando uma conta, eu quero que o sistema valide meu email corretamente, para que eu não insira um endereço inválido por engano.
```

### 3. Chain of Thought (CoT)

Foi criado um processo de raciocínio estruturado com tags XML para forçar análise intermediária antes da resposta final.

Justificativa:

- Bugs mais complexos exigem extração cuidadosa de logs, métricas, steps e integrações
- O raciocínio em etapas reduz omissões
- Essa técnica foi decisiva para elevar a métrica de completude

Exemplo prático:

```xml
<analise>
1. Tipo de bug
2. Persona afetada
3. Problema central
4. Complexidade
5. Detalhes técnicos encontrados
</analise>
```

### 4. Structured Output

O prompt obriga uma saída com seções fixas, padrão de user story e critérios em Given-When-Then.

Justificativa:

- As métricas avaliam formato e consistência estrutural
- Sem formato rígido, o modelo tende a variar a resposta
- Essa técnica melhora diretamente User Story Format e Acceptance Criteria

Exemplo prático:

```text
**User Story:**
Como um [persona específica], eu quero [ação clara], para que [benefício tangível].

**Critérios de Aceitação:**
- Dado que [contexto inicial]
- Quando [ação]
- Então [resultado mensurável]
```

### Resumo das escolhas

As técnicas foram escolhidas porque atacam problemas diferentes do prompt base:

- `Role Prompting` melhora contexto, tom e foco de produto
- `Few-shot Learning` ensina o padrão esperado com exemplos concretos
- `Chain of Thought` melhora análise e completude em bugs complexos
- `Structured Output` garante consistência de formato e testabilidade

O material detalhado dessa análise está em [`TECNICAS.md`](TECNICAS.md).

## B) Resultados Finais

### Link público do dashboard do LangSmith

- Projeto de avaliação: `https://smith.langchain.com/o/ab74ea20-0cd6-49fc-95ee-5b3950b759a7/projects/p/17d5dda4-4547-4618-bf5f-7326d557be8d`

### Comparativo v1 vs v2

| Métrica | v1 (baseline) | v2 (otimizado) | Diferença |
|---|---:|---:|---:|
| Tone Score | 0.99 | 0.99 | 0.00 |
| Acceptance Criteria Score | 0.88 | 0.96 | +0.08 |
| User Story Format Score | 0.89 | 0.99 | +0.10 |
| Completeness Score | 0.73 | 0.98 | +0.25 |
| **Média Geral** | **0.8711** | **0.9819** | **+0.1108** |

### Leitura dos resultados

O prompt v2 superou o critério mínimo de 0.9 de média geral e apresentou a maior evolução em `Completeness Score`, o que indica melhora relevante na captura de detalhes técnicos, edge cases e contexto do bug.

Também houve ganho claro em `User Story Format Score` e `Acceptance Criteria Score`, refletindo o efeito do formato rígido de saída, do uso de few-shot examples e do raciocínio estruturado antes da resposta final.

### Screenshots das avaliações

Nesta versão do repositório, as evidências estão documentadas por links públicos do LangSmith. As screenshots não foram anexadas.

## C) Como Executar

### Pré-requisitos

- Python 3.9+
- Ambiente virtual Python
- Conta no LangSmith
- Credenciais configuradas no arquivo `.env`
- Chave de API de um provider de LLM suportado:
  - OpenAI
  - Google Gemini

### Instalação

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuração do ambiente

Crie o arquivo `.env` a partir do template:

```bash
cp .env.example .env
```

Preencha as variáveis obrigatórias:

- `LANGSMITH_API_KEY`
- `LANGSMITH_PROJECT`
- `USERNAME_LANGSMITH_HUB`
- `LLM_PROVIDER`
- `LLM_MODEL`
- `EVAL_MODEL`
- `OPENAI_API_KEY` ou `GOOGLE_API_KEY`, conforme o provider escolhido

Exemplo com Gemini:

```env
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=desafio-prompt-engineer
USERNAME_LANGSMITH_HUB=casaccia

GOOGLE_API_KEY=...
LLM_PROVIDER=google
LLM_MODEL=gemini-2.5-flash
EVAL_MODEL=gemini-2.5-flash
```

Exemplo com OpenAI:

```env
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=desafio-prompt-engineer
USERNAME_LANGSMITH_HUB=casaccia

OPENAI_API_KEY=...
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
EVAL_MODEL=gpt-4o
```

### Fase 1. Fazer pull do prompt base

```bash
python src/pull_prompts.py
```

Esse comando baixa o prompt baseline `leonanluppi/bug_to_user_story_v1` do LangSmith Hub e salva localmente em [`prompts/bug_to_user_story_v1.yml`](prompts/bug_to_user_story_v1.yml).

### Fase 2. Editar o prompt otimizado

Edite o arquivo [`prompts/bug_to_user_story_v2.yml`](prompts/bug_to_user_story_v2.yml) com a versão otimizada do prompt, mantendo:

- chave YAML `bug_to_user_story_v2`
- `system_prompt`
- `user_prompt`
- `version`
- `techniques_applied`

### Fase 3. Validar a estrutura do prompt

```bash
pytest tests/test_prompts.py -v
```

Os testes verificam:

- existência e conteúdo do `system_prompt`
- presença de persona
- formato de user story
- exemplos few-shot
- ausência de TODOs
- mínimo de técnicas declaradas

### Fase 4. Publicar o prompt no LangSmith Hub

```bash
python src/push_prompts.py
```

Esse comando:

- lê [`prompts/bug_to_user_story_v2.yml`](prompts/bug_to_user_story_v2.yml)
- monta o `ChatPromptTemplate`
- publica o prompt como público no LangSmith Hub

Prompt publicado neste projeto:

- `https://smith.langchain.com/prompts/casaccia/bug_to_user_story_v2`

### Fase 5. Executar a avaliação

```bash
python src/evaluate.py
```

Esse script:

- cria ou atualiza o dataset de avaliação no LangSmith
- usa [`datasets/bug_to_user_story.jsonl`](datasets/bug_to_user_story.jsonl)
- puxa o prompt publicado no Hub
- executa as métricas automáticas
- publica os resultados no projeto do LangSmith

Projeto usado na avaliação:

- `https://smith.langchain.com/o/ab74ea20-0cd6-49fc-95ee-5b3950b759a7/projects/p/17d5dda4-4547-4618-bf5f-7326d557be8d`

### Fase 6. Iterar até atingir a meta

Repita o ciclo abaixo até atingir a nota mínima:

```bash
pytest tests/test_prompts.py -v
python src/push_prompts.py
python src/evaluate.py
```

Critério de aprovação:

- `Tone Score >= 0.9`
- `Acceptance Criteria Score >= 0.9`
- `User Story Format Score >= 0.9`
- `Completeness Score >= 0.9`
- média geral `>= 0.9`

## D) Evidências no LangSmith

### Link do dashboard e do prompt publicado

- Prompt otimizado publicado: `https://smith.langchain.com/prompts/casaccia/bug_to_user_story_v2`
- Dashboard do projeto de avaliação: `https://smith.langchain.com/o/ab74ea20-0cd6-49fc-95ee-5b3950b759a7/projects/p/17d5dda4-4547-4618-bf5f-7326d557be8d`

### Dataset de avaliação

- Dataset utilizado: `desafio-prompt-engineer-eval`
- Quantidade de exemplos: `20`

### Execuções dos prompts

- Prompt baseline `v1` de origem: `https://smith.langchain.com/hub/leonanluppi/bug_to_user_story_v1?organizationId=ab74ea20-0cd6-49fc-95ee-5b3950b759a7`
- Prompt `v2` otimizado publicado e usado na avaliação: `casaccia/bug_to_user_story_v2`
- Resultado agregado documentado neste repositório:
  - média `v1`: `0.8711`
  - média `v2`: `0.9819`

Observação:

- Há trace no projeto comprovando execução do baseline `leonanluppi/bug_to_user_story_v1`:
  - `https://smith.langchain.com/o/ab74ea20-0cd6-49fc-95ee-5b3950b759a7/projects/p/17d5dda4-4547-4618-bf5f-7326d557be8d/r/f82bd32f-e750-49cb-b935-5200453ec128?trace_id=2727da00-29a3-4866-a3d2-870740f3a6ee&start_time=2026-04-02T15:05:57.351898`
- As execuções detalhadas do `v2` estão refletidas no dashboard e nos traces abaixo
- As notas comparativas de `v1` e `v2` estão consolidadas na seção `B) Resultados Finais`

### Tracing detalhado

Os traces abaixo foram confirmados no projeto `desafio-prompt-engineer`:

- `https://smith.langchain.com/o/ab74ea20-0cd6-49fc-95ee-5b3950b759a7/projects/p/17d5dda4-4547-4618-bf5f-7326d557be8d/r/517f1667-c2f1-4eaf-acfd-6a8a35e31a15?trace_id=517f1667-c2f1-4eaf-acfd-6a8a35e31a15&start_time=2026-04-02T15:48:20.608886`
- `https://smith.langchain.com/o/ab74ea20-0cd6-49fc-95ee-5b3950b759a7/projects/p/17d5dda4-4547-4618-bf5f-7326d557be8d/r/563d46d1-2ea1-4601-936d-9c2de1cdc4c1?trace_id=563d46d1-2ea1-4601-936d-9c2de1cdc4c1&start_time=2026-04-02T15:48:14.560848`
- `https://smith.langchain.com/o/ab74ea20-0cd6-49fc-95ee-5b3950b759a7/projects/p/17d5dda4-4547-4618-bf5f-7326d557be8d/r/31106a88-c811-4570-b814-33be34d25289?trace_id=31106a88-c811-4570-b814-33be34d25289&start_time=2026-04-02T15:48:05.250839`
