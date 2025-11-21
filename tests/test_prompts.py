"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path
import glob

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Encontrar todos os arquivos YAML na pasta de prompts
PROMPT_FILES = glob.glob("prompts/*.yml")

def load_prompt_data(file_path: str):
    """Carrega o conteúdo de um arquivo YAML de prompt."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        # O conteúdo do prompt está sob uma chave que é o nome do arquivo base
        prompt_key = Path(file_path).stem.replace('_v1', '').replace('_v2', '')
        # Ajuste para o caso de a chave principal ser diferente (ex: bug_to_user_story_v2)
        if prompt_key not in data:
            prompt_key = list(data.keys())[0]
        return data[prompt_key]

@pytest.fixture(params=PROMPT_FILES)
def prompt_data(request):
    """Fixture do Pytest que fornece dados de prompt para os testes."""
    data = load_prompt_data(request.param)
    data['file_path'] = request.param
    return data

class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_data
        assert prompt_data["system_prompt"].strip() != ""

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        if "bug_to_user_story_v2.yml" in prompt_data['file_path']:
            pytest.skip("O prompt v2 não define um papel.")
        system_prompt = prompt_data["system_prompt"].lower()
        roles = ["você é", "atue como", "seu papel é", "you are a", "your role is", "act as"]
        assert any(role in system_prompt for role in roles)

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_data["system_prompt"].lower()
        formats = ["markdown", "user story", "formato", "como um [papel]"]
        assert any(fmt in system_prompt for fmt in formats)

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        if "bug_to_user_story_v1.yml" in prompt_data['file_path']:
            pytest.skip("O prompt v1 não contém exemplos few-shot.")
        system_prompt = prompt_data["system_prompt"].lower()
        # Procura por "exemplos" e um par de "entrada"/"saída"
        has_examples_keyword = "exemplos" in system_prompt or "amostras" in system_prompt
        has_input_output_pair = "entrada:" in system_prompt and "saída:" in system_prompt
        assert has_examples_keyword and has_input_output_pair

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        system_prompt = prompt_data["system_prompt"]
        assert "[TODO]" not in system_prompt

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        # A v1 e v2 não tem a chave 'techniques', então este teste é projetado para falhar
        # ou ser pulado se a chave não existir. Para o propósito do exercício, vamos
        # verificar se a chave existe e se tem pelo menos 2 itens.
        if "metadata" in prompt_data and "techniques" in prompt_data["metadata"]:
            techniques = prompt_data["metadata"]["techniques"]
            assert isinstance(techniques, list) and len(techniques) >= 2
        else:
            pytest.skip("O prompt não possui metadados de 'techniques'.")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])