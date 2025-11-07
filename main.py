"""Aplicação principal: GUI simples para selecionar arquivos/pastas e converter em JSONs.

Novas funcionalidades:
- OCR para PDFs escaneados
- Conversão PDF para Word
- Limpeza de caracteres especiais
- Saída em múltiplos formatos (JSON, TXT, PDF)

Uso: python main.py
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading
import os
import sys
import logging
from converter import reader, chunker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class App:
    def __init__(self, root):
        self.root = root
        root.title("Conversor para JSON (txt/pdf/docx)")

        frm = tk.Frame(root)
        frm.pack(padx=10, pady=10)

        tk.Button(frm, text="Selecionar arquivos...", command=self.select_files).grid(row=0, column=0, sticky="w")
        tk.Button(frm, text="Selecionar pasta...", command=self.select_folder).grid(row=0, column=1, sticky="w")

        tk.Label(frm, text="Arquivos selecionados:").grid(row=1, column=0, columnspan=2, sticky="w")
        self.listbox = tk.Listbox(frm, width=80, height=8)
        self.listbox.grid(row=2, column=0, columnspan=2)

        tk.Label(frm, text="Pasta de saída:").grid(row=3, column=0, sticky="w")
        self.out_entry = tk.Entry(frm, width=50)
        self.out_entry.grid(row=3, column=1, sticky="w")
        tk.Button(frm, text="Selecionar...", command=self.select_output).grid(row=3, column=2, sticky="w")

        tk.Label(frm, text="Tamanho máximo por JSON (MB):").grid(row=4, column=0, sticky="w")
        self.size_entry = tk.Entry(frm, width=10)
        self.size_entry.insert(0, "50")
        self.size_entry.grid(row=4, column=1, sticky="w")

        self.recursive_var = tk.BooleanVar(value=True)
        tk.Checkbutton(frm, text="Recursivo (quando selecionar pasta)", variable=self.recursive_var).grid(row=5, column=0, columnspan=2, sticky="w")

        self.progress = tk.Label(frm, text="Pronto")
        self.progress.grid(row=6, column=0, columnspan=2, sticky="w")

        tk.Button(frm, text="Converter", command=self.start_conversion).grid(row=7, column=0, pady=8)

        self.files = []

    def select_files(self):
        paths = filedialog.askopenfilenames(title="Selecionar arquivos", filetypes=[
            ("Documentos", "*.txt *.pdf *.docx *.doc"), ("Todos", "*.*")])
        for p in paths:
            if p not in self.files:
                self.files.append(p)
                self.listbox.insert("end", p)

    def select_folder(self):
        folder = filedialog.askdirectory(title="Selecionar pasta")
        if folder:
            self.listbox.insert("end", folder)
            self.files.append(folder)

    def select_output(self):
        out = filedialog.askdirectory(title="Selecionar pasta de saída")
        if out:
            self.out_entry.delete(0, "end")
            self.out_entry.insert(0, out)

    def start_conversion(self):
        try:
            max_mb = float(self.size_entry.get())
            if max_mb <= 0:
                raise ValueError()
        except Exception:
            messagebox.showerror("Erro", "Tamanho inválido. Informe um número positivo (MB).")
            return
        out_dir = self.out_entry.get().strip()
        if not out_dir:
            messagebox.showerror("Erro", "Escolha a pasta de saída.")
            return

        # run in background
        t = threading.Thread(target=self.run_conversion, args=(list(self.files), out_dir, int(max_mb * 1024 * 1024), self.recursive_var.get()))
        t.start()

    def run_conversion(self, inputs, out_dir, max_bytes, recursive):
        self.set_progress("Iniciando...")
        # gather file list
        candidates = []
        for p in inputs:
            pth = Path(p)
            if pth.is_dir():
                if recursive:
                    for fp in pth.rglob("*"):
                        if fp.is_file() and reader.is_supported(str(fp)):
                            candidates.append(str(fp))
                else:
                    for fp in pth.iterdir():
                        if fp.is_file() and reader.is_supported(str(fp)):
                            candidates.append(str(fp))
            elif pth.is_file():
                if reader.is_supported(str(pth)):
                    candidates.append(str(pth))

        if not candidates:
            self.set_progress("Nenhum arquivo suportado encontrado.")
            return

        docs = []
        total = len(candidates)
        for i, fp in enumerate(candidates, 1):
            try:
                self.set_progress(f"Lendo ({i}/{total}): {fp}")
                text = reader.extract_text(fp)
            except Exception as e:
                logger.exception("Erro lendo %s", fp)
                # registrar como aviso e pular
                continue
            docs.append({
                "source_path": str(fp),
                "filename": Path(fp).name,
                "filetype": Path(fp).suffix.lower().lstrip('.'),
                "text": text,
            })

        self.set_progress("Gerando JSONs...")
        try:
            chunker.chunk_and_write(docs, Path(out_dir), max_bytes)
            self.set_progress("Concluído.")
            messagebox.showinfo("Sucesso", "Conversão concluída com sucesso.")
        except Exception as e:
            logger.exception("Erro durante chunking")
            messagebox.showerror("Erro", f"Erro durante escrita: {e}")
            self.set_progress("Erro")

    def set_progress(self, text):
        def upd():
            self.progress.config(text=text)
        self.root.after(0, upd)


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
