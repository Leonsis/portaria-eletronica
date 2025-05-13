import re
import os

def alterar_config(filepath, novas_configuracoes):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            conteudo = file.read()

        # Localiza o bloco CONFIG e substitui pelas novas configurações
        padrao = r"CONFIG\s*=\s*\{.*?\}"
        novas_config_str = f"CONFIG = {novas_configuracoes}"
        conteudo_atualizado = re.sub(padrao, novas_config_str, conteudo, flags=re.DOTALL)

        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(conteudo_atualizado)

        print("CONFIG atualizado com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar CONFIG: {e}")

if __name__ == "__main__":
    # Localiza o arquivo "start_server.py" no mesmo diretório
    caminho_arquivo = os.path.join(os.path.dirname(__file__), "start_server.py")
    if not os.path.exists(caminho_arquivo):
        print(f"Arquivo 'start_server.py' não encontrado no diretório atual.")
    else:
        print("Digite as novas configurações para o CONFIG:")
        novas_config = {
            'escola': input("Escola: ").strip(),
            'telefone': input("Telefone: ").strip(),
            'endereco': input("Endereço: ").strip(),
            'validade': input("Validade: ").strip(),
            'assinatura': 'assinatura.png'
        }
        alterar_config(caminho_arquivo, novas_config)
