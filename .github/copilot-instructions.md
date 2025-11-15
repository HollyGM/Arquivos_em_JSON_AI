# GitHub Copilot Instructions for Arquivos em JSON AI

## Project Overview

This repository contains a Python-based document converter that transforms text files (.txt, .pdf, .docx, .doc) into structured JSON files optimized for use as knowledge sources by AI models. The project includes both GUI (Tkinter) and CLI interfaces.

**Main Purpose:** Convert documents into JSON format with metadata chunks for AI model ingestion.

## Project Structure

- `main.py` - Main GUI application using Tkinter
- `main_cli.py` - Command-line interface version
- `main_enhanced.py` - Enhanced GUI with OCR, PDF-to-Word conversion, character cleaning, and multi-format output (JSON/TXT/PDF)
- `converter/` - Core conversion modules
  - `reader.py` - File reading logic for txt, pdf, docx, doc
  - `chunker.py` - Document chunking and JSON generation
  - `ocr.py` - OCR functionality for scanned PDFs
  - `pdf_to_word.py` - PDF to Word conversion
  - `output_formats.py` - Multiple output format support
- `tests/` - Test files
- `test_*.py` - Various test scripts (functionality, GUI simulation)
- `dependencies/` - Dependencies management
- `test_output*/` - Test output directories

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Windows, Linux, or macOS

### Installation
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. For OCR functionality (optional):
   - Install Tesseract OCR on your system
   - Required packages: pytesseract, Pillow, pdf2image

3. For better .doc support (optional):
   - Install textract and system dependencies (may vary by OS)

### Running the Application
- **GUI:** `python main.py` or double-click `run.bat` (Windows)
- **CLI:** `python main_cli.py`
- **Enhanced version:** `python main_enhanced.py`

### Running Tests
```bash
python -m pytest tests/ -v
```

Or run individual test files:
```bash
python test_functionality.py
python test_gui_simulation.py
```

## Coding Standards

### Python Style
- Follow PEP 8 conventions
- Use descriptive variable names in Portuguese or English (project uses mix)
- Include docstrings for all functions and classes
- Use type hints where appropriate

### Code Organization
- Keep conversion logic in the `converter/` module
- Separate GUI/CLI interface from business logic
- Use logging for debugging and information messages
- Handle errors gracefully with appropriate error messages

### File Handling
- Always use pathlib.Path for file operations
- Support cross-platform file paths
- Clean up temporary files after processing
- Validate file types before processing

### JSON Output Format
Generated JSON files should follow this structure:
```json
{
  "batch_id": "unique-identifier",
  "created_at": "ISO-8601-timestamp",
  "documents": [
    {
      "id": "document-id",
      "source_path": "original-file-path",
      "filename": "filename.ext",
      "filetype": "txt|pdf|docx|doc",
      "chunk_index": 0,
      "text": "content chunk...",
      "char_count": 12345
    }
  ]
}
```

## Testing Guidelines

### When Making Changes
1. Run existing tests before making changes to establish baseline
2. Add new tests for new functionality
3. Ensure all tests pass before submitting changes
4. Test with different file formats (txt, pdf, docx)
5. Test edge cases (empty files, large files, corrupted files)

### Test Files Location
- Place test sample files in test output directories
- Use `test_sample.txt` for basic functionality tests
- Don't commit large test files or output files to git

## Dependencies

### Core Dependencies
- `pdfminer.six` - PDF text extraction
- `python-docx` - DOCX file handling
- `chardet` - Character encoding detection
- `tqdm` - Progress bars

### Optional Dependencies
- `pytesseract` - OCR for scanned PDFs
- `Pillow` - Image processing
- `pdf2image` - PDF to image conversion
- `reportlab` - PDF generation
- `textract` - Better .doc support (requires system dependencies)

### Adding New Dependencies
1. Check for security vulnerabilities before adding
2. Add to `requirements.txt` with version constraint
3. Document in this file if it's an optional dependency
4. Test installation on clean environment

## Common Tasks

### Adding Support for New File Format
1. Add reader function in `converter/reader.py`
2. Update file type detection logic
3. Add tests for the new format
4. Update README.md with new supported format

### Modifying JSON Structure
1. Update chunker logic in `converter/chunker.py`
2. Update JSON structure documentation in README.md and this file
3. Add migration notes if breaking change
4. Test with existing workflows

### Improving Performance
1. Profile code to identify bottlenecks
2. Consider chunking strategies for large files
3. Implement caching where appropriate
4. Test with various file sizes

## Known Issues and Limitations

- `.doc` (binary format) support requires the `textract` library and platform-specific system dependencies (e.g., antiword on Linux, Microsoft Office components on Windows). If not available, .doc files will be skipped with a warning.
- OCR functionality requires Tesseract installation
- GUI is designed for Windows but should work on other platforms with Tkinter support
- Large files may take significant time to process

## Best Practices for Contributors

1. **Before Starting Work:**
   - Read the README.md for project context
   - Run existing tests to understand current behavior
   - Check for related issues or PRs

2. **While Working:**
   - Make small, focused changes
   - Test changes with multiple file types
   - Keep UI/UX consistent with existing design
   - Log important operations for debugging

3. **Before Submitting:**
   - Run all tests and ensure they pass
   - Update documentation if behavior changes
   - Check for console errors or warnings
   - Verify file paths work cross-platform

4. **Code Review:**
   - Respond to feedback promptly
   - Explain design decisions if non-obvious
   - Update tests based on review feedback

## Project-Specific Notes

- The project currently uses a mix of Portuguese and English in comments and variable names - when contributing, maintain consistency within each file and consider gradually moving toward English-only for better international collaboration
- Batch processing is controlled by max file size (in MB) parameter
- All generated JSONs include metadata for AI model compatibility
- The GUI uses threading to prevent UI freezing during conversion
- Error handling should show user-friendly messages in the GUI
- CLI version should support batch operations and scripting

## Security Considerations

- Validate file types before processing
- Sanitize file paths to prevent directory traversal
- Don't execute untrusted code from document files
- Be careful with temporary file creation and cleanup
- Log security-relevant events
