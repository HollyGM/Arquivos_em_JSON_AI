import json
from pathlib import Path

from converter import output_formats


def test_json_to_mrd(tmp_path):
    batch = {
        "batch_id": "test",
        "created_at": "2025-01-01T00:00:00Z",
        "documents": [
            {"filename": "a.txt", "chunk_index": 0, "text": "Olá mundo. Teste de indexação.", "char_count": 30},
        ],
    }

    out = tmp_path / "out.mrd.json"
    path = output_formats.json_to_mrd(batch, str(out), embed_index=True)
    p = Path(path)
    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))
    assert 'local_index' in data
    assert 'mrd_version' in data
    assert data['documents'][0]['filename'] == 'a.txt'
