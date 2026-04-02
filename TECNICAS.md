# Técnicas Aplicadas

O prompt otimizado (`prompts/bug_to_user_story_v2.yml`) aplica **4 técnicas avançadas de prompt engineering** 



## 1. Role Prompting

**O que é:** Atribuir ao modelo uma persona específica com expertise e vocabulário adequados ao domínio da tarefa.

**Onde foi aplicado (linha 5 do prompt v2):**

```
Você é um Product Manager sênior especializado em transformar relatos de bugs em User Stories claras e acionáveis.
```

**Por que foi escolhido:** O prompt v1 usava apenas "Você é um assistente que ajuda a transformar relatos de bugs", uma persona vaga que não ancorava o modelo em nenhum domínio. Ao definir "Product Manager sênior", o modelo adota:

- Vocabulário de produto (user stories, critérios de aceitação, personas)
- Tom profissional e empático (métrica "Tone Score")
- Foco em valor para o negócio/usuário, não apenas na descrição técnica do bug

**Exemplo prático** -- comparação v1 vs v2:

| v1 (baseline) | v2 (otimizado) |
|---|---|
| "Você é um assistente que ajuda a transformar relatos de bugs" | "Você é um Product Manager sênior especializado em transformar relatos de bugs em User Stories claras e acionáveis" |

---

## 2. Few-shot Learning

**O que é:** Incluir exemplos concretos de entrada e saída dentro do prompt, para que o modelo aprenda o formato e o nível de detalhe esperados sem necessidade de fine-tuning.

**Onde foi aplicado (linhas 63-168 do prompt v2):** 4 exemplos completos extraídos do dataset, cobrindo diferentes níveis de complexidade:

| Exemplo | Tipo | Critérios | Contexto Técnico |
|---|---|---|---|
| 1 - Email inválido | Bug simples | 5 bullets | Sem |
| 2 - Webhook de pagamento | Bug médio (integração) | 6 bullets | Com (HTTP 500, endpoint) |
| 3 - Relatório lento | Bug de performance | 5 bullets | Com (query SQL, timeout) |
| 4 - Estoque concorrente | Bug de concorrência | 6 bullets | Com (SKU, locks) |

**Por que foi escolhido:** O prompt v1 não continha nenhum exemplo, forçando o modelo a "adivinhar" o formato esperado. Os exemplos few-shot:

- Demonstram o formato exato: User Story + Critérios de Aceitação + Contexto Técnico
- Mostram como variar o número de critérios conforme a complexidade (5 para simples, 6 para médio)
- Ensinam o padrão Given-When-Then com edge cases reais

**Exemplo prático** -- trecho do Exemplo 1 (bug simples):

```
Bug:
"Campo de email aceita texto sem @, permitindo cadastros inválidos."

User Story:
Como um usuário criando uma conta, eu quero que o sistema valide meu email
corretamente, para que eu não insira um endereço inválido por engano.

Critérios de Aceitação:
- Dado que estou no formulário de cadastro
- Quando digito um email sem o caractere @
- Então devo ver uma mensagem de erro
- E não devo conseguir prosseguir com o cadastro
- E a mensagem deve explicar o formato correto
```

---

## 3. Chain of Thought (CoT)

**O que é:** Instruir o modelo a decompor o raciocínio em etapas intermediárias antes de gerar a resposta final, melhorando a qualidade e completude do output.

**Onde foi aplicado (linhas 173-281 do prompt v2):** Processo de raciocínio estruturado com **tags XML** que forçam o modelo a pensar passo a passo:

1. `<analise>` -- Classifica o bug (tipo, persona, complexidade, detalhes técnicos)
2. `<rascunho_user_story>` -- Elabora persona, ação e benefício antes de redigir
3. `<rascunho_criterios>` -- Planeja os critérios com regras condicionais (integrações, segurança, concorrência)
4. `<rascunho_contexto>` -- Decide se contexto técnico é necessário e transcreve valores exatos
5. `<checklist>` -- Valida 15 critérios de qualidade antes de gerar a resposta final

**Por que foi escolhido:** Bugs complexos (integrações, concorrência, segurança) exigem que o modelo:

- Identifique TODOS os detalhes técnicos (logs, métricas, steps to reproduce) antes de escrever
- Decida a quantidade correta de critérios baseada na complexidade
- Verifique completude antes de finalizar (reduz omissões que prejudicam a métrica "Completeness Score")

**Exemplo prático** -- trecho da tag `<analise>`:

