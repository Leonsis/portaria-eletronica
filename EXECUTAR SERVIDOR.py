import subprocess
import sys
import os

# Limpa a tela
os.system('cls' if os.name == 'nt' else 'clear')

# Lista dos scripts que você deseja executar
script_paths = [
    'app.py',
    'carteirinha.py',
    'upload.py'
]

processes = []

for script in script_paths:
    try:
        # Inicia cada script em um processo separado com saída redirecionada
        process = subprocess.Popen([sys.executable, script], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
        processes.append(process)
    except Exception as e:
        print(f"Erro ao iniciar {script}: {e}")

print("\nPORTARIA ELETRÔNICA v1.0\n")
print("\nPara executar as ações localmente:\n")
print("http://localhost:5000 - Painel de Registro de Presença e Consulta de Acessos")
print("http://localhost:5010 - Painel Administrativo (para editar, remover ou incluir cadastro)")
print("http://localhost:5020 - Painel de Emissão de Carteirinha\n")
print("Para executar as ações remotamente:\n")
print("Troque \"localhost\" pelo IP do servidor.")
print("Para sair do servidor, basta fechar a janela do terminal ou pressionar Ctrl+C.\n")

# Aguarda todos os processos terminarem silenciosamente
for process in processes:
    process.wait()