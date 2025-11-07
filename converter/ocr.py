"""Módulo para processamento OCR de PDFs e imagens.

Funcionalidades:
- OCR em PDFs escaneados
- Limpeza de caracteres especiais
- Normalização de texto
"""
from pathlib import Path
import logging
import re

try:
    import pytesseract
    from PIL import Image
    from pdf2image import convert_from_path
except ImportError:
    pytesseract = None
    Image = None
    convert_from_path = None

logger = logging.getLogger(__name__)


def clean_text(text: str, simple_mode: bool = True) -> str:
    """Limpa e normaliza texto removendo caracteres especiais.
    
    Args:
        text: Texto a ser limpo
        simple_mode: Se True, mantém apenas caracteres básicos
    
    Returns:
        Texto limpo e normalizado
    """
    if not text:
        return ""
    
    # Normalizar espaços em branco
    text = re.sub(r'\s+', ' ', text.strip())
    
    if simple_mode:
        # Manter apenas letras, números, espaços e pontuação básica
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\"\'\/\\\n\r]', '', text, flags=re.UNICODE)
        
        # Remover caracteres de controle
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Normalizar quebras de linha múltiplas
        text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()


def ocr_pdf(pdf_path: str, clean_special_chars: bool = True) -> str:
    """Extrai texto de PDF usando OCR.
    
    Args:
        pdf_path: Caminho para o arquivo PDF
        clean_special_chars: Se deve limpar caracteres especiais
    
    Returns:
        Texto extraído via OCR
    
    Raises:
        RuntimeError: Se dependências OCR não estão instaladas
    """
    if not all([pytesseract, Image, convert_from_path]):
        raise RuntimeError(
            "Dependências OCR não encontradas. Instale: pip install pytesseract Pillow pdf2image"
        )
    
    try:
        # Converter PDF para imagens
        logger.info(f"Convertendo PDF para imagens: {pdf_path}")
        images = convert_from_path(pdf_path, dpi=200)
        
        extracted_text = []
        
        for i, image in enumerate(images):
            logger.info(f"Processando página {i+1}/{len(images)}")
            
            # Aplicar OCR na imagem
            page_text = pytesseract.image_to_string(image, lang='por+eng')
            
            if clean_special_chars:
                page_text = clean_text(page_text)
            
            extracted_text.append(page_text)
        
        full_text = '\n\n--- PÁGINA {} ---\n\n'.join(
            f"{i+1}\n{text}" for i, text in enumerate(extracted_text) if text.strip()
        )
        
        logger.info(f"OCR concluído. Extraído {len(full_text)} caracteres")
        return full_text
        
    except Exception as e:
        logger.error(f"Erro durante OCR do PDF {pdf_path}: {e}")
        raise


def is_scanned_pdf(pdf_path: str) -> bool:
    """Verifica se um PDF é escaneado (sem texto extraível).
    
    Args:
        pdf_path: Caminho para o arquivo PDF
    
    Returns:
        True se o PDF parece ser escaneado
    """
    try:
        # Tentar extrair texto normal primeiro
        from .reader import read_pdf
        text = read_pdf(Path(pdf_path))
        
        # Se o texto extraído é muito pequeno ou contém muitos caracteres estranhos,
        # provavelmente é um PDF escaneado
        if len(text.strip()) < 100:
            return True
        
        # Verificar se há muitos caracteres não alfanuméricos
        alphanumeric_ratio = sum(c.isalnum() or c.isspace() for c in text) / len(text)
        if alphanumeric_ratio < 0.7:
            return True
        
        return False
        
    except Exception:
        # Se não conseguir extrair texto, assumir que é escaneado
        return True


def extract_text_with_ocr(pdf_path: str, force_ocr: bool = False, clean_special_chars: bool = True) -> str:
    """Extrai texto de PDF, usando OCR se necessário.
    
    Args:
        pdf_path: Caminho para o arquivo PDF
        force_ocr: Se deve forçar uso do OCR mesmo se há texto extraível
        clean_special_chars: Se deve limpar caracteres especiais
    
    Returns:
        Texto extraído
    """
    if force_ocr or is_scanned_pdf(pdf_path):
        logger.info(f"Usando OCR para PDF: {pdf_path}")
        return ocr_pdf(pdf_path, clean_special_chars)
    else:
        logger.info(f"Extraindo texto normal do PDF: {pdf_path}")
        from .reader import read_pdf
        text = read_pdf(Path(pdf_path))
        
        if clean_special_chars:
            text = clean_text(text)
        
        return text