import json
from pathlib import Path
import tempfile

from converter import indexer


def test_build_and_query_index(tmp_path):
    # Criar um JSON de exemplo com 2 documentos
    batch = {
        "batch_id": "test",
        "created_at": "2025-01-01T00:00:00Z",
        "documents": [
            {"filename": "a.txt", "chunk_index": 0, "text": "Olá mundo. Teste de indexação.", "char_count": 30},
            {"filename": "b.txt", "chunk_index": 0, "text": "Outro documento de teste mundo.", "char_count": 28},
        ],
    }

    out_dir = tmp_path
    jf = out_dir / "output_0001.json"
    with open(jf, "w", encoding="utf-8") as f:
        json.dump(batch, f, ensure_ascii=False)

    # Construir índice
    idx_path = indexer.build_index(out_dir, [jf.name])
    assert idx_path.exists()

    # Consultar por termo "mundo" deve retornar referências
    results = indexer.query_index(idx_path, "mundo", top_k=10)
    assert len(results) >= 1
    # A referência deve conter o arquivo onde o termo aparece
    assert any(r.get("filename") in {"a.txt", "b.txt"} for r in results)
