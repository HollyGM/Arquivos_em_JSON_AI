"""Script para simular a execução da GUI sem interface gráfica."""

import sys
import os
from pathlib import Path

# Adicionar o diretório atual ao path para importar converter
sys.path.insert(0, os.path.dirname(__file__))

from converter import reader, chunker

def simulate_run_conversion(inputs, out_dir, max_bytes, recursive, use_ocr, clean_chars, output_txt, output_pdf):
    print("DEBUG: Iniciando...")
    print(f"DEBUG: Inputs: {inputs}")
    print(f"DEBUG: Out dir: {out_dir}")
    print(f"DEBUG: Max bytes: {max_bytes}")
    print(f"DEBUG: Recursive: {recursive}")
    print(f"DEBUG: Use OCR: {use_ocr}")
    print(f"DEBUG: Clean chars: {clean_chars}")
    # gather file list
    candidates = []
    for p in inputs:
        pth = Path(p)
        print(f"DEBUG: Checking path: {p} -> {pth}")
        if pth.is_dir():
            print(f"DEBUG: {p} is dir, recursive={recursive}")
            if recursive:
                for fp in pth.rglob("*"):
                    if fp.is_file() and reader.is_supported(str(fp)):
                        candidates.append(str(fp))
                        print(f"DEBUG: Added file: {fp}")
            else:
                for fp in pth.iterdir():
                    if fp.is_file() and reader.is_supported(str(fp)):
                        candidates.append(str(fp))
                        print(f"DEBUG: Added file: {fp}")
        elif pth.is_file():
            if reader.is_supported(str(pth)):
                candidates.append(str(pth))
                print(f"DEBUG: Added file: {pth}")

    print(f"DEBUG: Candidates found: {candidates}")
    if not candidates:
        print("DEBUG: Nenhum arquivo suportado encontrado.")
        return

    docs = []
    total = len(candidates)
    for i, fp in enumerate(candidates, 1):
        try:
            print(f"DEBUG: Reading file: {fp}")
            text = reader.extract_text(fp, use_ocr=use_ocr, clean_special_chars=clean_chars)
            print(f"DEBUG: Text length: {len(text)}")
        except Exception as e:
            print(f"DEBUG: Error reading {fp}: {e}")
            continue
        docs.append({
            "source_path": str(fp),
            "filename": Path(fp).name,
            "filetype": Path(fp).suffix.lower().lstrip('.'),
            "text": text,
        })

    print(f"DEBUG: Docs prepared: {len(docs)}")
    print("DEBUG: Gerando JSONs...")
    try:
        chunker.chunk_and_write(docs, Path(out_dir), max_bytes)
        print(f"DEBUG: JSONs written to {out_dir}")

        # Gerar formatos adicionais se solicitado
        if output_txt or output_pdf:
            print("DEBUG: Gerando formatos adicionais...")
            try:
                from converter.output_formats import convert_json_files

                if output_txt:
                    convert_json_files(out_dir, 'txt', Path(out_dir) / 'txt_output')
                    print("DEBUG: TXT generated")

                if output_pdf:
                    convert_json_files(out_dir, 'pdf', Path(out_dir) / 'pdf_output')
                    print("DEBUG: PDF generated")

            except ImportError:
                print("DEBUG: Módulo de formatos de saída não disponível")
            except Exception as e:
                print(f"DEBUG: Erro gerando formatos adicionais: {e}")

        print("DEBUG: Concluído.")
    except Exception as e:
        print(f"DEBUG: Erro durante chunking: {e}")

if __name__ == "__main__":
    # Simular chamada da GUI com arquivo de teste
    simulate_run_conversion(
        inputs=["test_sample.txt"],
        out_dir="test_output_gui",
        max_bytes=50 * 1024 * 1024,
        recursive=True,
        use_ocr=False,
        clean_chars=True,
        output_txt=False,
        output_pdf=False
    )