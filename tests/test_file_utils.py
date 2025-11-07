"""Tests for file_utils module."""
import pytest
from pathlib import Path
from converter import file_utils


def test_collect_files_single_file(tmp_path):
    """Test collecting a single supported file."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content")
    
    files = file_utils.collect_files([str(test_file)], recursive=False)
    
    assert len(files) == 1
    assert str(test_file) in files


def test_collect_files_directory_non_recursive(tmp_path):
    """Test collecting files from directory without recursion."""
    # Create files in root
    (tmp_path / "file1.txt").write_text("Content 1")
    (tmp_path / "file2.pdf").write_text("PDF content")
    
    # Create subdirectory with file (should be ignored)
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "file3.txt").write_text("Content 3")
    
    files = file_utils.collect_files([str(tmp_path)], recursive=False)
    
    assert len(files) == 2
    assert not any("file3.txt" in f for f in files)


def test_collect_files_directory_recursive(tmp_path):
    """Test collecting files from directory with recursion."""
    # Create files in root
    (tmp_path / "file1.txt").write_text("Content 1")
    
    # Create subdirectory with file
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "file2.txt").write_text("Content 2")
    
    files = file_utils.collect_files([str(tmp_path)], recursive=True)
    
    assert len(files) == 2
    assert any("file2.txt" in f for f in files)


def test_collect_files_unsupported_extension(tmp_path):
    """Test that unsupported files are ignored."""
    (tmp_path / "test.xyz").write_text("Unsupported")
    (tmp_path / "test.txt").write_text("Supported")
    
    files = file_utils.collect_files([str(tmp_path)], recursive=False)
    
    assert len(files) == 1
    assert "test.txt" in files[0]


def test_process_files_to_docs_basic(tmp_path):
    """Test basic document processing."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello World", encoding='utf-8')
    
    docs = file_utils.process_files_to_docs(
        [str(test_file)],
        use_ocr=False,
        clean_special_chars=False
    )
    
    assert len(docs) == 1
    assert docs[0]["filename"] == "test.txt"
    assert docs[0]["filetype"] == "txt"
    assert "Hello World" in docs[0]["text"]
    assert "source_path" in docs[0]


def test_process_files_to_docs_with_callback(tmp_path):
    """Test document processing with progress callback."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content", encoding='utf-8')
    
    progress_calls = []
    
    def callback(idx, total, filepath):
        progress_calls.append((idx, total, filepath))
    
    docs = file_utils.process_files_to_docs(
        [str(test_file)],
        use_ocr=False,
        clean_special_chars=False,
        progress_callback=callback
    )
    
    assert len(docs) == 1
    assert len(progress_calls) == 1
    assert progress_calls[0] == (1, 1, str(test_file))


def test_process_files_to_docs_empty_list():
    """Test processing empty file list."""
    docs = file_utils.process_files_to_docs(
        [],
        use_ocr=False,
        clean_special_chars=False
    )
    
    assert len(docs) == 0
