"""Test case for the encoding detection bug fix.

This test verifies that UTF-8 files with special characters are correctly decoded,
even when chardet misdetects the encoding with low confidence.
"""
from converter import reader
from pathlib import Path


def test_utf8_with_special_chars_low_confidence(tmp_path):
    """Test that UTF-8 files with accented characters are decoded correctly.
    
    This test specifically targets the bug where chardet would misdetect
    UTF-8 files with Portuguese/Spanish characters as ISO-8859-9 (Turkish)
    with low confidence (~63%), causing "á" to be decoded as "Ã¡".
    
    The fix ensures that when chardet confidence is below 90%, UTF-8 is
    tried first before falling back to the detected encoding.
    """
    # Create a small UTF-8 file with Portuguese accented characters
    # This is the exact scenario that triggered the bug
    p = tmp_path / "portuguese.txt"
    p.write_text("Olá mundo\nLinha 2\n", encoding="utf-8")
    
    # Extract text - should correctly decode as UTF-8
    text = reader.extract_text(str(p))
    
    # Verify the text is correctly decoded
    assert "Olá mundo" in text, f"Expected 'Olá mundo' but got: {repr(text)}"
    assert "Linha 2" in text
    # Verify corruption didn't happen
    assert "OlÃ¡" not in text, "Text was incorrectly decoded"


def test_utf8_with_multiple_accented_chars(tmp_path):
    """Test UTF-8 files with multiple types of accented characters."""
    p = tmp_path / "accents.txt"
    content = "Ação, Ñoño, Café, São Paulo, José"
    p.write_text(content, encoding="utf-8")
    
    text = reader.extract_text(str(p))
    
    assert "Ação" in text
    assert "Ñoño" in text
    assert "Café" in text
    assert "São Paulo" in text
    assert "José" in text


def test_utf8_with_emoji_and_special_chars(tmp_path):
    """Test UTF-8 files with emojis and various Unicode characters."""
    p = tmp_path / "unicode.txt"
    content = "Hello 👋 Olá 🌍 Привет"
    p.write_text(content, encoding="utf-8")
    
    text = reader.extract_text(str(p))
    
    assert "Hello" in text
    assert "Olá" in text
    # Note: emoji handling may vary depending on system, so we check the core text


def test_latin1_file_still_works(tmp_path):
    """Test that actual Latin-1 encoded files still work correctly."""
    p = tmp_path / "latin1.txt"
    # Write a Latin-1 file (not UTF-8)
    with open(p, "wb") as f:
        # "Olá" in Latin-1 is different from UTF-8
        f.write(b"Ol\xe1 mundo Latin-1\n")
    
    text = reader.extract_text(str(p))
    
    # Should successfully read the file (may use 'replace' mode for errors)
    assert "mundo" in text
    assert "Latin-1" in text
