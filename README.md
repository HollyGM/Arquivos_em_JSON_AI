# Conversor para JSON estruturado (txt, pdf, docx/doc)

Este projeto converte arquivos de texto (.txt, .pdf, .docx e .doc quando possível) em JSONs estruturados otimizados para uso como fonte de conhecimento por modelos de IA. O usuário pode selecionar arquivos individuais ou pastas (com subpastas) e definir o tamanho máximo (em MB) de cada arquivo JSON gerado.

Funcionalidades principais:
- Seleção de múltiplos arquivos ou uma pasta inteira (recursiva).
- Leitura de .txt, .pdf e .docx (com tentativa de leitura de .doc em sistemas com dependências instaladas).
- Agrupamento em arquivos JSON cujo tamanho (em bytes) não excede o limite escolhido.
- JSONs incluem metadados por chunk para facilitar ingestão por modelos.

Observações e suposições:
- `doc` (formato binário antigo) é suportado em modo "melhor esforço": requer bibliotecas externas (por exemplo, `textract`) que podem precisar de dependências do sistema. Se não estiver disponível, o arquivo será pulado com aviso.
- O projeto foi escrito para rodar com Python 3.8+ em Windows (GUI Tkinter incluído). Dependências opcionais estão listadas em `requirements.txt`.

Como usar (resumo):
1. Instale dependências: `pip install -r requirements.txt` (algumas são opcionais).
2. Execute `python main.py` ou clique duplo no arquivo `run.bat` (Windows).
3. Na interface: escolha arquivos ou pasta, selecione pasta de saída, defina tamanho máximo por JSON (MB) e clique em Converter.

Estrutura do JSON gerado (exemplo resumido):
{
  "batch_id": "...",
  "created_at": "...",
  "documents": [
    {
      "id": "...",
      "source_path": "C:/.../arquivo.pdf",
      "filename": "arquivo.pdf",
      "filetype": "pdf",
      "chunk_index": 0,
      "text": "conteúdo do chunk...",
      "char_count": 12345
    }
  ]
}

Mais detalhes nas docstrings do código.
