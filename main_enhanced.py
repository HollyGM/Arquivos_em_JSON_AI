"""Aplicação principal: GUI avançada para conversão de documentos.

Novas funcionalidades:
- OCR para PDFs escaneados
- Conversão PDF para Word
- Limpeza de caracteres especiais
- Saída em múltiplos formatos (JSON, TXT, PDF)

Uso: python main_enhanced.py
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading
import os
import sys
import logging
from converter import reader, chunker
from converter import file_utils

logging.basicConfig(level=logging.INFO, filename='gui_debug.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnhancedApp:
    def __init__(self, root):
        self.root = root
        root.title("Conversor Avançado (JSON/TXT/PDF/Word + OCR)")
        root.geometry("700x600")

        # Criar notebook para abas
        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Aba principal - Conversão para JSON
        self.main_frame = ttk.Frame(notebook)
        notebook.add(self.main_frame, text="Conversão para JSON")
        self.setup_main_tab()

        # Aba de conversão PDF para Word
        self.pdf_word_frame = ttk.Frame(notebook)
        notebook.add(self.pdf_word_frame, text="PDF para Word")
        self.setup_pdf_word_tab()

        # Aba de conversão de formatos de saída
        self.output_frame = ttk.Frame(notebook)
        notebook.add(self.output_frame, text="Converter Saídas")
        self.setup_output_tab()

        self.files = []

    def setup_main_tab(self):
        """Configura a aba principal de conversão para JSON"""
        frm = self.main_frame

        # Seleção de arquivos
        file_frame = ttk.LabelFrame(frm, text="Seleção de Arquivos")
        file_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(file_frame, text="Selecionar arquivos...", command=self.select_files).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(file_frame, text="Selecionar pasta...", command=self.select_folder).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(file_frame, text="Limpar Lista", command=self.clear_files).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Label(frm, text="Arquivos selecionados:").pack(anchor=tk.W, padx=5)
        self.listbox = tk.Listbox(frm, width=80, height=8)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configurações de saída
        output_config_frame = ttk.LabelFrame(frm, text="Configurações de Saída")
        output_config_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(output_config_frame, text="Pasta de saída:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.out_entry = ttk.Entry(output_config_frame, width=50)
        self.out_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(output_config_frame, text="Selecionar...", command=self.select_output).grid(row=0, column=2, padx=5, pady=2)

        ttk.Label(output_config_frame, text="Tamanho máximo por JSON (MB):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.size_entry = ttk.Entry(output_config_frame, width=10)
        self.size_entry.insert(0, "50")
        self.size_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        output_config_frame.columnconfigure(1, weight=1)

        # Opções de processamento
        options_frame = ttk.LabelFrame(frm, text="Opções de Processamento")
        options_frame.pack(fill=tk.X, padx=5, pady=5)

        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Recursivo (quando selecionar pasta)", variable=self.recursive_var).pack(anchor=tk.W, padx=5, pady=2)

        self.use_ocr_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Usar OCR para PDFs escaneados", variable=self.use_ocr_var).pack(anchor=tk.W, padx=5, pady=2)

        self.clean_chars_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Limpar caracteres especiais", variable=self.clean_chars_var).pack(anchor=tk.W, padx=5, pady=2)

        # Formatos de saída
        output_formats_frame = ttk.LabelFrame(frm, text="Formatos de Saída Adicionais")
        output_formats_frame.pack(fill=tk.X, padx=5, pady=5)

        formats_inner = ttk.Frame(output_formats_frame)
        formats_inner.pack(fill=tk.X, padx=5, pady=5)

        self.output_txt_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(formats_inner, text="TXT", variable=self.output_txt_var).pack(side=tk.LEFT, padx=10)

        self.output_pdf_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(formats_inner, text="PDF", variable=self.output_pdf_var).pack(side=tk.LEFT, padx=10)

        # Progress e controles
        self.progress = ttk.Label(frm, text="Pronto")
        self.progress.pack(anchor=tk.W, padx=5, pady=5)

        ttk.Button(frm, text="Converter", command=self.start_conversion).pack(pady=10)

    def setup_pdf_word_tab(self):
        """Configura a aba de conversão PDF para Word"""
        frm = self.pdf_word_frame

        # Seleção de PDFs
        pdf_file_frame = ttk.LabelFrame(frm, text="Seleção de PDFs")
        pdf_file_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(pdf_file_frame, text="Selecionar PDFs...", command=self.select_pdf_files).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(pdf_file_frame, text="Limpar Lista", command=self.clear_pdf_files).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Label(frm, text="PDFs selecionados:").pack(anchor=tk.W, padx=5)
        self.pdf_listbox = tk.Listbox(frm, width=80, height=8)
        self.pdf_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configurações de conversão PDF->Word
        pdf_config_frame = ttk.LabelFrame(frm, text="Configurações de Conversão")
        pdf_config_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(pdf_config_frame, text="Pasta de saída:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.pdf_out_entry = ttk.Entry(pdf_config_frame, width=50)
        self.pdf_out_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(pdf_config_frame, text="Selecionar...", command=self.select_pdf_output).grid(row=0, column=2, padx=5, pady=2)

        self.pdf_use_ocr_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(pdf_config_frame, text="Forçar uso de OCR", variable=self.pdf_use_ocr_var).grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=2)

        self.pdf_clean_chars_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(pdf_config_frame, text="Limpar caracteres especiais", variable=self.pdf_clean_chars_var).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=2)

        pdf_config_frame.columnconfigure(1, weight=1)

        # Progress e controles
        self.pdf_progress = ttk.Label(frm, text="Pronto")
        self.pdf_progress.pack(anchor=tk.W, padx=5, pady=5)

        ttk.Button(frm, text="Converter para Word", command=self.start_pdf_to_word).pack(pady=10)

        self.pdf_files = []

    def setup_output_tab(self):
        """Configura a aba de conversão de formatos de saída"""
        frm = self.output_frame

        # Seleção de JSONs
        json_frame = ttk.LabelFrame(frm, text="Converter JSONs para outros formatos")
        json_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(json_frame, text="Selecionar pasta com JSONs...", command=self.select_json_folder).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Label(frm, text="Pasta de JSONs:").pack(anchor=tk.W, padx=5)
        self.json_folder_entry = ttk.Entry(frm, width=60)
        self.json_folder_entry.pack(fill=tk.X, padx=5, pady=2)

        # Configurações de conversão
        convert_config_frame = ttk.LabelFrame(frm, text="Configurações de Conversão")
        convert_config_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(convert_config_frame, text="Pasta de saída:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.convert_out_entry = ttk.Entry(convert_config_frame, width=50)
        self.convert_out_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(convert_config_frame, text="Selecionar...", command=self.select_convert_output).grid(row=0, column=2, padx=5, pady=2)

        ttk.Label(convert_config_frame, text="Formato de saída:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.format_var = tk.StringVar(value="txt")
        format_frame = ttk.Frame(convert_config_frame)
        format_frame.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        ttk.Radiobutton(format_frame, text="TXT", variable=self.format_var, value="txt").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(format_frame, text="PDF", variable=self.format_var, value="pdf").pack(side=tk.LEFT, padx=5)

        convert_config_frame.columnconfigure(1, weight=1)

        # Progress e controles
        self.convert_progress = ttk.Label(frm, text="Pronto")
        self.convert_progress.pack(anchor=tk.W, padx=5, pady=5)

        ttk.Button(frm, text="Converter", command=self.start_format_conversion).pack(pady=10)

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

    def clear_files(self):
        self.files.clear()
        self.listbox.delete(0, tk.END)

    def select_output(self):
        out = filedialog.askdirectory(title="Selecionar pasta de saída")
        if out:
            self.out_entry.delete(0, "end")
            self.out_entry.insert(0, out)

    def select_pdf_files(self):
        paths = filedialog.askopenfilenames(title="Selecionar PDFs", filetypes=[
            ("PDF", "*.pdf"), ("Todos", "*.*")])
        for p in paths:
            if p not in self.pdf_files:
                self.pdf_files.append(p)
                self.pdf_listbox.insert("end", p)

    def clear_pdf_files(self):
        self.pdf_files.clear()
        self.pdf_listbox.delete(0, tk.END)

    def select_pdf_output(self):
        out = filedialog.askdirectory(title="Selecionar pasta de saída para Word")
        if out:
            self.pdf_out_entry.delete(0, "end")
            self.pdf_out_entry.insert(0, out)

    def select_json_folder(self):
        folder = filedialog.askdirectory(title="Selecionar pasta com JSONs")
        if folder:
            self.json_folder_entry.delete(0, "end")
            self.json_folder_entry.insert(0, folder)

    def select_convert_output(self):
        out = filedialog.askdirectory(title="Selecionar pasta de saída para conversão")
        if out:
            self.convert_out_entry.delete(0, "end")
            self.convert_out_entry.insert(0, out)

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
        t = threading.Thread(target=self.run_conversion, args=(
            list(self.files), out_dir, int(max_mb * 1024 * 1024), 
            self.recursive_var.get(), self.use_ocr_var.get(), 
            self.clean_chars_var.get(), self.output_txt_var.get(), 
            self.output_pdf_var.get()
        ))
        t.start()

    def start_pdf_to_word(self):
        if not self.pdf_files:
            messagebox.showerror("Erro", "Selecione pelo menos um arquivo PDF.")
            return
        
        out_dir = self.pdf_out_entry.get().strip()
        if not out_dir:
            messagebox.showerror("Erro", "Escolha a pasta de saída.")
            return

        t = threading.Thread(target=self.run_pdf_to_word, args=(
            list(self.pdf_files), out_dir, 
            self.pdf_use_ocr_var.get(), self.pdf_clean_chars_var.get()
        ))
        t.start()

    def start_format_conversion(self):
        json_folder = self.json_folder_entry.get().strip()
        if not json_folder:
            messagebox.showerror("Erro", "Selecione a pasta com arquivos JSON.")
            return
        
        out_dir = self.convert_out_entry.get().strip()
        if not out_dir:
            messagebox.showerror("Erro", "Escolha a pasta de saída.")
            return

        t = threading.Thread(target=self.run_format_conversion, args=(
            json_folder, out_dir, self.format_var.get()
        ))
        t.start()

    def run_conversion(self, inputs, out_dir, max_bytes, recursive, use_ocr, clean_chars, output_txt, output_pdf):
        self.set_progress("Iniciando...")
        logger.info(f"Inputs: {inputs}")
        logger.info(f"Out dir: {out_dir}")
        logger.info(f"Max bytes: {max_bytes}")
        logger.info(f"Recursive: {recursive}")
        logger.info(f"Use OCR: {use_ocr}")
        logger.info(f"Clean chars: {clean_chars}")
        
        # Gather file list using utility function
        candidates = file_utils.collect_files(inputs, recursive)
        
        logger.info(f"Candidates found: {candidates}")
        if not candidates:
            self.set_progress("Nenhum arquivo suportado encontrado.")
            return

        # Process files using utility function
        errors = []
        
        def progress_callback(i, total, fp):
            self.set_progress(f"Lendo ({i}/{total}): {fp}")
            logger.info(f"Reading file: {fp}")
        
        try:
            docs = file_utils.process_files_to_docs(
                candidates,
                use_ocr=use_ocr,
                clean_special_chars=clean_chars,
                progress_callback=progress_callback
            )
        except Exception as e:
            logger.exception("Erro processando arquivos")
            errors.append(f"Erro geral: {e}")
            docs = []
        
        # Track individual file errors if needed
        logger.info(f"Text length: {len(docs[0]['text']) if docs else 0}")

        logger.info(f"Docs prepared: {len(docs)}")
        if not docs:
            self.set_progress("Nenhum documento foi processado com sucesso.")
            error_msg = "Nenhum documento foi processado. Verifique os arquivos e configurações de OCR."
            if errors:
                joined = "\n".join(errors[:5])
                error_msg += f"\n\nFalhas detectadas:\n{joined}"
                if len(errors) > 5:
                    error_msg += "\n..."
            messagebox.showerror("Erro", error_msg)
            return

        self.set_progress("Gerando JSONs...")
        try:
            json_files = chunker.chunk_and_write(docs, Path(out_dir), max_bytes)
            logger.info(f"JSONs written to {out_dir}: {json_files}")
            summary_lines = [f"{len(json_files)} arquivo(s) JSON gerados em {out_dir}"]
            
            # Gerar formatos adicionais se solicitado
            if output_txt or output_pdf:
                self.set_progress("Gerando formatos adicionais...")
                try:
                    from converter.output_formats import convert_json_files
                    txt_paths = []
                    pdf_paths = []
                    if output_txt:
                        txt_dir = Path(out_dir) / 'txt_output'
                        txt_paths = convert_json_files(out_dir, 'txt', txt_dir, json_files=json_files)
                        if txt_paths:
                            summary_lines.append(f"{len(txt_paths)} arquivo(s) TXT em {txt_dir}")
                        logger.info("TXT generated")

                    if output_pdf:
                        pdf_dir = Path(out_dir) / 'pdf_output'
                        pdf_paths = convert_json_files(out_dir, 'pdf', pdf_dir, json_files=json_files)
                        if pdf_paths:
                            summary_lines.append(f"{len(pdf_paths)} arquivo(s) PDF em {pdf_dir}")
                        logger.info("PDF generated")
                        
                except ImportError:
                    logger.warning("Módulo de formatos de saída não disponível")
                except Exception as e:
                    logger.exception("Erro gerando formatos adicionais: %s", e)
            
            self.set_progress("Concluído.")

            if errors:
                warn_msg = "Alguns arquivos falharam durante o processamento:\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    warn_msg += "\n..."
                poppler_missing = any('poppler' in err.lower() for err in errors)
                if poppler_missing:
                    warn_msg += "\n\nDica: Instale o Poppler e garanta que o executável esteja no PATH para habilitar OCR em PDFs."
                messagebox.showwarning("Aviso", warn_msg)

            messagebox.showinfo("Sucesso", "\n".join(summary_lines))
        except Exception as e:
            logger.exception("Erro durante chunking")
            messagebox.showerror("Erro", f"Erro durante escrita: {e}")
            self.set_progress("Erro")

    def run_pdf_to_word(self, pdf_files, out_dir, use_ocr, clean_chars):
        self.set_pdf_progress("Iniciando conversão PDF para Word...")
        
        try:
            from converter.pdf_to_word import batch_pdf_to_word
            
            converted_files = batch_pdf_to_word(
                pdf_files, out_dir, use_ocr=use_ocr, clean_special_chars=clean_chars
            )
            
            self.set_pdf_progress("Concluído.")
            messagebox.showinfo("Sucesso", f"Conversão concluída. {len(converted_files)} arquivos convertidos.")
            
        except ImportError:
            messagebox.showerror("Erro", "Módulo de conversão PDF para Word não disponível.")
            self.set_pdf_progress("Erro")
        except Exception as e:
            logger.exception("Erro durante conversão PDF para Word")
            messagebox.showerror("Erro", f"Erro durante conversão: {e}")
            self.set_pdf_progress("Erro")

    def run_format_conversion(self, json_folder, out_dir, output_format):
        self.set_convert_progress("Iniciando conversão de formato...")
        
        try:
            from converter.output_formats import convert_json_files
            
            converted_files = convert_json_files(json_folder, output_format, out_dir)
            
            if not converted_files:
                self.set_convert_progress("Nenhum arquivo convertido.")
                messagebox.showwarning("Aviso", "Nenhum arquivo JSON foi encontrado na pasta selecionada.")
                return

            self.set_convert_progress("Concluído.")
            messagebox.showinfo("Sucesso", f"Conversão concluída. {len(converted_files)} arquivo(s) convertidos.")
            
        except ImportError:
            messagebox.showerror("Erro", "Módulo de conversão de formatos não disponível.")
            self.set_convert_progress("Erro")
        except Exception as e:
            logger.exception("Erro durante conversão de formato")
            messagebox.showerror("Erro", f"Erro durante conversão: {e}")
            self.set_convert_progress("Erro")

    def set_progress(self, text):
        def upd():
            self.progress.config(text=text)
        self.root.after(0, upd)

    def set_pdf_progress(self, text):
        def upd():
            self.pdf_progress.config(text=text)
        self.root.after(0, upd)

    def set_convert_progress(self, text):
        def upd():
            self.convert_progress.config(text=text)
        self.root.after(0, upd)


def main():
    root = tk.Tk()
    app = EnhancedApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()