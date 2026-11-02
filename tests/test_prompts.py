"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
import re
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

PROMPT_V2_PATH = str(Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml")


class TestPrompts:
    @pytest.fixture(autouse=True)
    def setup(self):
        data = load_prompts(PROMPT_V2_PATH)
        self.prompt_data = data["bug_to_user_story_v2"]
        self.system_prompt = self.prompt_data.get("system_prompt", "")

    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in self.prompt_data
        assert self.prompt_data["system_prompt"].strip() != ""

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        assert re.search(r"voc[eê] [ée] um", self.system_prompt, re.IGNORECASE)

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        lowered = self.system_prompt.lower()
        assert "markdown" in lowered or "user story" in lowered

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        lowered = self.system_prompt.lower()
        assert "exemplo" in lowered
        assert lowered.count("exemplo") >= 2

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        assert "[TODO]" not in self.system_prompt
        assert "TODO" not in self.system_prompt

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = self.prompt_data.get("techniques_applied", [])
        assert len(techniques) >= 2

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])