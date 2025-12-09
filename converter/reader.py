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
        detection = chardet.detect(raw)
        enc = detection.get("encoding") or "utf-8"
        confidence = detection.get("confidence", 0)
        
        # Se a confiança da detecção for baixa, tentar UTF-8 primeiro
        # UTF-8 é o encoding mais comum atualmente e deve ser preferido
        # quando não há certeza sobre o encoding detectado
        if confidence < 0.9:
            try:
                return raw.decode("utf-8")
            except (UnicodeDecodeError, AttributeError):
                # Se UTF-8 falhar, usar o encoding detectado pelo chardet
                pass
        
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
    """Extrai texto de um arquivo PDF.

    Args:
        path: Caminho para o arquivo PDF

    Returns:
        Texto extraído do PDF

    Raises:
        RuntimeError: Se pdfminer.six não estiver instalado
        Exception: Para outros erros durante extração
    """
    if extract_text_from_pdf is None:
        raise RuntimeError(
            "Dependência pdfminer.six não encontrada.\n"
            "Instale com: pip install pdfminer.six"
        )
    try:
        text = extract_text_from_pdf(str(path))
        return text or ""
    except Exception as e:
        logger.error(f"Erro ao extrair texto do PDF {path}: {e}")
        raise RuntimeError(f"Falha ao processar PDF {path.name}: {e}") from e


def read_docx(path: Path) -> str:
    """Extrai texto de um arquivo DOCX.

    Args:
        path: Caminho para o arquivo DOCX

    Returns:
        Texto extraído do documento

    Raises:
        RuntimeError: Se python-docx não estiver instalado ou houver erro de leitura
    """
    if docx is None:
        raise RuntimeError(
            "Dependência python-docx não encontrada.\n"
            "Instale com: pip install python-docx"
        )
    try:
        doc = docx.Document(str(path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)
    except Exception as e:
        logger.error(f"Erro ao extrair texto do DOCX {path}: {e}")
        raise RuntimeError(f"Falha ao processar DOCX {path.name}: {e}") from e


def read_doc_fallback(path: Path) -> str:
    """Tenta ler arquivo .doc antigo com textract (melhor esforço).

    Args:
        path: Caminho para o arquivo DOC

    Returns:
        Texto extraído do documento

    Raises:
        RuntimeError: Se textract não estiver disponível ou falhar
    """
    if textract is None:
        raise RuntimeError(
            "Leitura de .doc não disponível.\n"
            "Instale textract e dependências do sistema para suportar arquivos .doc antigos.\n"
            "Nota: Considere converter .doc para .docx usando Microsoft Word ou LibreOffice."
        )
    try:
        data = textract.process(str(path))
        try:
            return data.decode("utf-8", errors="replace")
        except Exception:
            return str(data)
    except Exception as e:
        logger.error(f"Erro ao processar arquivo DOC {path}: {e}")
        raise RuntimeError(
            f"Falha ao processar arquivo DOC {path.name}.\n"
            f"Erro: {e}\n"
            f"Dica: Converta o arquivo para .docx usando Word ou LibreOffice."
        ) from e


def extract_text(path: str, use_ocr: bool = False, clean_special_chars: bool = True) -> str:
    """Extrai texto do arquivo com base na extensão.

    Args:
        path: Caminho para o arquivo
        use_ocr: Se deve usar OCR para PDFs (força OCR ou detecta automaticamente)
        clean_special_chars: Se deve limpar caracteres especiais

    Returns:
        Texto extraído do documento

    Raises:
        ValueError: Se a extensão do arquivo não for suportada
        RuntimeError: Se dependências necessárias não estiverem instaladas
        FileNotFoundError: Se o arquivo não existir
    """
    p = Path(path)

    # Validar existência do arquivo
    if not p.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    if not p.is_file():
        raise ValueError(f"Caminho não é um arquivo: {path}")

    ext = p.suffix.lower()
    logger.info(f"Extraindo texto de {p.name} (tipo: {ext})")

    try:
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
            supported_formats = [".txt", ".pdf", ".docx", ".doc"]
            raise ValueError(
                f"Extensão não suportada: {ext}\n"
                f"Formatos suportados: {', '.join(supported_formats)}"
            )

        # Aplicar limpeza de caracteres se solicitado
        if clean_special_chars and ext != ".pdf":  # PDF com OCR já aplica limpeza
            try:
                from .ocr import clean_text
                text = clean_text(text)
            except ImportError:
                pass  # Se módulo OCR não disponível, manter texto original

        logger.info(f"Texto extraído com sucesso: {len(text)} caracteres")
        return text

    except Exception as e:
        logger.error(f"Erro ao extrair texto de {path}: {e}")
        raise


def is_supported(path: str) -> bool:
    return Path(path).suffix.lower() in {".txt", ".pdf", ".docx", ".doc"}
