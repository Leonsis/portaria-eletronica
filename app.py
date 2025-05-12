import logging
import csv
import os
import requests
from collections import defaultdict
from datetime import datetime, timedelta
from flask import Flask, render_template, request, send_from_directory

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Iniciando o aplicativo Flask")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'registros'
app.config['STATIC_FOLDER'] = 'static'

TELEGRAM_TOKEN = '452429006:AAHfFItKogarQKTQftX5eNC05n86-155CgQ'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'

TURNOS = ['Manhã', 'Tarde', 'Noite']
contadores = defaultdict(int)
registros_diarios = []
ultimo_registro = {}  # Dicionário para rastrear o último registro de cada aluno
COOLDOWN_MINUTES = 5  # Tempo mínimo entre registros (em minutos)

def reset_contadores():
    """Reseta os contadores à meia-noite e salva os registros do dia anterior."""
    global contadores, registros_diarios
    contadores.clear()
    if registros_diarios:
        data = datetime.now().strftime("%Y-%m-%d")
        pasta_registros = 'registros_diarios'
        os.makedirs(pasta_registros, exist_ok=True)
        
        arquivo = os.path.join(pasta_registros, f"{data}.csv")
        with open(arquivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['codigo', 'turno', 'data/hora', 'tipo'])
            writer.writeheader()
            for registro in registros_diarios:
                writer.writerow({
                    'codigo': registro['codigo'],
                    'turno': registro['turno'],
                    'data/hora': f"{datetime.now().strftime('%Y-%m-%d')} {registro['hora']}",
                    'tipo': registro['tipo']
                })
    registros_diarios.clear()

def salvar_registro_diario(registro):
    """Salva o registro no arquivo CSV do dia atual."""
    data = datetime.now().strftime("%Y-%m-%d")
    pasta_registros = 'registros_diarios'
    os.makedirs(pasta_registros, exist_ok=True)
    
    arquivo = os.path.join(pasta_registros, f"{data}.csv")
    arquivo_existe = os.path.exists(arquivo)
    
    with open(arquivo, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['codigo', 'turno', 'data/hora', 'tipo'])
        if not arquivo_existe:
            writer.writeheader()
        writer.writerow({
            'codigo': registro['codigo'],
            'turno': registro['turno'],
            'data/hora': f"{datetime.now().strftime('%Y-%m-%d')} {registro['hora']}",
            'tipo': registro['tipo']
        })

def buscar_aluno(codigo):
    """Busca um aluno no arquivo database.csv pelo código."""
    try:
        with open('database.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Codigo'] == codigo.strip():
                    return row
    except FileNotFoundError:
        logger.error("Arquivo database.csv não encontrado.")
    return None

def registrar_acesso(codigo, nome, turma, tipo_acesso):
    """Registra o acesso (entrada ou saída) no arquivo TXT."""
    now = datetime.now()
    data_hora = now.strftime("%d/%m/%Y %H:%M:%S")
    registro = f"{data_hora} - {tipo_acesso}"
    
    pasta_turma = os.path.join(app.config['UPLOAD_FOLDER'], turma)
    os.makedirs(pasta_turma, exist_ok=True)
        
    arquivo_path = os.path.join(pasta_turma, f"{codigo}.txt")
    arquivo_existe = os.path.exists(arquivo_path)
    
    with open(arquivo_path, 'a', encoding='utf-8') as f:
        if not arquivo_existe:
            aluno = buscar_aluno(codigo)
            f.write(f"Nome: {nome}\n")
            f.write(f"Turma: {turma}\n")
            f.write(f"Turno: {aluno['Turno']}\n")
            f.write(f"Código: {codigo}\n")
            f.write("\nREGISTRO DE ACESSOS:\n")
            f.write("-" * 30 + "\n")
        f.write(f"{registro}\n")
    
    aluno = buscar_aluno(codigo)
    if aluno:
        contadores[aluno['Turno']] += 1
        registro_diario = {
            'hora': now.strftime("%H:%M:%S"),
            'codigo': codigo,
            'turno': aluno['Turno'],
            'tipo': tipo_acesso
        }
        registros_diarios.append(registro_diario)
        salvar_registro_diario(registro_diario)

def enviar_telegram(chat_id, nome, tipo_acesso):
    """Envia mensagem ao Telegram indicando entrada ou saída."""
    mensagem = f"O aluno {nome} registrou {'entrada' if tipo_acesso == 'Entrada' else 'saída'} às {datetime.now().strftime('%H:%M')}"
    params = {'chat_id': chat_id, 'text': mensagem}
    try:
        response = requests.post(TELEGRAM_API_URL, params=params, timeout=5)
        response.raise_for_status()
        logger.info(f"Mensagem enviada com sucesso: {response.json()}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao enviar para Telegram: {e}")

@app.route('/registros/<path:filename>')
def registros_files(filename):
    """Serve os arquivos de registro."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, mimetype='text/plain')

@app.route('/', methods=['GET', 'POST'])
def index():
    """Rota principal para registrar acessos."""
    mensagem = ""
    aluno = None
    alerta = False
    erro = False

    if request.method == 'POST':
        codigo = request.form.get('codigo', '')
        aluno = buscar_aluno(codigo)
        
        if aluno:
            if aluno['Permissao'].lower() == 'sim':
                now = datetime.now()
                ultimo = ultimo_registro.get(codigo)
                if ultimo and (now - ultimo['hora']) < timedelta(minutes=COOLDOWN_MINUTES):
                    mensagem = "⏳ Aguarde antes de registrar novamente."
                else:
                    tipo_acesso = 'Entrada' if ultimo is None or ultimo['tipo'] == 'Saída' else 'Saída'
                    registrar_acesso(aluno['Codigo'], aluno['Nome'], aluno['Turma'], tipo_acesso)
                    if aluno['TelegramID']:
                        enviar_telegram(aluno['TelegramID'], aluno['Nome'], tipo_acesso)
                    ultimo_registro[codigo] = {'hora': now, 'tipo': tipo_acesso}
                    mensagem = f"✅ {tipo_acesso} registrada com sucesso!"
            else:
                alerta = True
                mensagem = "⛔ Acesso Negado!"
        else:
            erro = True
            mensagem = "⚠️ Código não encontrado!"

    return render_template('index.html', 
                           mensagem=mensagem, 
                           aluno=aluno, 
                           alerta=alerta, 
                           erro=erro)

@app.route('/consulta', methods=['GET', 'POST'])
def consulta():
    """Rota para consulta de alunos."""
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
    return render_template('consulta.html', resultados=resultados, termo=termo)

@app.route('/get_contadores')
def get_contadores():
    """Retorna os contadores de acessos."""
    now = datetime.now()
    if now.hour == 0 and now.minute == 0:
        reset_contadores()
    return {'contadores': dict(contadores), 'total': sum(contadores.values())}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)