# Conversor de Documentos para JSON

Conversor robusto e otimizado que transforma arquivos de texto (TXT, PDF, DOCX, DOC) em JSONs estruturados, ideal para uso como base de conhecimento por modelos de IA e RAG (Retrieval-Augmented Generation).

## 🚀 Funcionalidades Principais

### Conversão de Documentos
- **Formatos suportados**: `.txt`, `.pdf`, `.docx`, `.doc` (melhor esforço)
- **Processamento em lote**: Múltiplos arquivos ou pastas inteiras (recursivo)
- **Chunking inteligente**: Agrupa documentos respeitando limite de tamanho configurável
- **Metadados completos**: Cada chunk inclui informações de origem, tipo, índice e contagem de caracteres

### Processamento Avançado
- **OCR em PDFs**: Extração de texto de PDFs escaneados usando Tesseract
- **Limpeza de texto**: Remoção automática de caracteres especiais e normalização
- **Detecção de encoding**: Suporte automático para diferentes codificações de texto
- **Tratamento robusto de erros**: Logs detalhados e mensagens de erro claras

### Formatos de Saída
- **JSON estruturado** (formato principal)
- **TXT formatado** (relatórios legíveis)
- **PDF** (documentos formatados com reportlab)
- **DOCX** (conversão de PDF para Word)

### Interfaces
- **GUI Avançada** com múltiplas abas e configurações detalhadas
- **CLI** para automação e processamento em lote
- **Launcher .bat** otimizado para Windows

## 📋 Requisitos

- **Python 3.8+**
- **Dependências Python**: Instaladas automaticamente via `requirements.txt`
- **Tesseract OCR** (opcional): Para OCR em PDFs escaneados
- **Poppler** (opcional): Para conversão PDF→imagem (necessário para OCR)

## 🔧 Instalação

### 1. Clone o repositório
```bash
git clone <repositório>
cd Arquivos_em_JSON_AI
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. (Opcional) Instale Tesseract para OCR
- **Windows**: Baixe e instale de [GitHub Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- **Linux**: `sudo apt-get install tesseract-ocr tesseract-ocr-por`
- **Mac**: `brew install tesseract tesseract-lang`

### 4. (Opcional) Instale Poppler para OCR em PDFs
- **Windows**: Baixe de [Poppler Windows](https://github.com/oschwartz10612/poppler-windows/releases/)
- Extraia para `dependencies/poppler-23.08.0-0/` ou adicione ao PATH

## 🎯 Como Usar

### Modo GUI (Recomendado)

**Windows - Opção 1 (Completa com verificações):**
```bash
run.bat
```
Faz verificação completa de Python, dependências e Poppler.

**Windows - Opção 2 (Rápida):**
```bash
run_gui.bat
```
Launcher simplificado que inicia a GUI diretamente (mais rápido).

**Linux/Mac:**
```bash
python main_enhanced.py
```

A interface possui 3 abas:
1. **Conversão para JSON**: Processamento principal de documentos
2. **PDF para Word**: Conversão direta PDF→DOCX
3. **Converter Saídas**: Transforma JSONs em TXT ou PDF

### Modo CLI
```bash
# Processar pasta atual recursivamente
python main_cli.py --inputs . --outdir output --recursive

# Processar com OCR forçado
python main_cli.py --inputs docs/ --outdir output --force-ocr

# Processar e gerar TXT adicional
python main_cli.py --inputs docs/ --outdir output --json-to txt

# Converter PDFs para Word
python main_cli.py --pdf-to-word --pdf-inputs file1.pdf file2.pdf --pdf-to-word-outdir docx_output
```

### Argumentos CLI
- `--inputs, -i`: Arquivos ou pastas de entrada
- `--outdir, -o`: Pasta de saída para JSONs (padrão: `output_jsons/`)
- `--max-mb`: Tamanho máximo por JSON em MB (padrão: 50)
- `--recursive`: Pesquisar pastas recursivamente
- `--force-ocr`: Forçar OCR em todos os PDFs
- `--no-clean`: Não limpar caracteres especiais
- `--json-to {txt,pdf}`: Converter JSONs gerados para formato adicional
- `--pdf-to-word`: Modo de conversão PDF→DOCX

## 📊 Estrutura do JSON Gerado

```json
{
  "batch_id": "uuid-do-lote",
  "created_at": "2025-01-15T10:30:00Z",
  "documents": [
    {
      "id": "uuid-do-documento",
      "source_path": "/caminho/completo/arquivo.pdf",
      "filename": "arquivo.pdf",
      "filetype": "pdf",
      "chunk_index": 0,
      "text": "Conteúdo extraído do documento...",
      "char_count": 12345
    }
  ]
}
```

### Campos dos Documentos
- **id**: Identificador único do documento
- **source_path**: Caminho original do arquivo
- **filename**: Nome do arquivo
- **filetype**: Extensão (txt, pdf, docx, doc)
- **chunk_index**: Índice do chunk (0 para documento inteiro, 1+ se dividido)
- **text**: Conteúdo de texto extraído
- **char_count**: Número de caracteres no chunk

## 🏗️ Estrutura do Projeto

```
Arquivos_em_JSON_AI/
├── converter/              # Módulos principais
│   ├── reader.py          # Extração de texto
│   ├── chunker.py         # Divisão em chunks
│   ├── ocr.py             # Processamento OCR
│   ├── output_formats.py  # Conversão de formatos
│   └── pdf_to_word.py     # PDF para Word
├── main.py                # GUI simples
├── main_enhanced.py       # GUI avançada (recomendado)
├── main_cli.py            # Interface CLI
├── run.bat                # Launcher Windows
├── requirements.txt       # Dependências Python
└── README.md             # Este arquivo
```

## 🐛 Solução de Problemas

### OCR não funciona
- Verifique se Tesseract está instalado: `tesseract --version`
- Verifique se Poppler está no PATH
- No Windows, o `run.bat` tentará usar Poppler em `dependencies/`

### Erro ao ler arquivos .doc
- Formato antigo, suporte limitado
- **Recomendação**: Converta para .docx usando Word ou LibreOffice
- Para suporte .doc: instale `textract` e dependências do sistema

### Arquivo muito grande
- Aumente `--max-mb` no CLI
- Ou diminua para dividir em mais arquivos menores

### Caracteres estranhos no texto
- Habilite "Limpar caracteres especiais" na GUI
- Ou remova `--no-clean` no CLI

## 📝 Logs e Debug

Logs são salvos em:
- **gui_debug.log**: Logs detalhados da interface gráfica
- Console: Logs do modo CLI

## 🤝 Contribuindo

Contribuições são bem-vindas! Áreas de melhoria:
- Suporte a mais formatos (HTML, Markdown, etc.)
- Melhorias no OCR (preprocessamento de imagens)
- Interface web
- Testes automatizados adicionais

## 📄 Licença

Este projeto é fornecido como está, sem garantias. Use por sua conta e risco.

## 🔗 Links Úteis

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [Poppler](https://poppler.freedesktop.org/)
- [python-docx](https://python-docx.readthedocs.io/)
- [pdfminer.six](https://pdfminersix.readthedocs.io/)

---

**Versão**: 2.0
**Última atualização**: 2025-01-15
