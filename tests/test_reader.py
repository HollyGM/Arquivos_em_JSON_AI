from converter import reader
from pathlib import Path


def test_read_txt(tmp_path):
    p = tmp_path / "sample.txt"
    p.write_text("Olá mundo\nLinha 2\n")
    text = reader.extract_text(str(p))
    assert "Olá mundo" in text
