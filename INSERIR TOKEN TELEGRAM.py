import tkinter as tk
from tkinter import messagebox

def salvar_token():
    novo_token = entry_token.get()
    if novo_token:
        with open('app.py', 'r', encoding='utf-8') as file:
            linhas = file.readlines()
        
        with open('app.py', 'w', encoding='utf-8') as file:
            for linha in linhas:
                if linha.startswith("TELEGRAM_TOKEN"):
                    file.write(f"TELEGRAM_TOKEN = '{novo_token}'\n")
                else:
                    file.write(linha)
        
        messagebox.showinfo("Sucesso", "Token atualizado com sucesso!")
        entry_token.delete(0, tk.END)
    else:
        messagebox.showwarning("Atenção", "Por favor, insira um token.")

app = tk.Tk()
app.title("Atualizar Token do Telegram")

label_token = tk.Label(app, text="Insira o novo Token do Telegram:")
label_token.pack(pady=10)

entry_token = tk.Entry(app, width=50)
entry_token.pack(pady=5)

botao_salvar = tk.Button(app, text="Salvar Token", command=salvar_token)
botao_salvar.pack(pady=20)

app.mainloop()
