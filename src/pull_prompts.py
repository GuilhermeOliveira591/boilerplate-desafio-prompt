"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz o pull do prompt do Hub (usando o USUÁRIO correto)
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa o cliente LangSmith e resolve o nome do usuário automaticamente.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

def main():
    print_section_header("PULL DE PROMPTS DO LANGSMITH")

    # 1. Verificação de variáveis de ambiente
    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    # 2. Configuração
    hub_username = os.getenv("USERNAME_LANGSMITH_HUB")
    prompt_name = "bug_to_user_story_v2"
    
    # Monta o handle correto: usuario/nome-do-prompt
    prompt_handle = f"{hub_username}/{prompt_name}"
    
    output_path = Path(f"prompts/{prompt_name}.yml")
    
    # Garante que a pasta prompts existe
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # 3. Conectar e fazer o Pull
        print(f"🔌 Conectando ao LangSmith Hub...")
        client = Client()
        
        print(f"⬇️  Baixando prompt: {prompt_handle}")
        
        # O objeto retornado é um ChatPromptTemplate do LangChain
        prompt_object = client.pull_prompt(prompt_handle)
        
        # 4. Extrair conteúdo para o formato YAML simplificado do projeto
        system_msg = ""
        user_msg = ""
        
        # Lógica robusta para extrair mensagens de diferentes estruturas do LangChain
        for msg in prompt_object.messages:
            # Tenta extrair o template (texto cru com variáveis {var})
            content = ""
            if hasattr(msg, 'prompt') and hasattr(msg.prompt, 'template'):
                content = msg.prompt.template
            elif hasattr(msg, 'content'):
                content = msg.content
            
            # Classifica entre System e User
            msg_type = str(type(msg)).lower()
            if 'system' in msg_type or (hasattr(msg, 'type') and msg.type == 'system'):
                system_msg = content
            else:
                # Assume que qualquer outra coisa é a mensagem do usuário/human
                user_msg = content

        # Monta o dicionário estruturado
        prompt_data = {
            prompt_name: {
                "description": f"Prompt recuperado do LangSmith Hub ({prompt_handle})",
                "system_prompt": system_msg,
                "user_prompt": user_msg,
                "version": "v1_pulled",
                "tags": ["restored", "langsmith-hub"]
            }
        }

        # 5. Salvar localmente
        save_yaml(str(output_path), prompt_data)
        
        print(f"\n✅ Prompt salvo com sucesso em: {output_path}")
        print("Conteúdo extraído:")
        print(f" - System Prompt: {len(system_msg)} caracteres")
        print(f" - User Prompt: {len(user_msg)} caracteres")
        
        return 0

    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ Erro ao fazer pull do prompt: {error_msg}")
        
        if "404" in error_msg:
             print(f"\n⚠️  Dica: Verifique se o prompt '{prompt_handle}' realmente existe no LangSmith.")
             print("   Se você nunca fez o 'push' deste prompt, você não conseguirá fazer o 'pull'.")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())