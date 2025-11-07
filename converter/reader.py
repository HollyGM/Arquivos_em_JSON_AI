"""Funções para extração de texto de diferentes tipos de arquivo.

Suporta: .txt, .pdf, .docx e tentativa de .doc (melhor esforço).
Suporta OCR para PDFs escaneados.
Dependências opcionais (pdfminer.six, python-docx, textract, pytesseract).
"""
from pathlib import Path
import logging
import os

try:
    from pdfminer.high_level import extract_text as extract_text_from_pdf
except Exception:
    extract_text_from_pdf = None

try:
    import docx
except Exception:
    docx = None

try:
    import textract
except Exception:
    textract = None

try:
    import chardet
except Exception:
    chardet = None

logger = logging.getLogger(__name__)


def read_txt(path: Path) -> str:
    """Lê arquivo .txt tentando detectar encoding.

    Retorna string com todo o texto (strip preservado).
    """
    # Tentar detectar encoding com chardet se disponível
    if chardet:
        with open(path, "rb") as f:
            raw = f.read()
        enc = chardet.detect(raw).get("encoding") or "utf-8"
        try:
            return raw.decode(enc, errors="replace")
        except Exception:
            return raw.decode("utf-8", errors="replace")
    # fallback
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        with open(path, "r", encoding="latin-1", errors="replace") as f:
            return f.read()


def read_pdf(path: Path) -> str:
    if extract_text_from_pdf is None:
        raise RuntimeError("Dependência pdfminer.six não encontrada — instale via pip install pdfminer.six")
    text = extract_text_from_pdf(str(path))
    return text or ""


def read_docx(path: Path) -> str:
    if docx is None:
        raise RuntimeError("Dependência python-docx não encontrada — instale via pip install python-docx")
    doc = docx.Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs)


def read_doc_fallback(path: Path) -> str:
    """Tentar ler .doc com textract (melhor esforço)."""
    if textract is None:
        raise RuntimeError("Leitura de .doc não disponível: instale textract (e dependências do sistema) para suportar .doc")
    data = textract.process(str(path))
    try:
        return data.decode("utf-8", errors="replace")
    except Exception:
        return str(data)


def extract_text(path: str, use_ocr: bool = False, clean_special_chars: bool = True) -> str:
    """Extrai texto do arquivo com base na extensão.

    Args:
        path: Caminho para o arquivo
        use_ocr: Se deve usar OCR para PDFs (força OCR ou detecta automaticamente)
        clean_special_chars: Se deve limpar caracteres especiais

    Lança RuntimeError com mensagem amigável quando dependência ausente.
    """
    p = Path(path)
    ext = p.suffix.lower()
    if ext == ".txt":
        text = read_txt(p)
    elif ext == ".pdf":
        if use_ocr:
            # Usar OCR para PDFs
            try:
                from .ocr import extract_text_with_ocr
                text = extract_text_with_ocr(str(path), force_ocr=True, clean_special_chars=clean_special_chars)
            except ImportError:
                logger.warning("Módulo OCR não disponível, usando extração normal")
                text = read_pdf(p)
            except Exception as e:
                logger.warning(f"OCR falhou para {path}: {e}, usando extração normal")
                text = read_pdf(p)
        else:
            text = read_pdf(p)
    elif ext == ".docx":
        text = read_docx(p)
    elif ext == ".doc":
        text = read_doc_fallback(p)
    else:
        raise ValueError(f"Extensão não suportada: {ext}")
    
    # Aplicar limpeza de caracteres se solicitado
    if clean_special_chars and ext != ".pdf":  # PDF com OCR já aplica limpeza
        try:
            from .ocr import clean_text
            text = clean_text(text)
        except ImportError:
            pass  # Se módulo OCR não disponível, manter texto original
    
    return text


def is_supported(path: str) -> bool:
    return Path(path).suffix.lower() in {".txt", ".pdf", ".docx", ".doc"}
