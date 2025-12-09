from converter import reader
from pathlib import Path
import pytest


def test_read_txt(tmp_path):
    p = tmp_path / "sample.txt"
    p.write_text("Olá mundo\nLinha 2\n")
    text = reader.extract_text(str(p))
    assert "Olá mundo" in text


def test_read_txt_utf8_with_special_chars(tmp_path):
    """Test that UTF-8 files with special characters are read correctly.
    
    This test specifically validates the bug fix where chardet would incorrectly
    identify UTF-8 files as other encodings (e.g., ISO-8859-9), causing corruption
    of special characters like á, é, ã, ç commonly used in Portuguese text.
    """
    p = tmp_path / "portuguese_text.txt"
    
    # Create a file with various Portuguese special characters
    content = (
        "Olá mundo\n"
        "Este é um texto em português.\n"
        "Caracteres especiais: á é í ó ú ã õ ç\n"
        "Acentuação: ÀÁÂÃÄÅÈÉÊË"
    )
    p.write_text(content, encoding='utf-8')
    
    # Extract text (clean_special_chars=True is default, which normalizes whitespace)
    text = reader.extract_text(str(p), clean_special_chars=False)
    
    # Verify all special characters are preserved correctly
    assert "Olá mundo" in text
    assert "português" in text
    assert "á é í ó ú ã õ ç" in text
    assert "ÀÁÂÃÄÅÈÉÊË" in text
    
    # Verify the text is correct (should be exactly the same without cleaning)
    assert text == content


def test_read_txt_latin1_fallback(tmp_path):
    """Test that latin-1 encoded files can still be read correctly."""
    p = tmp_path / "latin1_text.txt"
    
    # Create a latin-1 encoded file
    content = "Texto com acentuação latin-1: café, São Paulo"
    with open(p, 'w', encoding='latin-1') as f:
        f.write(content)
    
    # Extract text - should handle latin-1 gracefully
    text = reader.extract_text(str(p), clean_special_chars=False)
    
    # Verify the text is readable and contains expected content
    # Latin-1 should be correctly decoded when UTF-8 fails
    assert "Texto" in text
    assert "café" in text
    assert "São Paulo" in text


def test_read_txt_empty_file(tmp_path):
    """Test reading an empty file."""
    p = tmp_path / "empty.txt"
    p.write_text("", encoding='utf-8')
    
    text = reader.extract_text(str(p))
    assert text == ""


def test_read_txt_nonexistent_file(tmp_path):
    """Test that reading a non-existent file raises FileNotFoundError."""
    p = tmp_path / "nonexistent.txt"
    
    with pytest.raises(FileNotFoundError):
        reader.extract_text(str(p))
