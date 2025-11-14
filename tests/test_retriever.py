import json
from pathlib import Path

from converter import indexer, retriever


def test_retrieve_top_chunks(tmp_path):
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

    idx_path = indexer.build_index(out_dir, [jf.name])
    results = retriever.retrieve_top_chunks(out_dir, idx_path, "mundo teste", top_k=5)
    assert isinstance(results, list)
    assert len(results) >= 1
    assert any(r.get("filename") in {"a.txt", "b.txt"} for r in results)
