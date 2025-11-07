"""Modo CLI para operações em lote do conversor.

Uso exemplo:
  python main_cli.py --inputs "docs/" --outdir out_json --max-mb 50 --recursive --force-ocr --json-to txt
  python main_cli.py --pdf-to-word --pdf-inputs file1.pdf file2.pdf --pdf-to-word-outdir docx_out --force-ocr
"""
import argparse
import logging
import os
from pathlib import Path
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from converter import reader, chunker
from converter import ocr as conv_ocr
from converter import output_formats
from converter import pdf_to_word
from converter import file_utils


def process_files(candidates, out_dir, max_bytes, force_ocr=False, clean_special_chars=True):
    """Processa arquivos e gera JSONs.
    
    Args:
        candidates: Lista de caminhos de arquivos a processar
        out_dir: Diretório de saída para os arquivos JSON
        max_bytes: Tamanho máximo em bytes por arquivo JSON
        force_ocr: Se deve forçar OCR em PDFs
        clean_special_chars: Se deve limpar caracteres especiais
    
    Returns:
        Lista de caminhos dos arquivos JSON criados
    """
    def log_progress(i, total, fp):
        logger.info(f"Lendo ({i}/{total}): {fp}")
    
    # Use utility function for processing
    docs = file_utils.process_files_to_docs(
        candidates,
        use_ocr=force_ocr,
        clean_special_chars=clean_special_chars,
        progress_callback=log_progress
    )
    
    # Write JSON chunks
    return chunker.chunk_and_write(docs, Path(out_dir), max_bytes)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="CLI para conversor de documentos")
    parser.add_argument('--inputs', '-i', nargs='*', help='Arquivos ou pastas de entrada (padrão: cwd)')
    parser.add_argument('--outdir', '-o', default=str(Path.cwd() / 'output_jsons'), help='Pasta de saída para JSONs')
    parser.add_argument('--max-mb', type=int, default=50, help='Tamanho máximo por JSON em MB')
    parser.add_argument('--recursive', action='store_true', help='Pesquisar pastas recursivamente')
    parser.add_argument('--force-ocr', action='store_true', help='Forçar OCR em PDFs')
    parser.add_argument('--no-clean', dest='clean', action='store_false', help='Não limpar caracteres especiais')
    parser.add_argument('--json-to', choices=['txt', 'pdf'], help='Converter JSONs gerados para TXT ou PDF')
    parser.add_argument('--output-converted-dir', default=None, help='Diretório para arquivos convertidos (JSON->TXT/PDF)')
    parser.add_argument('--pdf-to-word', dest='pdf_to_word', action='store_true', help='Converter PDFs para DOCX (batch)')
    parser.add_argument('--pdf-inputs', nargs='*', help='Lista de PDFs para conversão para Word (se --pdf-to-word)')
    parser.add_argument('--pdf-to-word-outdir', default=str(Path.cwd() / 'pdf_to_word'), help='Pasta de saída para DOCX')
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    if args.pdf_to_word:
        pdfs = args.pdf_inputs or []
        if not pdfs:
            logger.error("Nenhum PDF informado para --pdf-to-word")
            sys.exit(1)
        pdf_to_word.batch_pdf_to_word(pdfs, args.pdf_to_word_outdir, use_ocr=args.force_ocr, clean_special_chars=args.clean)
        logger.info("Conversão PDF->Word concluída")
        return

    inputs = args.inputs or [os.getcwd()]
    candidates = file_utils.collect_files(inputs, args.recursive)
    if not candidates:
        logger.warning("Nenhum arquivo suportado encontrado nas entradas fornecidas.")
        return

    logger.info(f"Processando {len(candidates)} arquivos. Saida em: {args.outdir}")
    json_files = process_files(candidates, args.outdir, args.max_mb * 1024 * 1024, force_ocr=args.force_ocr, clean_special_chars=args.clean)

    # Conversão adicional: JSON -> txt/pdf
    if args.json_to:
        logger.info(f"Convertendo JSONs para {args.json_to}")
        output_formats.convert_json_files(args.outdir, args.json_to, args.output_converted_dir, json_files=json_files)


if __name__ == '__main__':
    main()