```xml
<analise>
1. **Tipo de bug**: [UI/validação/performance/integração/segurança]
2. **Persona afetada**: [cliente/usuário/administrador/gerente/analista]
3. **Problema central**: [em 1 frase]
4. **Complexidade**: [Simples=5 critérios | Médio=6 critérios | Complexo=...]
5. **Detalhes técnicos encontrados**:
   - Logs/erros: [listar ou "nenhum"]
   - Métricas: [listar ou "nenhum"]
   - Steps to reproduce: [listar ou "nenhum"]
6. **Lista de requisitos extraídos do bug**: [...]
</analise>
```

---

## 4. Structured Output

**O que é:** Definir um formato rígido de saída com seções, padrões e regras claras, garantindo consistência e facilitando avaliação automática.

**Onde foi aplicado (linhas 7-43 do prompt v2):** Formato obrigatório com 3 seções fixas e regras detalhadas:

```
**User Story:**
Como um [persona específica], eu quero [ação clara], para que [benefício tangível].

**Critérios de Aceitação:**
- Dado que [contexto inicial]
- Quando [ação]
- Então [resultado mensurável]
- E [validação]
- E [edge case relevante]

**Contexto Técnico:**
- [Apenas quando bug incluir logs, métricas ou steps to reproduce]
```

**Por que foi escolhido:** As 4 métricas de avaliação (Tone, Acceptance Criteria, User Story Format, Completeness) verificam elementos estruturais específicos. Sem um formato rígido:

- O modelo pode variar a estrutura da user story (prejudica "User Story Format Score")
- Os critérios podem não seguir Given-When-Then (prejudica "Acceptance Criteria Score")
- Detalhes técnicos podem ser omitidos ou misturados (prejudica "Completeness Score")

**Regras específicas do Structured Output:**

| Regra | Propósito |
|---|---|
| Exatamente "Como um... eu quero... para que..." | Garante aderência ao formato de user story |
| Padrão Given-When-Then em todos os critérios | Garante testabilidade dos critérios de aceitação |
| 5 critérios (simples) ou 6 (médio) | Calibra completude por complexidade do bug |
| Último bullet = edge case | Garante cobertura de cenários limítrofes |
| Contexto Técnico com valores EXATOS | Garante completude de informações técnicas |

---

## Comparação v1 vs v2

| Aspecto | v1 (Baseline) | v2 (Otimizado) |
|---|---|---|
| **Persona** | "assistente" genérico | "Product Manager sênior" (Role Prompting) |
| **Exemplos** | Nenhum | 4 exemplos com complexidade variada (Few-shot) |
| **Raciocínio** | Nenhum | 5 etapas com tags XML + checklist (CoT) |
| **Formato** | Livre ("crie uma user story") | 3 seções fixas + Given-When-Then (Structured Output) |
| **Tamanho** | ~6 linhas | ~288 linhas |
| **Técnicas** | 0 | 4 (Role Prompting, Few-shot, CoT, Structured Output) |
| **Score médio** | **0.8711** (Reprovado) | **0.9819** (Aprovado) |

### Resultados da avaliação comparativa

Scores obtidos na execução do `evaluate.py` com 15 exemplos do dataset:

| Métrica | v1 (Baseline) | v2 (Otimizado) | Melhoria | Técnica principal responsável |
|---|---|---|---|---|
| Tone Score | 0.99 | **0.99** | = | Role Prompting (persona PM + tom empático) |
| Acceptance Criteria Score | 0.88 | **0.96** | +0.08 | Structured Output (Given-When-Then) + Few-shot (exemplos) |
| User Story Format Score | 0.89 | **0.99** | +0.10 | Structured Output (formato "Como um... eu quero... para que...") |
| Completeness Score | 0.73 | **0.98** | +0.25 | Chain of Thought (análise prévia) + Few-shot (exemplos com Contexto Técnico) |
| **Média Geral** | **0.8711** | **0.9819** | **+0.1108** | Todas as 4 técnicas em conjunto |

> Critério de aprovação: média geral >= 0.9

A maior melhoria foi em **Completeness** (+0.25), onde o Chain of Thought com análise prévia (`<analise>`, `<rascunho_contexto>`) força o modelo a extrair todos os detalhes técnicos antes de gerar a resposta. A segunda maior melhoria foi em **User Story Format** (+0.10), diretamente atribuível ao Structured Output com formato rígido "Como um... eu quero... para que...".
