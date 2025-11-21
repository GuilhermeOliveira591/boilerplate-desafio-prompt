from langsmith import Client
import inspect

# Inicializa
client = Client()

# Pega a assinatura exata da função push_prompt instalada no seu ambiente
sig = inspect.signature(client.push_prompt)

print("\n========================================")
print("ASSINATURA DA FUNÇÃO:")
print(sig)
print("========================================\n")

# Lista os parametros para facilitar leitura
for name, param in sig.parameters.items():
    print(f"- {name}: {param.kind}")