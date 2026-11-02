"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull do prompt semente do desafio
3. Salva localmente em prompts/bug_to_user_story_v1.yml

DICAS DE IMPLEMENTAÇÃO:

- O pull é feito pelo cliente do LangSmith:

      from langsmith import Client
      client = Client()
      prompt = client.pull_prompt(
          "leonanluppi/bug_to_user_story_v1",
          dangerously_pull_public_prompt=True,
      )

- O parâmetro `dangerously_pull_public_prompt=True` é obrigatório sempre que o
  identificador tem dono explícito ("owner/nome"). O LangSmith bloqueia esse pull
  por padrão porque um prompt do Hub é um objeto LangChain serializado, que pode
  vir de terceiros. Aqui o prompt é o do desafio, então o risco é conhecido.

- O retorno é um ChatPromptTemplate. Para extrair o conteúdo das mensagens,
  use a serialização nativa do LangChain (`prompt.messages`, e o atributo
  `.prompt.template` de cada mensagem).

- Use `save_yaml` de utils.py para gravar o resultado no arquivo .yml.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPT_ID = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = str(PROJECT_ROOT / "prompts" / "bug_to_user_story_v1.yml")


def pull_prompts_from_langsmith():
    """
    Faz pull do prompt semente do desafio e salva localmente em YAML.

    Returns:
        True se sucesso, False caso contrário
    """
    client = Client()

    print(f"Puxando prompt do LangSmith Hub: {PROMPT_ID}")
    prompt = client.pull_prompt(PROMPT_ID, dangerously_pull_public_prompt=True)

    messages = prompt.messages
    system_prompt = messages[0].prompt.template if messages else ""
    user_prompt = messages[1].prompt.template if len(messages) > 1 else ""

    prompt_data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    if not save_yaml(prompt_data, OUTPUT_PATH):
        return False

    print(f"✓ Prompt salvo em {OUTPUT_PATH}")
    return True


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH")

    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return 1

    try:
        success = pull_prompts_from_langsmith()
    except Exception as e:
        print(f"❌ Erro ao fazer pull do prompt: {e}")
        return 1

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
