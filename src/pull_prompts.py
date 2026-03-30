"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull do prompt: leonanluppi/bug_to_user_story_v1
3. Salva localmente em prompts/bug_to_user_story_v1.yml

IMPORTANTE: Este script extrai o conteúdo CORRETO do ChatPromptTemplate
do LangSmith Hub e salva em formato YAML editável.

Uso:
    python src/pull_prompts.py
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def main():
    """
    Função principal que faz pull do prompt inicial do Hub.

    Fluxo:
    1. Verifica variáveis de ambiente
    2. Faz pull de: leonanluppi/bug_to_user_story_v1
    3. Extrai SystemMessage e HumanMessage
    4. Salva em formato YAML em: prompts/bug_to_user_story_v1.yml
    """
    print_section_header("PULL DO PROMPT INICIAL DO LANGSMITH HUB")

    # 1. Verificar variáveis de ambiente
    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        print("\n💡 Dica: Configure LANGSMITH_API_KEY no arquivo .env")
        return 1

    # 2. Definir nome do prompt a ser baixado
    prompt_source = "leonanluppi/bug_to_user_story_v1"

    print(f"\n📥 Fazendo pull do prompt: {prompt_source}")
    print("   Este é o prompt INICIAL (não otimizado) fornecido como baseline.\n")

    try:
        # 3. Fazer pull do Hub
        prompt = hub.pull(prompt_source)
        print("   ✅ Pull bem-sucedido!")

        # 4. Extrair mensagens do ChatPromptTemplate
        if not hasattr(prompt, 'messages') or len(prompt.messages) == 0:
            print("\n❌ Erro: Prompt não tem mensagens")
            return 1

        system_prompt = ""
        user_prompt = "{bug_report}"

        print(f"\n📋 Extraindo conteúdo ({len(prompt.messages)} mensagens):")

        for i, msg in enumerate(prompt.messages, 1):
            msg_type = msg.__class__.__name__
            print(f"   [{i}] {msg_type}")

            # SystemMessagePromptTemplate
            if msg_type == "SystemMessagePromptTemplate":
                if hasattr(msg, 'prompt') and hasattr(msg.prompt, 'template'):
                    system_prompt = msg.prompt.template
                    print(f"       ✓ System prompt extraído ({len(system_prompt)} chars)")

            # HumanMessagePromptTemplate
            elif msg_type == "HumanMessagePromptTemplate":
                if hasattr(msg, 'prompt') and hasattr(msg.prompt, 'template'):
                    user_prompt = msg.prompt.template
                    print(f"       ✓ User prompt extraído: {user_prompt}")

        # 5. Validar extração
        if not system_prompt:
            print("\n⚠️  Aviso: System prompt está vazio!")

        # 6. Criar estrutura YAML
        yaml_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt inicial para converter bugs em User Stories (não otimizado)",
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": [
                    "bug-analysis",
                    "user-story",
                    "product-management",
                    "baseline"
                ],
            }
        }

        # 7. Salvar em arquivo YAML
        output_dir = Path("prompts")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "bug_to_user_story_v1.yml"

        print(f"\n💾 Salvando prompt em: {output_file}")

        if save_yaml(yaml_data, str(output_file)):
            print("   ✅ Arquivo salvo com sucesso!")

            # 8. Exibir próximos passos
            print("\n" + "=" * 70)
            print("✅ PULL CONCLUÍDO COM SUCESSO!")
            print("=" * 70)

            print("\n📋 PRÓXIMOS PASSOS:")
            print("\n1. Analise o prompt em: prompts/bug_to_user_story_v1.yml")
            print("\n2. Crie a versão otimizada:")
            print("   cp prompts/bug_to_user_story_v1.yml prompts/bug_to_user_story_v2.yml")
            print("\n3. Edite bug_to_user_story_v2.yml:")
            print("   • Troque a chave YAML de 'bug_to_user_story_v1:' para 'bug_to_user_story_v2:'")
            print("   • Adicione Few-shot examples no system_prompt")
            print("   • Melhore as instruções (Chain of Thought)")
            print("   • Defina uma persona especializada (Role Prompting)")
            print("   • Adicione campo: techniques_applied: ['Few-shot Learning', 'Chain of Thought']")
            print("\n4. Faça push do prompt otimizado:")
            print("   python src/push_prompts.py")
            print("\n5. Execute a avaliação:")
            print("   python src/evaluate.py")
            print("\n💡 Meta: Atingir score >= 0.9 em todas as 5 métricas!")

            return 0
        else:
            print("\n❌ Erro ao salvar arquivo YAML")
            return 1

    except Exception as e:
        print(f"\n❌ Erro ao fazer pull: {e}")
        print("\nVerifique:")
        print("- LANGSMITH_API_KEY está configurada corretamente no .env")
        print("- Você tem conexão com a internet")
        print(f"- Prompt {prompt_source} existe e está acessível")
        print("\nDetalhes do erro:")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
