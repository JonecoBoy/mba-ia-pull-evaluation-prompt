"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

DICAS DE IMPLEMENTAÇÃO:

- O push é feito pelo cliente do LangSmith:

      from langsmith import Client
      from langchain_core.prompts import ChatPromptTemplate

      client = Client()
      prompt = ChatPromptTemplate.from_messages([
          ("system", system_prompt),
          ("user", user_prompt),
      ])
      url = client.push_prompt(
          f"{username}/bug_to_user_story_v2",
          object=prompt,
          is_public=True,
          description="...",
          tags=[...],
      )

- `username` vem de USERNAME_LANGSMITH_HUB no .env e precisa ser o seu handle
  do Hub. Se você ainda não tem um handle, veja as instruções no .env.example.

- A variável do template precisa ser {bug_report}, que é a chave de entrada
  usada no dataset de avaliação.

- Use `load_yaml` de utils.py para ler o arquivo .yml.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPT_V2_PATH = str(PROJECT_ROOT / "prompts" / "bug_to_user_story_v2.yml")


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    client = Client()

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", prompt_data["system_prompt"]),
        ("user", prompt_data["user_prompt"]),
    ])

    try:
        url = client.push_prompt(
            prompt_name,
            object=prompt_template,
            is_public=True,
            description=prompt_data.get("description", ""),
            tags=prompt_data.get("tags", []),
        )
        print(f"✓ Push realizado com sucesso: {prompt_name}")
        print(f"  {url}")
        return True
    except Exception as e:
        err_msg = str(e).lower()
        if "has not changed" in err_msg or "nothing to commit" in err_msg:
            print(f"✓ Prompt já sincronizado com o LangSmith Hub (sem alterações): {prompt_name}")
            return True
        raise


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    required_fields = ["description", "system_prompt", "user_prompt", "version"]
    for field in required_fields:
        if field not in prompt_data or not str(prompt_data[field]).strip():
            errors.append(f"Campo obrigatório faltando ou vazio: {field}")

    system_prompt = prompt_data.get("system_prompt", "")
    if "[TODO]" in system_prompt or "TODO" in system_prompt:
        errors.append("system_prompt ainda contém TODOs")

    techniques = prompt_data.get("techniques_applied", [])
    if len(techniques) < 2:
        errors.append(f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS PARA O LANGSMITH")

    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB")

    prompts = load_yaml(PROMPT_V2_PATH)
    if prompts is None:
        return 1

    prompt_data = prompts.get("bug_to_user_story_v2")
    if prompt_data is None:
        print("❌ Chave 'bug_to_user_story_v2' não encontrada no YAML")
        return 1

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido:")
        for error in errors:
            print(f"   - {error}")
        return 1

    prompt_name = f"{username}/bug_to_user_story_v2"

    try:
        success = push_prompt_to_langsmith(prompt_name, prompt_data)
    except Exception as e:
        print(f"❌ Erro ao fazer push do prompt: {e}")
        return 1

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
