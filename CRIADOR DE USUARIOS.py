from werkzeug.security import generate_password_hash
import csv
import tkinter as tk
from tkinter import ttk, messagebox
import os

class CadastroUsuarios:
    def __init__(self, root):
        self.root = root
        self.root.title("Cadastro de Usuários")
        self.root.geometry("400x500")
        
        # Estilo
        style = ttk.Style()
        style.configure('TButton', padding=6)
        style.configure('TLabel', padding=4)
        style.configure('TEntry', padding=4)
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Campos de entrada
        ttk.Label(main_frame, text="Usuário:").grid(row=0, column=0, sticky=tk.W)
        self.username = ttk.Entry(main_frame, width=30)
        self.username.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(main_frame, text="Senha:").grid(row=1, column=0, sticky=tk.W)
        self.password = ttk.Entry(main_frame, width=30, show="*")
        self.password.grid(row=1, column=1, padx=5, pady=5)
        
        # Botão cadastrar
        ttk.Button(main_frame, text="Cadastrar", command=self.adicionar_usuario).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Lista de usuários
        ttk.Label(main_frame, text="Usuários Cadastrados:").grid(row=3, column=0, columnspan=2, sticky=tk.W)
        self.lista_usuarios = ttk.Treeview(main_frame, columns=('Usuario',), height=10)
        self.lista_usuarios.heading('#0', text='')
        self.lista_usuarios.heading('Usuario', text='Usuário')
        self.lista_usuarios.column('#0', width=0, stretch=tk.NO)
        self.lista_usuarios.column('Usuario', width=350)
        self.lista_usuarios.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Carregar usuários existentes
        self.carregar_usuarios()

        # Adicionar botão excluir após a lista de usuários
        ttk.Button(main_frame, text="Excluir Usuário", 
                  command=self.excluir_usuario).grid(row=5, column=0, columnspan=2, pady=10)

    def usuario_existe(self, username):
        if os.path.exists('usuarios.csv'):
            with open('usuarios.csv', 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] == username:
                        return True
        return False

    def adicionar_usuario(self):
        username = self.username.get().strip()
        password = self.password.get().strip()

        if not username or not password:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos!")
            return

        if os.path.exists('usuarios.csv'):
            with open('usuarios.csv', 'r') as file:
                reader = csv.reader(file)
                if username in [row[0] for row in reader]:
                    messagebox.showerror("Erro", "Usuário já existe!")
                    return

        hashed_password = generate_password_hash(password)
        
        with open('usuarios.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([username, hashed_password])
        
        self.username.delete(0, tk.END)
        self.password.delete(0, tk.END)
        
        # Atualizar lista
        self.carregar_usuarios()
        
        messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")

    def carregar_usuarios(self):
        # Limpar lista atual
        for item in self.lista_usuarios.get_children():
            self.lista_usuarios.delete(item)
        
        # Verificar se arquivo existe
        if os.path.exists('usuarios.csv'):
            with open('usuarios.csv', 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row:  # Verifica se a linha não está vazia
                        self.lista_usuarios.insert('', 'end', values=(row[0],))

    def excluir_usuario(self):
        selected_items = self.lista_usuarios.selection()
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione um usuário para excluir!")
            return
            
        if not messagebox.askyesno("Confirmar", "Deseja realmente excluir o usuário?"):
            return
            
        try:
            usuario_selecionado = self.lista_usuarios.item(selected_items[0])['values'][0]
            
            # Ler usuários atuais
            usuarios = []
            with open('usuarios.csv', 'r') as f:
                reader = csv.DictReader(f)
                usuarios = [row for row in reader if row['username'] != usuario_selecionado]
            
            # Reescrever arquivo sem o usuário excluído
            with open('usuarios.csv', 'w', newline='') as f:
                fieldnames = ['username', 'password_hash']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(usuarios)
            
            messagebox.showinfo("Sucesso", "Usuário excluído com sucesso!")
            self.carregar_usuarios()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir usuário: {str(e)}")

if __name__ == '__main__':
    root = tk.Tk()
    app = CadastroUsuarios(root)
    root.mainloop()