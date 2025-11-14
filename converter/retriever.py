"""Recuperador que usa o índice TF-IDF para retornar os chunks mais relevantes.

Funções:
- retrieve_top_chunks(out_dir, index_dir, query, top_k): retorna lista de dicionários
  com o texto e metadados dos chunks mais relevantes.
"""
from pathlib import Path
import json
from typing import List, Dict, Any
import logging
from . import indexer

logger = logging.getLogger(__name__)


def retrieve_top_chunks(out_dir: Path, index_dir: Path, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Consulta o índice TF-IDF, recupera os chunks mais relevantes e retorna seu conteúdo.

    Args:
        out_dir: O diretório onde os arquivos JSON dos batches estão.
        index_dir: O diretório onde o índice TF-IDF foi salvo.
        query: A string de busca.
        top_k: O número de chunks a retornar.

    Returns:
        Uma lista de dicionários, cada um contendo o texto e metadados do chunk.
    """
    out_dir = Path(out_dir)
    index_dir = Path(index_dir)

    # 1. Consultar o índice para obter as referências dos chunks mais relevantes
    try:
        ranked_refs = indexer.query_index(index_dir, query, top_k)
    except Exception as e:
        logger.error(f"Falha ao consultar o índice em {index_dir}: {e}")
        return []

    if not ranked_refs:
        return []

    # 2. Carregar o texto dos chunks a partir dos arquivos JSON
    results: List[Dict[str, Any]] = []
    
    # Cache para evitar reabrir o mesmo arquivo JSON várias vezes
    json_cache: Dict[str, Dict] = {}

    for ref in ranked_refs:
        json_filename = ref.get("json_file")
        if not json_filename:
            continue

        try:
            # Carregar o batch JSON do cache ou do disco
            if json_filename not in json_cache:
                jf_path = out_dir / json_filename
                with open(jf_path, "r", encoding="utf-8") as f:
                    json_cache[json_filename] = json.load(f)
            
            batch = json_cache[json_filename]
            
            docs = batch.get("documents", [])
            doc_pos = int(ref.get("doc_pos", -1))

            if 0 <= doc_pos < len(docs):
                doc = docs[doc_pos]
                # Montar o resultado final com texto e metadados
                results.append({
                    "text": doc.get("text", ""),
                    "filename": doc.get("filename"),
                    "json_file": json_filename,
                    "doc_pos": doc_pos,
                    "chunk_index": doc.get("chunk_index", 0),
                    "char_count": doc.get("char_count", 0),
                    "score": ref.get("score", 0.0),
                })
            else:
                logger.warning(f"Posição de documento inválida {doc_pos} para o arquivo {json_filename}")

        except FileNotFoundError:
            logger.warning(f"Arquivo JSON referenciado pelo índice não encontrado: {json_filename}")
        except Exception as e:
            logger.warning(f"Falha ao processar referência para {json_filename}: {e}")

    return results
