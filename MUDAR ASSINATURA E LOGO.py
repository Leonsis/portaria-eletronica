import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Alterar Logo e Assinatura")
        self.root.geometry("600x300")

        # Avisos
        tk.Label(root, text="ATENÇÃO:", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Label(root, text="- Para a assinatura na parte traseira, o arquivo DEVE estar em PNG!").pack()
        tk.Label(root, text="- Para a logo na parte frontal, o arquivo DEVE estar em SVG no tamanho 156x56!").pack()
        
        # Botões
        tk.Button(root, text="Selecionar Nova Assinatura (PNG)", 
                 command=self.mudar_assinatura).pack(pady=20)
        tk.Button(root, text="Selecionar Nova Logo (SVG)", 
                 command=self.mudar_logo).pack(pady=20)

    def mudar_assinatura(self):
        arquivo = filedialog.askopenfilename(
            filetypes=[("Arquivos PNG", "*.png")]
        )
        if arquivo:
            if not arquivo.lower().endswith('.png'):
                messagebox.showerror("Erro", "O arquivo deve ser PNG!")
                return
            try:
                shutil.copy2(arquivo, "static/assinatura.png")
                messagebox.showinfo("Sucesso", "Assinatura alterada com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao copiar arquivo: {str(e)}")

    def mudar_logo(self):
        arquivo = filedialog.askopenfilename(
            filetypes=[("Arquivos SVG", "*.svg")]
        )
        if arquivo:
            if not arquivo.lower().endswith('.svg'):
                messagebox.showerror("Erro", "O arquivo deve ser SVG!")
                return
            try:
                shutil.copy2(arquivo, "static/logo.svg")
                messagebox.showinfo("Sucesso", "Logo alterada com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao copiar arquivo: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()