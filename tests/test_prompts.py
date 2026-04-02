"""
Testes automatizados para validação de prompts.
"""

import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="class")
def prompts():
    """Fixture que carrega o arquivo de prompts uma vez para todos os testes."""
    return load_prompts("prompts/bug_to_user_story_v2.yml")


@pytest.fixture(scope="class")
def prompt_data(prompts):
    """Fixture que extrai os dados do prompt v2."""
    data = prompts.get("bug_to_user_story_v2")
    assert data is not None, "Chave 'bug_to_user_story_v2' não encontrada"
    return data


@pytest.fixture(scope="class")
def system_prompt(prompt_data):
    """Fixture que extrai o system_prompt."""
    return prompt_data.get("system_prompt", "")


class TestPrompts:
    def test_basic_structure_validation(self, prompt_data):
        """Valida estrutura básica do prompt usando validate_prompt_structure."""
        # Usa a função de validação estrutural do utils.py
        is_valid, errors = validate_prompt_structure(prompt_data)

        # Filtra erros de TODO (falso positivo com "TODOS" em português)
        # O teste test_prompt_no_todos já faz validação mais precisa
        errors_filtered = [e for e in errors if "TODO" not in e]

        assert len(errors_filtered) == 0, (
            f"Validação estrutural falhou: {', '.join(errors_filtered)}"
        )

    def test_prompt_has_system_prompt(self, system_prompt):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert system_prompt.strip(), "system_prompt está vazio ou não existe"
        assert len(system_prompt) > 50, "system_prompt parece muito curto"

    def test_prompt_has_role_definition(self, system_prompt):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        # Check for role prompting pattern
        assert "Você é" in system_prompt or "você é" in system_prompt, (
            "Prompt não define uma persona clara com 'Você é'"
        )

        # Verify specificity (not just generic)
        assert "Product Manager" in system_prompt or "especializado" in system_prompt, (
            "Persona não é específica o suficiente"
        )

    def test_prompt_mentions_format(self, system_prompt):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        # Check for format section
        format_keywords = ["FORMATO", "User Story", "Markdown", "Como um"]
        has_format = any(keyword in system_prompt for keyword in format_keywords)
        assert has_format, (
            "Prompt não menciona formato específico (User Story/Markdown)"
        )

        # Verify the exact User Story pattern
        assert "Como um" in system_prompt and "eu quero" in system_prompt, (
            "Prompt não menciona o padrão 'Como um... eu quero... para que...'"
        )

    def test_prompt_has_few_shot_examples(self, system_prompt):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        # Check for examples section
        assert "## EXEMPLOS DO DATASET" in system_prompt, (
            "Prompt não tem seção de exemplos"
        )

        # Count examples (should have at least 2)
        example_count = system_prompt.count("### Exemplo")
        assert example_count >= 2, (
            f"Prompt tem apenas {example_count} exemplos, mínimo é 2"
        )

        # Verify structure (Bug -> User Story pattern)
        assert "Bug:" in system_prompt and "User Story:" in system_prompt, (
            "Exemplos não seguem padrão Bug -> User Story"
        )

    def test_prompt_no_todos(self, system_prompt):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        # Check for common TODO patterns
        todo_patterns = ["[TODO]", "[todo]", "TODO:", "FIXME", "[FIXME]"]
        found_todos = [pattern for pattern in todo_patterns if pattern in system_prompt]

        assert not found_todos, f"Encontrados TODOs não completados: {found_todos}"

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_data.get("techniques_applied", [])
        assert isinstance(techniques, list), "techniques_applied deve ser uma lista"
        assert len(techniques) >= 2, (
            f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}"
        )

        # Optional: validate technique names
        valid_techniques = {
            "role_prompting",
            "few_shot_learning",
            "chain_of_thought",
            "tree_of_thought",
            "structured_output",
        }
        invalid = [t for t in techniques if t.lower() not in valid_techniques]
        if invalid:
            print(f"⚠️ Técnicas não reconhecidas: {invalid} (aviso, não erro)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
