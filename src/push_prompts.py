import os
import sys
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.load import dumpd # <--- IMPORTANTE: Para converter em dicionário
from pathlib import Path
from typing import Dict, Any
import yaml
from langsmith import Client 

# 1. Carregar variáveis de ambiente
load_dotenv()

# --- Funções Utilitárias ---

def check_env_vars(required_vars: list):
    if "LANGSMITH_API_KEY" in required_vars:
        api_key = os.getenv("LANGSMITH_API_KEY", "").strip()
        if not api_key:
            print("ERRO: A variável LANGSMITH_API_KEY deve ser definida no .env.")
            sys.exit(1)
        os.environ["LANGCHAIN_API_KEY"] = api_key
    
    if "USERNAME_LANGSMITH_HUB" in required_vars:
        hub_owner = os.getenv("USERNAME_LANGSMITH_HUB", "").strip()
        if not hub_owner:
            print("ERRO: A variável USERNAME_LANGSMITH_HUB deve ser definida no .env.")
            sys.exit(1)
        os.environ["USERNAME_LANGSMITH_HUB"] = hub_owner
        os.environ["LANGCHAIN_HUB_OWNER"] = hub_owner

    missing = [var for var in required_vars if not os.getenv(var) and var not in ["USERNAME_LANGSMITH_HUB", "LANGSMITH_API_KEY"]]
    if missing:
        print(f"ERRO: Faltam variáveis: {', '.join(missing)}")
        sys.exit(1)

def print_section_header(title: str):
    print(f"\n{'='*60}\n {title} \n{'='*60}")

def load_yaml(file_path: Path) -> Dict[str, Any]:
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# --- Lógica Principal ---

def push_optimized_prompt():
    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    check_env_vars(required_vars)
    
    HUB_OWNER = os.environ["USERNAME_LANGSMITH_HUB"]
    PROMPT_REPO_NAME = "bug_to_user_story_v2"
    PROMPT_FILE = Path(f"prompts/{PROMPT_REPO_NAME}.yml") 
    
    print_section_header(f"Carregando Prompt de {PROMPT_FILE}")
    try:
        yaml_data = load_yaml(PROMPT_FILE)
        prompt_data = yaml_data[PROMPT_REPO_NAME] 
        system_content = prompt_data["system_prompt"]
        user_content = prompt_data["user_prompt"]
        
        print(f"Nome do Repositório: {PROMPT_REPO_NAME}")
        print(f"Proprietário (Handle): {HUB_OWNER}")
        
    except Exception as e:
        print(f"ERRO ao carregar o YAML: {e}")
        sys.exit(1)

    messages = [("system", system_content), ("human", user_content)]
    prompt_template = ChatPromptTemplate.from_messages(messages)
    
    # --- CORREÇÃO DE FORMATO: USAR DICIONÁRIO ---
    # A API espera um Objeto/Dict, não uma string JSON.
    # Usamos dumpd para converter o objeto LangChain em um Dict serializável.
    try:
        prompt_content_object = dumpd(prompt_template)
    except Exception as e:
        print(f"Erro ao converter prompt para dict: {e}")
        sys.exit(1)
    
    print_section_header(f"Inicializando Cliente LangSmith")
    try:
        client = Client()
    except Exception as e:
        print(f"ERRO ao inicializar o Cliente LangSmith: {e}")
        sys.exit(1)

    full_repo_name = f"{HUB_OWNER}/{PROMPT_REPO_NAME}"
        
    print_section_header(f"Fazendo Push para o Hub ({full_repo_name})")
    
    try:
        # Chamada Correta:
        # 1. Nome do Repo (Posicional)
        # 2. Conteúdo como DICT (Keyword 'object')
        
        url = client.push_prompt(
            full_repo_name,             
            object=prompt_content_object, # Agora passando um Dict!
            is_public=True,
            tags=prompt_data.get("tags", []),
            description=prompt_data.get("description")
        )
        
        print_section_header("SUCESSO")
        print(f"Prompt enviado com sucesso!")
        print(f"URL PÚBLICO: {url}")
        
    except Exception as e:
        print_section_header("ERRO NO PUSH")
        print(f"Detalhes do Erro: {e}")
        sys.exit(1)

if __name__ == "__main__":
    push_optimized_prompt()