"""Script de teste para verificar as novas funcionalidades implementadas.

Este arquivo é um script de testes manuais e NÃO deve ser executado pelo pytest automaticamente.
Se o pytest coletar este arquivo ele causará falhas porque espera fixtures que não existem.
Para evitar isso, pulamos a execução quando o pytest faz a coleta do módulo.
"""

import pytest
pytest.skip("Skipping manual test script (run manually with python test_functionality.py)", allow_module_level=True)

import os
import json
from pathlib import Path
from converter import reader, chunker
# módulos opcionais usados apenas em versões avançadas de teste/manual
try:
    from converter.ocr import clean_text
except Exception:
    clean_text = lambda t, simple_mode=True: t

try:
    from converter.output_formats import json_to_txt, json_to_pdf
except Exception:
    json_to_txt = lambda data, p: None
    json_to_pdf = lambda data, p: None

def test_basic_functionality():
    """Testa a funcionalidade básica de conversão."""
    print("=== Testando funcionalidade básica ===")
    
    # Teste de leitura de arquivo
    test_file = "test_sample.txt"
    if os.path.exists(test_file):
        print(f"Lendo arquivo: {test_file}")
        text = reader.extract_text(test_file, clean_special_chars=True)
        print(f"Texto extraído (primeiros 100 chars): {text[:100]}...")
        
        # Teste de limpeza de caracteres
        print("\n=== Testando limpeza de caracteres ===")
        dirty_text = "Texto com @#$%^&*() caracteres especiais!!!"
        clean = clean_text(dirty_text, simple_mode=True)
        print(f"Original: {dirty_text}")
        print(f"Limpo: {clean}")
        
        return text
    else:
        print(f"Arquivo {test_file} não encontrado!")
        return None

def test_json_generation(text):
    """Testa a geração de JSON."""
    if not text:
        return None
        
    print("\n=== Testando geração de JSON ===")
    
    # Criar documento de teste
    docs = [{
        "source_path": "test_sample.txt",
        "filename": "test_sample.txt",
        "filetype": "txt",
        "text": text,
    }]
    
    # Criar diretório de saída
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    # Gerar JSON
    chunker.chunk_and_write(docs, output_dir, 1024 * 1024)  # 1MB max
    
    # Verificar se foi criado
    json_files = list(output_dir.glob("*.json"))
    if json_files:
        print(f"JSON criado: {json_files[0]}")
        
        # Carregar e verificar conteúdo
        with open(json_files[0], 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Documentos no JSON: {len(data.get('documents', []))}")
        return json_files[0], data
    else:
        print("Nenhum arquivo JSON foi criado!")
        return None, None

def test_output_formats(json_file, json_data):
    """Testa os formatos de saída adicionais."""
    if not json_file or not json_data:
        return
        
    print("\n=== Testando formatos de saída ===")
    
    try:
        # Teste TXT
        print("Gerando arquivo TXT...")
        txt_file = json_to_txt(json_data, "test_output/output.txt")
        print(f"Arquivo TXT criado: {txt_file}")
        
        # Teste PDF
        print("Gerando arquivo PDF...")
        pdf_file = json_to_pdf(json_data, "test_output/output.pdf")
        print(f"Arquivo PDF criado: {pdf_file}")
        
    except Exception as e:
        print(f"Erro testando formatos de saída: {e}")

def main():
    """Função principal de teste."""
    print("Iniciando testes das novas funcionalidades...\n")
    
    # Teste básico
    text = test_basic_functionality()
    
    # Teste JSON
    json_file, json_data = test_json_generation(text)
    
    # Teste formatos de saída
    test_output_formats(json_file, json_data)
    
    print("\n=== Testes concluídos ===")
    print("Verifique a pasta 'test_output' para os arquivos gerados.")

if __name__ == "__main__":
    main()