# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **prompt optimization challenge** for converting bug reports into user stories. The workflow involves:
1. Pulling baseline prompts from LangSmith Hub
2. Refactoring prompts using advanced prompt engineering techniques
3. Pushing optimized prompts back to LangSmith
4. Evaluating prompt quality against 4 custom metrics (Tone, Acceptance Criteria, User Story Format, Completeness)
5. Iterating until all metrics achieve ≥ 0.9 score

**Critical constraint:** Average score must be ≥ 0.9 across all 4 metrics.

## Key Commands

### Development Workflow (in order)
```bash
# 1. Pull baseline prompts from LangSmith Hub
python src/pull_prompts.py

# 2. Push optimized prompts to LangSmith Hub
python src/push_prompts.py

# 3. Evaluate prompts (runs against all 15 examples in dataset)
python src/evaluate.py

# 4. Run validation tests
pytest tests/test_prompts.py -v
```

### Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure .env (copy from .env.example)
cp .env.example .env
# Edit .env with your API keys
```

## Architecture & Key Concepts

### Evaluation System
- **Dataset**: `datasets/bug_to_user_story.jsonl` (15 examples: 5 simple, 7 medium, 3 complex)
- **Source of truth**: LangSmith Hub prompts (NOT local YAML files)
- **Evaluation flow**:
  1. `evaluate.py` pulls prompts from LangSmith Hub
  2. Runs each prompt against all dataset examples
  3. Calculates 4 metrics using GPT-4o as judge (see `src/metrics.py`)
  4. Publishes results to LangSmith project dashboard

**IMPORTANT:** `evaluate.py` line 212 evaluates ALL 15 examples (not just 10). This was modified from `examples[:10]` to `examples` to reduce non-deterministic variance in scores.

### Prompt Engineering Techniques Required
The optimized prompt (`prompts/bug_to_user_story_v2.yml`) must apply **at least 2** of these techniques:
- **Role Prompting**: Define persona (e.g., "You are a Product Manager")
- **Few-shot Learning**: Include 2-3 clear input/output examples
- **Chain of Thought (CoT)**: Instruct model to "think step by step"
- **Tree of Thought**: Explore multiple reasoning paths
- **Structured Output**: Enforce specific format (User Story + Acceptance Criteria + Technical Context)

Current implementation uses 4 techniques: Role Prompting, Few-shot Learning, Chain of Thought (with explicit XML tags), and Structured Output.

### LLM Provider System
The codebase supports **multi-provider** LLM access via `src/utils.py`:
- **OpenAI**: `gpt-4o-mini` (generation), `gpt-4o` (evaluation)
- **Google Gemini**: `gemini-2.5-flash` (both generation and evaluation)

Configure via `.env`:
```bash
LLM_PROVIDER=openai  # or 'google'
LLM_MODEL=gpt-4o-mini
EVAL_MODEL=gpt-4o
```

Use `get_llm()` for generation and `get_eval_llm()` for evaluation throughout the codebase.

### Prompt Structure (YAML)
Prompts in `prompts/*.yml` must follow this structure:
```yaml
prompt_name:
  description: "..."
  system_prompt: |
    Your prompt content here
  user_prompt: "{bug_report}"
  version: "v2"
  created_at: "YYYY-MM-DD"
  tags: [...]
  techniques_applied:
    - "role_prompting"
    - "few_shot_learning"
    # Must list at least 2
```

### Four Evaluation Metrics
Implemented in `src/metrics.py`:

1. **Tone Score**: Professional and empathetic tone
2. **Acceptance Criteria Score**: Clear, testable Given-When-Then format
3. **User Story Format Score**: Follows "Como um... eu quero... para que..." structure
4. **Completeness Score**: Includes all technical details (logs, metrics, steps, integrations)

Each metric uses GPT-4o as judge, comparing the generated output against a reference answer in the dataset.

## Critical Files

### Prompts
- `prompts/bug_to_user_story_v1.yml`: Baseline (poor quality)
- `prompts/bug_to_user_story_v2.yml`: Optimized version (must achieve ≥0.9)

### Core Scripts
- `src/pull_prompts.py`: Pulls prompts from LangSmith Hub
- `src/push_prompts.py`: Pushes prompts to LangSmith Hub (validates structure first)
- `src/evaluate.py`: Main evaluation script (pulls from Hub, runs metrics)
- `src/metrics.py`: Implements 4 custom metrics using LLM-as-judge
- `src/utils.py`: Shared utilities (YAML handling, LLM initialization, validation)

### State Tracking
- `ONDE_PAREI.md`: Current progress snapshot (score: 0.8908, need 0.9)
- `memory/PROGRESSO_ITERACAO.md`: Full iteration history (5 iterations completed)
- `memory/MEMORY.md`: Key lessons learned (overengineering pitfall, non-deterministic variance)

## Current Status & Next Steps

**Current Score**: 0.8908 (needs 0.0092 more to reach 0.9)
- Tone: 0.92 ✓
- Acceptance: 0.88 ✗
- Format: 0.93 ✓
- Completeness: 0.83 ✗

**Pending Changes** (applied but not yet evaluated):
- Line ~153 in `bug_to_user_story_v2.yml`: Reinforced Given-When-Then format requirement
- Line ~159: Emphasized "transcribe EXACT values - don't paraphrase"

**To continue**:
```bash
python src/push_prompts.py && python src/evaluate.py
```

**Decision tree**:
- If score ≥ 0.9: Document results in README.md, capture screenshots, commit
- If 0.89-0.9: Accept as passing or do 1 final iteration
- If < 0.89: Revert surgical changes, document variance as limitation

## Key Lessons from Iteration History

1. **Overengineering hurts**: Adding verbose checklists dropped score from 0.9127 to 0.8827. Keep changes surgical (1-2 lines), not verbose paragraphs.

2. **Non-deterministic variance**: GPT-4o scores vary ±0.01-0.02 between runs. Evaluating all 15 examples (not 10) provides more stable averages.

3. **Official criterion**: Code checks `average_score >= 0.9` (line 298 of `evaluate.py`), not individual metrics.

4. **Hub is source of truth**: `evaluate.py` always pulls from LangSmith Hub, NOT local YAML files. Always push before evaluating.

## LangSmith Integration

- **Hub URL**: https://smith.langchain.com/prompts/casaccia/bug_to_user_story_v2
- **Project Dashboard**: https://smith.langchain.com/projects/prompt-optimization-challenge-resolved
- Prompts must be marked as **public** on the Hub (enforced by `push_prompts.py`)

## Testing

Validation tests in `tests/test_prompts.py` verify:
- System prompt exists and isn't empty
- Role definition present (e.g., "Product Manager")
- Format requirements mentioned (Markdown/User Story)
- Few-shot examples included
- No TODOs left in prompt
- Minimum 2 techniques listed in metadata

Run with: `pytest tests/test_prompts.py -v`
