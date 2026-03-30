"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

Uso:
    python src/push_prompts.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt do YAML

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros

    Validações:
    - Campos obrigatórios: description, system_prompt, version
    - system_prompt não vazio
    - system_prompt não contém TODOs
    - Mínimo 2 técnicas listadas (se campo existe)
    """
    errors = []

    # 1. Verificar campos obrigatórios
    required_fields = ["description", "system_prompt", "version"]
    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"❌ Campo obrigatório faltando: '{field}'")

    # 2. Verificar se system_prompt não está vazio
    system_prompt = prompt_data.get("system_prompt", "").strip()
    if not system_prompt:
        errors.append("❌ Campo 'system_prompt' está vazio")
    else:
        # 3. Verificar se não tem TODOs pendentes (apenas [TODO] ou TODO:)
        if "[TODO]" in system_prompt or "TODO:" in system_prompt:
            errors.append("⚠️  O 'system_prompt' ainda contém TODOs pendentes")

    # 4. Verificar técnicas aplicadas
    techniques = prompt_data.get("techniques_applied", [])
    if isinstance(techniques, list) and len(techniques) < 2:
        errors.append(
            f"⚠️  Campo 'techniques_applied' deve ter pelo menos 2 técnicas "
            f"(encontradas: {len(techniques)})"
        )

    # 5. Verificar se user_prompt existe
    if "user_prompt" not in prompt_data:
        errors.append(
            "⚠️  Campo 'user_prompt' não encontrado (recomendado: '{bug_report}')"
        )

    is_valid = len(errors) == 0
    return (is_valid, errors)


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt (ex: "bug_to_user_story_v2")
        prompt_data: Dados do prompt do YAML

    Returns:
        True se sucesso, False caso contrário

    Formato esperado do prompt_data:
    {
        "description": "...",
        "system_prompt": "...",
        "user_prompt": "{bug_report}",
        "version": "v2",
        "tags": ["tag1", "tag2"],
        "techniques_applied": ["Few-shot", "Chain of Thought"]
    }
    """
    try:
        username = os.getenv("USERNAME_LANGSMITH_HUB")
        if not username:
            print("❌ USERNAME_LANGSMITH_HUB não configurado no .env")
            print(
                "\nPara obter seu username, publique um prompt no LangSmith Hub e copie o username da URL."
            )
            return False

        # Criar o ChatPromptTemplate
        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "{bug_report}")

        # Criar mensagens do template
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessagePromptTemplate.from_template(user_prompt),
        ]

        prompt_template = ChatPromptTemplate.from_messages(messages)

        # Montar nome completo do prompt (com username)
        full_prompt_name = f"{username}/{prompt_name}"

        print(f"\n📤 Fazendo push do prompt para o LangSmith Hub...")
        print(f"   Nome: {full_prompt_name}")
        print(f"   Descrição: {prompt_data.get('description', 'N/A')}")

        # Preparar metadados
        tags = prompt_data.get("tags", [])
        techniques = prompt_data.get("techniques_applied", [])

        # Adicionar técnicas às tags
        if techniques:
            print(f"   Técnicas: {', '.join(techniques)}")
            tags.extend([f"technique:{t}" for t in techniques])

        # Fazer push para o Hub (PÚBLICO)
        hub.push(
            full_prompt_name,
            prompt_template,
            new_repo_is_public=True,  # IMPORTANTE: Público para o evaluate.py funcionar
        )

        print(f"\n✅ Prompt publicado com sucesso!")
        print(f"   URL: https://smith.langchain.com/prompts/{full_prompt_name}")
        print(f"   Versão: {prompt_data.get('version', 'N/A')}")
        print(f"   Tags: {', '.join(prompt_data.get('tags', []))}")

        return True

    except Exception as e:
        print(f"\n❌ Erro ao fazer push do prompt: {e}")
        print("\nVerifique:")
        print("- LANGSMITH_API_KEY está configurada corretamente no .env")
        print("- USERNAME_LANGSMITH_HUB está configurado no .env")
        print("- Você tem conexão com a internet")
        print("- O prompt está no formato correto")
        return False


def main():
    """
    Função principal que orquestra o push dos prompts.

    Fluxo:
    1. Verifica variáveis de ambiente
    2. Carrega o arquivo YAML do prompt v2
    3. Valida a estrutura
    4. Faz push para o LangSmith Hub
    """
    print_section_header("PUSH DE PROMPTS PARA LANGSMITH HUB")

    # 1. Verificar variáveis de ambiente
    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        print("\n💡 Dica: Configure o arquivo .env antes de continuar")
        return 1

    # 2. Definir arquivo do prompt
    prompt_file = Path("prompts/bug_to_user_story_v2.yml")

    if not prompt_file.exists():
        print(f"\n❌ Arquivo não encontrado: {prompt_file}")
        print("\nPara criar o prompt otimizado:")
        print("1. Copie o arquivo prompts/bug_to_user_story_v1.yml")
        print("2. Renomeie para bug_to_user_story_v2.yml")
        print("3. Otimize o prompt aplicando técnicas de Prompt Engineering:")
        print("   - Few-shot Learning")
        print("   - Chain of Thought")
        print("   - Role Prompting")
        print("   - Estruturação clara")
        print("\n4. Execute novamente: python src/push_prompts.py")
        return 1

    print(f"\n📂 Carregando prompt de: {prompt_file}")

    # 3. Carregar arquivo YAML
    prompts_data = load_yaml(str(prompt_file))
    if not prompts_data:
        print("❌ Erro ao carregar arquivo YAML")
        return 1

    # 4. Identificar o prompt v2
    prompt_key = "bug_to_user_story_v2"
    if prompt_key not in prompts_data:
        print(f"\n❌ Prompt '{prompt_key}' não encontrado no arquivo YAML")
        print(f"\nEstrutura esperada:")
        print(f"bug_to_user_story_v2:")
        print(f"  description: '...'")
        print(f"  system_prompt: |")
        print(f"    ...")
        print(f"  user_prompt: '{{bug_report}}'")
        print(f"  version: 'v2'")
        return 1

    prompt_data = prompts_data[prompt_key]

    # 5. Validar prompt
    print(f"\n🔍 Validando prompt '{prompt_key}'...")
    is_valid, errors = validate_prompt(prompt_data)

    if not is_valid:
        print("\n❌ Validação falhou:")
        for error in errors:
            print(f"   {error}")

        print("\n💡 Corrija os erros acima e execute novamente.")
        return 1

    print("   ✅ Validação passou!")

    # 6. Fazer push do prompt
    success = push_prompt_to_langsmith(prompt_key, prompt_data)

    if success:
        print("\n" + "=" * 70)
        print("✅ PUSH CONCLUÍDO COM SUCESSO!")
        print("=" * 70)
        print("\n📋 Próximos passos:")
        print("1. Verifique o prompt no LangSmith Hub")
        print("2. Teste o prompt manualmente se desejar")
        print("3. Execute a avaliação:")
        print("   python src/evaluate.py")
        print(
            "\n💡 Lembre-se: O prompt deve atingir score >= 0.9 em todas as métricas!"
        )
        return 0
    else:
        print("\n❌ PUSH FALHOU")
        print("\nVerifique os erros acima e tente novamente.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
