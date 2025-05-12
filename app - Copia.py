import logging

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)

# Criação do logger
logger = logging.getLogger(__name__)

# Exemplo de uso do logger
logger.info("Iniciando o aplicativo Flask")

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import csv
import datetime
import os
import requests
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'registros'
app.config['STATIC_FOLDER'] = 'static'

TELEGRAM_TOKEN = '452429006:AAHfFItKogarQKTQftX5eNC05n86-155CgQ'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'

TURNOS = ['Manhã', 'Tarde', 'Noite']
contadores = defaultdict(int)
registros_diarios = []

def reset_contadores():
    """Reset counters at midnight"""
    global contadores, registros_diarios
    contadores.clear()
    # Save daily records to CSV
    if registros_diarios:
        data = datetime.now().strftime("%Y-%m-%d")
        pasta_registros = 'registros_diarios'
        if not os.path.exists(pasta_registros):
            os.makedirs(pasta_registros)
        
        arquivo = os.path.join(pasta_registros, f"{data}.csv")
        with open(arquivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['codigo', 'turno', 'data/hora'])
            writer.writeheader()
            for registro in registros_diarios:
                writer.writerow({
                    'codigo': registro['codigo'],
                    'turno': registro['turno'],
                    'data/hora': f"{datetime.now().strftime('%Y-%m-%d')} {registro['hora']}"
                })
    
    registros_diarios.clear()

def salvar_registro_diario(registro):
    """Salva o registro no arquivo CSV do dia atual"""
    data = datetime.now().strftime("%Y-%m-%d")
    pasta_registros = 'registros_diarios'
    if not os.path.exists(pasta_registros):
        os.makedirs(pasta_registros)
    
    arquivo = os.path.join(pasta_registros, f"{data}.csv")
    arquivo_existe = os.path.exists(arquivo)
    
    with open(arquivo, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['codigo', 'turno', 'data/hora'])
        if not arquivo_existe:
            writer.writeheader()
        writer.writerow({
            'codigo': registro['codigo'],
            'turno': registro['turno'],
            'data/hora': f"{datetime.now().strftime('%Y-%m-%d')} {registro['hora']}"
        })

def buscar_aluno(codigo):
    with open('database.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Codigo'] == codigo.strip():
                return row
    return None

def registrar_acesso(codigo, nome, turma):
    # Fix the datetime usage here
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    registro = f"{data_hora} - Acesso registrado"
    
    pasta_turma = os.path.join(app.config['UPLOAD_FOLDER'], turma)
    if not os.path.exists(pasta_turma):
        os.makedirs(pasta_turma)
        
    arquivo_path = os.path.join(pasta_turma, f"{codigo}.txt")
    
    # Verifica se o arquivo existe para decidir se adiciona cabeçalho
    arquivo_existe = os.path.exists(arquivo_path)
    
    with open(arquivo_path, 'a', encoding='utf-8') as f:
        if not arquivo_existe:
            # Adiciona cabeçalho com informações do aluno
            aluno = buscar_aluno(codigo)
            f.write(f"Nome: {nome}\n")
            f.write(f"Turma: {turma}\n")
            f.write(f"Turno: {aluno['Turno']}\n")
            f.write(f"Código: {codigo}\n")
            f.write("\nREGISTRO DE ACESSOS:\n")
            f.write("-" * 30 + "\n")
        
        f.write(f"{registro}\n")
    
    # Update counter
    aluno = buscar_aluno(codigo)
    if aluno:
        contadores[aluno['Turno']] += 1
        
        # Add to daily records
        registro_diario = {
            'hora': datetime.now().strftime("%H:%M:%S"),
            'codigo': codigo,
            'turno': aluno['Turno']
        }
        registros_diarios.append(registro_diario)
        # Salva o registro imediatamente
        salvar_registro_diario(registro_diario)

def enviar_telegram(chat_id, nome):
    mensagem = f"O aluno {nome} passou a carteirinha na entrada às {datetime.now().strftime('%H:%M')}"
    params = {'chat_id': chat_id, 'text': mensagem}
    try:
        response = requests.post(TELEGRAM_API_URL, params=params, timeout=5)
        response.raise_for_status()  # Raise an error for bad status codes
        logger.info(f"Mensagem enviada com sucesso: {response.json()}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao enviar para Telegram: {e}")

# Adicione esta linha após criar a instância do Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'registros'
app.config['STATIC_FOLDER'] = 'static'

# Adicione esta rota para servir os arquivos de registro
@app.route('/registros/<path:filename>')
def registros_files(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        mimetype='text/plain'
    )

@app.route('/', methods=['GET', 'POST'])
def index():
    aluno = None
    alerta = False
    erro = False

    if request.method == 'POST':
        codigo = request.form.get('codigo', '')
        aluno = buscar_aluno(codigo)
        
        if aluno:
            if aluno['Permissao'].lower() == 'sim':
                registrar_acesso(
                    aluno['Codigo'],
                    aluno['Nome'],
                    aluno['Turma']
                )
                if aluno['TelegramID']:
                    enviar_telegram(aluno['TelegramID'], aluno['Nome'])
            else:
                alerta = True
        else:
            erro = True

    return render_template('index.html', 
                         aluno=aluno, 
                         alerta=alerta, 
                         erro=erro)

@app.route('/consulta', methods=['GET', 'POST'])
def consulta():
    resultados = []
    termo = ''

    if request.method == 'POST':
        termo = request.form.get('termo', '').lower()
        with open('database.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            resultados = [row for row in reader if (
                termo in row['Nome'].lower() or
                termo == row['Codigo'] or
                termo in row['Turma'].lower()
            )]

    return render_template('consulta.html', 
                         resultados=resultados, 
                         termo=termo)

@app.route('/get_contadores')
def get_contadores():
    # Check if we need to reset counters (new day)
    now = datetime.now()
    if now.hour == 0 and now.minute == 0:
        reset_contadores()
    return {
        'contadores': dict(contadores),
        'total': sum(contadores.values())
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
