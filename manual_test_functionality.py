"""Script de execução manual para verificar funcionalidades (não é um teste pytest).

Renomeado para evitar coleta automática pelo pytest. Execute com:
    python manual_test_functionality.py
"""
import os
import json
from pathlib import Path
from converter import reader, chunker

def basic_functionality():
    """Testa a funcionalidade básica de conversão (manual)."""
    print("=== Testando funcionalidade básica ===")
    test_file = "test_sample.txt"
    if os.path.exists(test_file):
        print(f"Lendo arquivo: {test_file}")
        text = reader.extract_text(test_file)
        print(f"Texto extraído (primeiros 100 chars): {text[:100]}...")
        return text
    else:
        print(f"Arquivo {test_file} não encontrado!")
        return None


def json_generation(text):
    if not text:
        return None, None
    print("\n=== Testando geração de JSON ===")
    docs = [{
        "source_path": "test_sample.txt",
        "filename": "test_sample.txt",
        "filetype": "txt",
        "text": text,
    }]
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    chunker.chunk_and_write(docs, output_dir, 1024 * 1024)
    json_files = list(output_dir.glob("*.json"))
    if json_files:
        print(f"JSON criado: {json_files[0]}")
        with open(json_files[0], 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Documentos no JSON: {len(data.get('documents', []))}")
        return json_files[0], data
    else:
        print("Nenhum arquivo JSON foi criado!")
        return None, None


def main():
    print("Iniciando testes manuais das novas funcionalidades...\n")
    text = basic_functionality()
    json_file, json_data = json_generation(text)
    print("\n=== Testes manuais concluídos ===")
    print("Verifique a pasta 'test_output' para os arquivos gerados.")


if __name__ == '__main__':
    main()
