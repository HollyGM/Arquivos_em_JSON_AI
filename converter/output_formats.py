"""Módulo para diferentes formatos de saída.

Funcionalidades:
- Conversão de JSON para TXT
- Conversão de JSON para PDF
- Formatação de dados para diferentes saídas
"""
from pathlib import Path
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
except ImportError:
    SimpleDocTemplate = None
    Paragraph = None
    getSampleStyleSheet = None

logger = logging.getLogger(__name__)


def json_to_txt(json_data: Dict[str, Any], output_path: str = None) -> str:
    """Converte dados JSON para formato TXT legível.
    
    Args:
        json_data: Dados JSON para converter
        output_path: Caminho de saída (opcional)
    
    Returns:
        Caminho do arquivo TXT criado
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"output_{timestamp}.txt"
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # Cabeçalho
        f.write("=" * 80 + "\n")
        f.write("RELATÓRIO DE DOCUMENTOS PROCESSADOS\n")
        f.write("=" * 80 + "\n\n")
        
        # Informações do batch
        if 'batch_id' in json_data:
            f.write(f"ID do Lote: {json_data['batch_id']}\n")
        if 'created_at' in json_data:
            f.write(f"Criado em: {json_data['created_at']}\n")
        
        f.write(f"Total de documentos: {len(json_data.get('documents', []))}\n\n")
        
        # Documentos
        for i, doc in enumerate(json_data.get('documents', []), 1):
            f.write("-" * 80 + "\n")
            f.write(f"DOCUMENTO {i}\n")
            f.write("-" * 80 + "\n")
            
            # Metadados
            if 'filename' in doc:
                f.write(f"Arquivo: {doc['filename']}\n")
            if 'filetype' in doc:
                f.write(f"Tipo: {doc['filetype']}\n")
            if 'source_path' in doc:
                f.write(f"Caminho: {doc['source_path']}\n")
            if 'char_count' in doc:
                f.write(f"Caracteres: {doc['char_count']}\n")
            if 'chunk_index' in doc:
                f.write(f"Chunk: {doc['chunk_index']}\n")
            
            f.write("\n")
            
            # Conteúdo
            f.write("CONTEÚDO:\n")
            f.write("-" * 40 + "\n")
            text = doc.get('text', '')
            if text:
                f.write(text)
                f.write("\n\n")
            else:
                f.write("(Sem conteúdo de texto)\n\n")
    
    logger.info(f"Arquivo TXT criado: {output_path}")
    return str(output_path)


def json_to_pdf(json_data: Dict[str, Any], output_path: str = None) -> str:
    """Converte dados JSON para formato PDF.
    
    Args:
        json_data: Dados JSON para converter
        output_path: Caminho de saída (opcional)
    
    Returns:
        Caminho do arquivo PDF criado
    
    Raises:
        RuntimeError: Se dependências não estão instaladas
    """
    if not SimpleDocTemplate:
        raise RuntimeError(
            "Dependência reportlab não encontrada. Instale: pip install reportlab"
        )
    
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"output_{timestamp}.pdf"
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Criar documento PDF
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1,  # Center
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    content = []
    
    # Título
    content.append(Paragraph("RELATÓRIO DE DOCUMENTOS PROCESSADOS", title_style))
    content.append(Spacer(1, 12))
    
    # Informações do batch
    if 'batch_id' in json_data:
        content.append(Paragraph(f"<b>ID do Lote:</b> {json_data['batch_id']}", styles['Normal']))
    if 'created_at' in json_data:
        content.append(Paragraph(f"<b>Criado em:</b> {json_data['created_at']}", styles['Normal']))
    
    content.append(Paragraph(f"<b>Total de documentos:</b> {len(json_data.get('documents', []))}", styles['Normal']))
    content.append(Spacer(1, 20))
    
    # Documentos
    for i, doc in enumerate(json_data.get('documents', []), 1):
        content.append(Paragraph(f"DOCUMENTO {i}", heading_style))
        
        # Metadados
        metadata = []
        if 'filename' in doc:
            metadata.append(f"<b>Arquivo:</b> {doc['filename']}")
        if 'filetype' in doc:
            metadata.append(f"<b>Tipo:</b> {doc['filetype']}")
        if 'source_path' in doc:
            metadata.append(f"<b>Caminho:</b> {doc['source_path']}")
        if 'char_count' in doc:
            metadata.append(f"<b>Caracteres:</b> {doc['char_count']}")
        if 'chunk_index' in doc:
            metadata.append(f"<b>Chunk:</b> {doc['chunk_index']}")
        
        for meta in metadata:
            content.append(Paragraph(meta, styles['Normal']))
        
        content.append(Spacer(1, 12))
        
        # Conteúdo
        content.append(Paragraph("<b>CONTEÚDO:</b>", styles['Normal']))
        text = doc.get('text', '')
        if text:
            # Dividir texto longo em parágrafos
            paragraphs = text.split('\\n\\n')
            for para in paragraphs:
                if para.strip():
                    # Escapar caracteres especiais para XML
                    para_escaped = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    content.append(Paragraph(para_escaped, styles['Normal']))
                    content.append(Spacer(1, 6))
        else:
            content.append(Paragraph("(Sem conteúdo de texto)", styles['Italic']))
        
        # Quebra de página entre documentos (exceto o último)
        if i < len(json_data.get('documents', [])):
            content.append(PageBreak())
    
    # Construir PDF
    doc.build(content)
    
    logger.info(f"Arquivo PDF criado: {output_path}")
    return str(output_path)


def convert_json_files(
    json_dir: str,
    output_format: str = 'txt',
    output_dir: str = None,
    json_files: Optional[List[str]] = None,
) -> List[str]:
    """Converte múltiplos arquivos JSON para o formato especificado.
    
    Args:
        json_dir: Diretório contendo arquivos JSON
        output_format: Formato de saída ('txt' ou 'pdf')
        output_dir: Diretório de saída (opcional)
    
    Returns:
        Lista de caminhos dos arquivos convertidos
    """
    json_dir = Path(json_dir)

    if output_dir is None:
        output_dir = json_dir / f"converted_{output_format}"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    converted_files = []
    if json_files:
        file_candidates = [Path(p) for p in json_files if Path(p).is_file()]
    else:
        file_candidates = [p for p in json_dir.rglob("*.json") if p.is_file()]
    
    if not file_candidates:
        logger.warning(f"Nenhum arquivo JSON encontrado em {json_dir}")
        return converted_files
    
    for json_file in sorted(file_candidates):
        try:
            logger.info(f"Convertendo {json_file.name} para {output_format.upper()}")
            
            # Carregar dados JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Definir arquivo de saída
            output_name = f"{json_file.stem}.{output_format}"
            output_path = output_dir / output_name
            
            # Converter
            if output_format.lower() == 'txt':
                result_path = json_to_txt(json_data, str(output_path))
            elif output_format.lower() == 'pdf':
                result_path = json_to_pdf(json_data, str(output_path))
            else:
                logger.error(f"Formato não suportado: {output_format}")
                continue
            
            converted_files.append(result_path)
            
        except Exception as e:
            logger.error(f"Erro convertendo {json_file}: {e}")
            continue
    
    logger.info(f"Conversão concluída. {len(converted_files)} arquivos convertidos.")
    return converted_files