import json
from pathlib import Path

from converter import chunker


def test_chunk_and_write_with_index(tmp_path):
    docs = [
        {"filename": "a.txt", "chunk_index": 0, "text": "Olá mundo index test", "char_count": 22},
        {"filename": "b.txt", "chunk_index": 0, "text": "Outro documento com texto de teste mundo", "char_count": 36},
    ]

    out_dir = tmp_path
    files = chunker.chunk_and_write(docs, out_dir, max_size_bytes=1024 * 10, embed_index=True)
    assert files
    p = Path(files[0])
    data = json.loads(p.read_text(encoding='utf-8'))
    assert 'local_index' in data
    # termo básico deve aparecer
    assert 'mundo' in data['local_index']
