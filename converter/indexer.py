"""Indexador simples para acelerar localização de trechos de texto.

Estratégia:
- Construir um inverted index (termo -> lista de referências)
- Cada referência contém: arquivo JSON, posição do documento no batch, chunk_index, filename e contagem de ocorrências
- Salvar índice em JSON em out_dir/index.json
- Fornecer função de consulta simples baseada em contagem de termos coincidentes

Este indexador é leve (não embeddings) e melhora muito a filtragem inicial de trechos
relevantes antes de enviar conteúdo ao modelo AI.
"""
from pathlib import Path
import json
import re
from collections import defaultdict, Counter
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def _normalize(text: str) -> List[str]:
    if not text:
        return []
    tokens = _TOKEN_RE.findall(text.lower())
    return tokens


def build_index(out_dir: Path, json_files: List[str]) -> Path:
    """Constrói e salva um índice invertido a partir dos arquivos JSON gerados.

    Args:
        out_dir: diretório onde salvar o índice
        json_files: lista de caminhos (strings) para os arquivos JSON gerados

    Returns:
        Path para o arquivo de índice salvo (out_dir/index.json)
    """
    out_dir = Path(out_dir)
    postings: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    total_docs = 0

    for jf in json_files:
        jf_path = out_dir / jf if not Path(jf).is_absolute() else Path(jf)
        try:
            with open(jf_path, "r", encoding="utf-8") as f:
                batch = json.load(f)
        except Exception as e:
            logger.warning(f"Falha ao ler JSON para indexação: {jf_path}: {e}")
            continue

        docs = batch.get("documents") or []
        for doc_pos, doc in enumerate(docs):
            total_docs += 1
            text = doc.get("text", "") or ""
            tokens = _normalize(text)
            if not tokens:
                continue
            counts = Counter(tokens)
            ref = {
                "json": str(jf_path.name),
                "doc_pos": doc_pos,
                "chunk_index": doc.get("chunk_index", 0),
                "filename": doc.get("filename"),
                "char_count": doc.get("char_count", len(text)),
            }
            for term, freq in counts.items():
                entry = dict(ref)
                entry["occurrences"] = freq
                postings[term].append(entry)

    index = {
        "meta": {
            "total_docs_indexed": total_docs,
        },
        "postings": postings,
    }

    idx_path = out_dir / "index.json"
    # Convert defaultdict to normal dict for JSON serialization
    serializable = {k: v for k, v in postings.items()}
    out_obj = {"meta": index["meta"], "postings": serializable}
    try:
        with open(idx_path, "w", encoding="utf-8") as f:
            json.dump(out_obj, f, ensure_ascii=False, indent=2)
        logger.info(f"Índice salvo em {idx_path} (termos: {len(serializable)})")
    except Exception as e:
        logger.exception(f"Erro ao salvar índice em {idx_path}: {e}")
        raise

    return idx_path


def query_index(index_path: Path, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Consulta o índice e retorna referências ordenadas por score simples.

    Score: soma das ocorrências dos termos da query em cada referência.
    """
    index_path = Path(index_path)
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            idx = json.load(f)
    except Exception as e:
        logger.error(f"Falha ao ler índice {index_path}: {e}")
        return []

    postings = idx.get("postings", {})
    terms = _normalize(query)
    scores: Dict[str, Dict[str, Any]] = {}

    for term in terms:
        for ref in postings.get(term, []):
            key = f"{ref['json']}|{ref['doc_pos']}|{ref.get('chunk_index',0)}"
            if key not in scores:
                scores[key] = {**ref, "score": 0}
            scores[key]["score"] += int(ref.get("occurrences", 1))

    # Ordenar por score desc e retornar top_k
    ranked = sorted(scores.values(), key=lambda r: r.get("score", 0), reverse=True)
    return ranked[:top_k]
