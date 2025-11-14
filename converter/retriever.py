"""Recuperador que usa o índice invertido para retornar os chunks mais relevantes.

Funções:
- retrieve_top_chunks(out_dir, index_path, query, top_k): retorna lista de dicionários
  com o texto e metadados (filename, json, doc_pos, chunk_index, char_count, score)
"""
from pathlib import Path
import json
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def retrieve_top_chunks(out_dir: Path, index_path: Path, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    out_dir = Path(out_dir)
    index_path = Path(index_path)
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            idx = json.load(f)
    except Exception as e:
        logger.error(f"Falha ao ler índice {index_path}: {e}")
        return []

    postings = idx.get("postings", {})
    # Use indexer.query_index-like logic but avoid re-loading indexer
    # Normalize query tokens simply by splitting on non-word
    import re
    tokens = re.findall(r"\w+", query.lower())
    if not tokens:
        return []

    scores = {}
    for term in tokens:
        for ref in postings.get(term, []):
            key = f"{ref['json']}|{ref['doc_pos']}|{ref.get('chunk_index',0)}"
            if key not in scores:
                scores[key] = {**ref, "score": 0}
            scores[key]["score"] += int(ref.get("occurrences", 1))

    ranked = sorted(scores.values(), key=lambda r: r.get("score", 0), reverse=True)[:top_k]

    results: List[Dict[str, Any]] = []
    for r in ranked:
        jf = Path(out_dir) / r["json"]
        try:
            with open(jf, "r", encoding="utf-8") as f:
                batch = json.load(f)
        except Exception as e:
            logger.warning(f"Falha ao abrir {jf}: {e}")
            continue

        docs = batch.get("documents", [])
        doc_pos = int(r.get("doc_pos", 0))
        if doc_pos < 0 or doc_pos >= len(docs):
            continue
        doc = docs[doc_pos]
        results.append({
            "text": doc.get("text", ""),
            "filename": doc.get("filename"),
            "json": r.get("json"),
            "doc_pos": doc_pos,
            "chunk_index": r.get("chunk_index", 0),
            "char_count": doc.get("char_count", len(doc.get("text", ""))),
            "score": r.get("score", 0),
        })

    return results
