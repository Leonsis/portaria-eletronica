# Portaria Eletrônica

Sistema de controle de acesso e gerador de carteirinha para instituições de ensino com integração ao Telegram.
Desenvolvido totalmente em Python e HTML.

<img src="https://github.com/gordaoescolas/portaria-eletronica/blob/main/screenshot01.png?raw=true" width="300" height="300"> <img src="https://github.com/gordaoescolas/portaria-eletronica/blob/main/screenshot02.png?raw=true" width="300" height="300"> <img src="https://github.com/gordaoescolas/portaria-eletronica/blob/main/screenshot3.png?raw=true" width="300" height="300"> <img src="https://github.com/gordaoescolas/portaria-eletronica/blob/main/screenshot4.png?raw=true" width="300" height="300"> <img src="https://github.com/gordaoescolas/portaria-eletronica/blob/main/screenshot5.png?raw=true" width="300" height="300"> <img src="https://github.com/gordaoescolas/portaria-eletronica/blob/main/screenshot06.png?raw=true" width="300" height="300">

## Vídeo de Demonstração
[![Vídeo de demonstração](https://github.com/gordaoescolas/portaria-eletronica/blob/main/youtube-thumb.jpg?raw=true)](https://youtu.be/_QDIDinA-3Y)

https://youtu.be/_QDIDinA-3Y
## Funcionalidades Principais

✅ **Registro de Presença:**
- Leitura de carteirinhas com código de barras
- Verificação instantânea de permissão
- Alertas visuais e sonoros para acesso negado
- Geração automática de relatórios em TXT

📊 **Painel de Controle:**
- Cadastro/Edição/Exclusão de alunos
- Upload de fotos dos alunos
- Gerenciamento de permissões
- Vinculação de ID do Telegram

🆔 **Carteirinha:**
- Gerador de carteirinha escolar
- Totalmente integrado com o serviço de portaria
- Permite imprimir em lotes ou individuais

📲 **Integração com Telegram:**
- Notificações instantâneas de acesso
- Configuração simplificada de IDs
- Mensagens personalizáveis

## Tecnologias Utilizadas

- **Frontend:** HTML5, CSS3
- **Backend:** Python (Flask)
- **Banco de Dados:** CSV
- **Integração:** Telegram Bot API
- **Outras:** Werkzeug (upload de arquivos)

## Instalação

### 1. **Pré-requisitos:**
   - Python 3.8+
   - Conta no Telegram

### 2. **Baixe o arquivo ZIP:**
   - Ele está localizado na aba "Releases"

### 3. **Mudar imagem da assinatura e logo:**
   - Basta abrir o "MUDAR ASSINATURA E LOGO.py" que poderá alterar de forma gráfica
   - Caso dê algum problema, você pode alterar de forma manual na pasta "static" e inserindo os arquivos "assinatura.png" e "logo.svg"
   - A assinatura DEVE estar em formato PNG, enquanto que a logo DEVE estar em formato SVG, de tamanho 156x56.

### 4. **Trocar informações em templates/carteirinha_template.html:**
   - Nas linhas 92, 93 e 94, terão as informações da escola. Altere manualmente para que fique nesse modelo:
      ```bash
      <p>NOME DA SUA ESCOLA</p>
      <p>Telefone: 123456789</p>
      <p>www.sitedaescola.com.br</p>
      ```

### 5. **Instalar dependências:**
   ```bash
   pip install Flask Werkzeug python-barcode Pillow requests python-dotenv Flask-Login
   ```
   ou
   ```bash
   pip install -r requirements.txt
   ```

### 6. **Configurar ambiente:**
   - Crie um bot no Telegram usando o BotFather
   - Cole o token recebido no arquivo `INSERIR TOKEN TELEGRAM.py`

### 7. **Crie um usuário:**
   - Por padrão, para acessar o painel administrativo, ele virá com usuário e senha `admin/admin`
   - Devido ser uma senha comum, recomendo mudar a senha o quanto antes
   - Para gerenciar novos usuários, use o arquivo `CRIADOR DE USUÁRIOS.py`

## Como Executar

### **Para executar todos os servidores:**
```bash
python "EXECUTAR SERVIDOR.py"
```

### **Painel de Registro de Presença e Consulta de Acessos (Porta 5000):**
```bash
python app.py
```

### **Painel Administrativo (Porta 5010):**
```bash
python upload.py
```

### **Painel de Emissão de Carteirinha (Porta 5020):**
```bash
python carteirinha.py
```


### **Acesse no navegador:**
- **Interface de Portaria:** [http://localhost:5000](http://localhost:5000)
- **Painel Administrativo:** [http://localhost:5010](http://localhost:5010)
- **Painel de Emissão de Carteirinha:** [http://localhost:5020](http://localhost:5020)

### **Você também pode utilizá-lo em uma VPS**
**(para execução em rede, trocar localhost pelo IP do dispositivo onde está rodando o servidor)**

## Estrutura de Arquivos

```
portaria-eletronica/
├── app.py               # Aplicação principal
├── upload.py            # Painel administrativo
├── database.csv         # Banco de dados
├── requirements.txt     # Dependências
├── registros/           # Históricos de acesso
├── static/
│   ├── fotos/           # Fotos dos alunos
│   ├── style.css        # Estilos
│   └── alert.mp3        # Som de alerta
└── templates/
    ├── (arquivos .html) # Templates das interfaces
```

## Configuração do Banco de Dados

O arquivo `database.csv` deve seguir este formato:

```csv
Nome,Codigo,Turma,Turno,Permissao,Foto,TelegramID
João Silva,123456,A1,Manhã,Sim,foto.jpg,123456789
```

## Personalização

### **Telegram:**
- Edite a mensagem no arquivo `app.py` (linha 34):
  ```python
  mensagem = f"O aluno {nome} passou a carteirinha às {datetime.datetime.now().strftime('%H:%M')}"
  ```

### **Interface:**
- Modifique o arquivo `static/style.css` para alterar o visual
- Adicione novos sons em `static/`

## Troubleshooting

| Problema Comum | Solução |
|---------------|-----------|
| Erro 404 nas fotos | Verifique se o diretório `static/fotos` está disponível  |
| Acesso negado sem motivo | Checar permissão no CSV (coluna 'Permissao') |
| Telegram não envia mensagens | Certifique-se de que o token do seu bot está devidamente configurado, além do ID estar devidamente cadastrado |
| Arquivos TXT não são gerados | Verificar permissões na pasta `registros/` |

## Licença

Distribuído sob Licença de Uso Livre Não Comercial. Veja `LICENSE` para mais informações.

Desenvolvido por Gordão Escolas - 🔗 [Repositório GitHub](https://github.com/gordaoescolas/portaria-eletronica)

