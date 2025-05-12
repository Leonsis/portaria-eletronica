from flask import Flask, render_template, request, redirect, url_for, g
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import csv
import os
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/fotos'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['DATABASE'] = 'database.csv'
app.secret_key = 'supersecretkey'
app.secret_key = 'sua_chave_secreta_muito_forte_aqui'

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.before_request
def before_request():
    g.user = current_user

# Função para verificar credenciais
def verificar_usuario(username, password):
    with open('usuarios.csv', 'r') as f:
        reader = csv.DictReader(f)
        for user in reader:
            if user['username'] == username:
                if check_password_hash(user['password_hash'], password):
                    return True
    return False

# Rotas de autenticação
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if verificar_usuario(username, password):
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        
        return render_template('login.html', error="Credenciais inválidas!")
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def read_database():
    with open(app.config['DATABASE'], 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def write_database(data):
    with open(app.config['DATABASE'], 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

@app.route('/')
@login_required
def index():
    alunos = read_database()
    return render_template('upload_index.html', alunos=alunos)

@app.route('/editar/<codigo>', methods=['GET', 'POST'])
@login_required
def editar(codigo):
    alunos = read_database()
    aluno = next((a for a in alunos if a['Codigo'] == codigo), None)
    
    if request.method == 'POST':
        # Atualizar dados
        aluno['Nome'] = request.form['nome']
        aluno['Turma'] = request.form['turma']
        aluno['Turno'] = request.form['turno']
        aluno['Permissao'] = request.form['permissao']
        aluno['TelegramID'] = request.form['telegramid']
        
        # Processar upload da foto
        if 'foto' in request.files:
            file = request.files['foto']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                aluno['Foto'] = filename
        
        write_database(alunos)
        return redirect(url_for('index'))
    
    return render_template('upload_editar.html', aluno=aluno)

@app.route('/excluir/<codigo>')
@login_required
def excluir(codigo):
    alunos = read_database()
    alunos = [a for a in alunos if a['Codigo'] != codigo]
    write_database(alunos)
    return redirect(url_for('index'))

@app.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if request.method == 'POST':
        novo_aluno = {
            'Nome': request.form['nome'],
            'Codigo': request.form['codigo'],
            'Turma': request.form['turma'],
            'Turno': request.form['turno'],
            'Permissao': request.form['permissao'],
            'Foto': 'semfoto.jpg',
            'TelegramID': request.form['telegramid']
        }
        
        # Processar upload da foto
        if 'foto' in request.files:
            file = request.files['foto']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                novo_aluno['Foto'] = filename
        
        alunos = read_database()
        alunos.append(novo_aluno)
        write_database(alunos)
        return redirect(url_for('index'))
    
    return render_template('upload_novo.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True)
