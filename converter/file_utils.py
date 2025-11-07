"""Utilidades compartilhadas para coleta e processamento de arquivos.

Este módulo contém funções reutilizáveis para evitar duplicação de código
entre main.py, main_cli.py e main_enhanced.py.
"""
from pathlib import Path
from typing import List, Dict, Any
import logging

from . import reader

logger = logging.getLogger(__name__)


def collect_files(inputs: List[str], recursive: bool = True) -> List[str]:
    """Coleta arquivos suportados a partir de uma lista de entradas.
    
    Args:
        inputs: Lista de caminhos de arquivos ou pastas
        recursive: Se deve pesquisar pastas recursivamente
    
    Returns:
        Lista de caminhos de arquivos suportados
    """
    candidates = []
    for p in inputs:
        pth = Path(p)
        if pth.is_dir():
            if recursive:
                for fp in pth.rglob("*"):
                    if fp.is_file() and reader.is_supported(str(fp)):
                        candidates.append(str(fp))
            else:
                for fp in pth.iterdir():
                    if fp.is_file() and reader.is_supported(str(fp)):
                        candidates.append(str(fp))
        elif pth.is_file():
            if reader.is_supported(str(pth)):
                candidates.append(str(pth))
    return candidates


def process_files_to_docs(
    candidates: List[str],
    use_ocr: bool = False,
    clean_special_chars: bool = True,
    progress_callback=None
) -> List[Dict[str, Any]]:
    """Processa lista de arquivos e retorna documentos estruturados.
    
    Args:
        candidates: Lista de caminhos de arquivos
        use_ocr: Se deve usar OCR para PDFs
        clean_special_chars: Se deve limpar caracteres especiais
        progress_callback: Função opcional para reportar progresso (índice, total, filepath)
    
    Returns:
        Lista de dicionários com metadata e texto dos documentos
    """
    docs = []
    total = len(candidates)
    
    for i, fp in enumerate(candidates, 1):
        try:
            if progress_callback:
                progress_callback(i, total, fp)
            
            text = reader.extract_text(fp, use_ocr=use_ocr, clean_special_chars=clean_special_chars)
        except Exception as e:
            logger.exception("Erro lendo %s: %s", fp, e)
            continue
        
        docs.append({
            "source_path": str(fp),
            "filename": Path(fp).name,
            "filetype": Path(fp).suffix.lower().lstrip('.'),
            "text": text,
        })
    
    return docs
