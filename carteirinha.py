from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import check_password_hash
import csv
import barcode
from barcode.codex import Code128
from barcode.writer import ImageWriter
from datetime import datetime
import os
import logging

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB

# Adicione estas linhas no início do arquivo carteirinha.py, após os imports existentes
login_manager = LoginManager()
app.secret_key = 'supersecretkey'  # mesma chave usada no upload.py
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def verificar_usuario(username, password):
    with open('usuarios.csv', 'r') as f:
        reader = csv.DictReader(f)
        for user in reader:
            if user['username'] == username:
                if check_password_hash(user['password_hash'], password):
                    return True
    return False

# Configurações da instituição
CONFIG = {
    'escola': 'Escola Novo Futuro',
    'telefone': '(61) 1234-4567',
    'validade': '31/12/2025',
    'assinatura': 'assinatura.png'
}

# Configurações do código de barras
BARCODE_SETTINGS = {
    'module_width': 0.3,
    'module_height': 15,
    'font_size': 12,
    'text_distance': 1,
    'quiet_zone': 5
}

def buscar_aluno(codigo):
    try:
        with open('database.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Codigo'] == codigo.strip():
                    return row
        return None
    except Exception as e:
        logger.error(f"Erro ao ler database: {str(e)}")
        return None

def buscar_turma(turma):
    try:
        alunos = []
        with open('database.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Turma'].lower() == turma.lower():
                    alunos.append(row)
        return alunos
    except Exception as e:
        logger.error(f"Erro ao buscar turma: {str(e)}")
        return []

def gerar_codigo_barras(codigo):
    try:
        # Garantir código com 9 dígitos
        codigo_formatado = codigo.zfill(9)
        
        # Criar diretório se não existir
        caminho_barcode = os.path.join(app.config['UPLOAD_FOLDER'], 'barcodes')
        os.makedirs(caminho_barcode, exist_ok=True)
        
        # Nome do arquivo final
        arquivo_final = os.path.join(caminho_barcode, f"{codigo_formatado}.png")
        
        # Verificar se já existe
        if not os.path.exists(arquivo_final):
            # Usar Code128
            code128 = barcode.Code128(
                codigo_formatado,
                writer=ImageWriter()
            )
            
            # Salvar imagem com configurações
            code128.save(
                os.path.join(caminho_barcode, codigo_formatado),
                BARCODE_SETTINGS
            )
        
        return arquivo_final
    except Exception as e:
        logger.error(f"Erro na geração do código de barras: {str(e)}")
        return None

# Modifique a rota raiz para exigir login
@app.route('/')
@login_required
def index():
    try:
        turmas = set()
        with open('database.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                turmas.add(row['Turma'])
        return render_template('carteirinha_index.html', 
                            turmas=sorted(turmas), 
                            config=CONFIG)
    except Exception as e:
        return render_template('erro.html', 
                            mensagem=f"Erro ao carregar dados: {str(e)}")

@app.route('/emitir', methods=['POST'])
def emitir():
    try:
        tipo_emissao = request.form.get('tipo_emissao')
        data_emissao = datetime.now().strftime("%d/%m/%Y")
        
        if not tipo_emissao:
            return render_template('erro.html', 
                                mensagem="Tipo de emissão não especificado!")

        if tipo_emissao == 'unitaria':
            codigo = request.form.get('codigo', '').strip()
            if not codigo:
                return render_template('erro.html', 
                                    mensagem="Código não informado!")
            
            aluno = buscar_aluno(codigo)
            if not aluno:
                return render_template('erro.html', 
                                    mensagem=f"Código {codigo} não encontrado!")
            
            # Gera código de barras
            barcode_path = gerar_codigo_barras(aluno['Codigo'])
            if not barcode_path:
                return render_template('erro.html', 
                                    mensagem="Erro ao gerar código de barras!")
            
            aluno.update({
                'barcode': os.path.basename(barcode_path),
                'data_emissao': data_emissao,
                **CONFIG
            })
            return render_template('carteirinha_template.html', 
                                alunos=[aluno])

        elif tipo_emissao == 'turma':
            turma = request.form.get('turma', '').strip()
            if not turma:
                return render_template('erro.html', 
                                    mensagem="Turma não informada!")
            
            alunos = buscar_turma(turma)
            if not alunos:
                return render_template('erro.html', 
                                    mensagem=f"Turma {turma} não encontrada!")
            
            # Processa todos os alunos da turma
            for aluno in alunos:
                barcode_path = gerar_codigo_barras(aluno['Codigo'])
                aluno.update({
                    'barcode': os.path.basename(barcode_path) if barcode_path else '',
                    'data_emissao': data_emissao,
                    **CONFIG
                })
            
            return render_template('carteirinha_template.html', 
                                alunos=alunos)

        else:
            return render_template('erro.html', 
                                mensagem="Tipo de emissão inválido!")

    except Exception as e:
        logger.error(f"Erro crítico: {str(e)}")
        return render_template('erro.html', 
                            mensagem=f"Erro interno: {str(e)}")

# Adicione as rotas de login/logout
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if verificar_usuario(username, password):
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        
        return render_template('login_carteirinha.html', error="Credenciais inválidas!")
    
    return render_template('login_carteirinha.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'barcodes'), exist_ok=True)
    app.run(host='0.0.0.0', port=5020, debug=False)