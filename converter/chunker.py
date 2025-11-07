"""Agrupa documentos em arquivos JSON respeitando um limite máximo de bytes por JSON.

Estratégia: iterar sobre documentos (cada doc é um dicionário com metadata + texto), gerar chunks por tamanho aproximado (medido em bytes ao serializar em UTF-8) e escrever arquivos JSON sequenciais.
"""
from pathlib import Path
import json
import uuid
from datetime import datetime
from typing import Iterable, Dict, Any


def _estimate_bytes(obj: Any) -> int:
    return len(json.dumps(obj, ensure_ascii=False).encode("utf-8"))


def chunk_and_write(documents: Iterable[Dict[str, Any]], out_dir: Path, max_size_bytes: int):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    batch = {
        "batch_id": str(uuid.uuid4()),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "documents": [],
    }
    current_size = _estimate_bytes(batch)  # base overhead
    file_index = 1
    created_files = []

    def flush_current():
        nonlocal batch, current_size, file_index, created_files
        if not batch["documents"]:
            return
        out_path = out_dir / f"output_{file_index:04d}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(batch, f, ensure_ascii=False, indent=2)
        created_files.append(str(out_path))
        file_index += 1
        # reset
        batch = {
            "batch_id": str(uuid.uuid4()),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "documents": [],
        }
        current_size = _estimate_bytes(batch)

    for doc in documents:
        # each doc may be big; if single doc > max_size_bytes, we will split by characters into smaller chunks
        doc_text = doc.get("text", "") or ""
        # prepare metadata base
        base_meta = {k: doc.get(k) for k in ("source_path", "filename", "filetype")}

        # If small enough to add as is
        candidate = {**base_meta, "chunk_index": 0, "text": doc_text, "char_count": len(doc_text)}
        candidate_size = _estimate_bytes(candidate)
        if candidate_size > max_size_bytes:
            # split by characters approximating bytes
            approx_chars_per_chunk = max(1024, int(len(doc_text) * (max_size_bytes / max(candidate_size, 1))))
            idx = 0
            start = 0
            while start < len(doc_text):
                part = doc_text[start:start + approx_chars_per_chunk]
                candidate = {**base_meta, "chunk_index": idx, "text": part, "char_count": len(part)}
                cand_size = _estimate_bytes(candidate)
                # If still too large, shrink
                while cand_size > max_size_bytes and len(part) > 100:
                    part = part[:len(part)//2]
                    candidate = {**base_meta, "chunk_index": idx, "text": part, "char_count": len(part)}
                    cand_size = _estimate_bytes(candidate)
                # check if adding fits current JSON
                if current_size + cand_size > max_size_bytes and batch["documents"]:
                    flush_current()
                batch["documents"].append(candidate)
                current_size += cand_size
                idx += 1
                start += len(part)
        else:
            # fits as single chunk
            if current_size + candidate_size > max_size_bytes and batch["documents"]:
                flush_current()
            batch["documents"].append(candidate)
            current_size += candidate_size

    # final flush
    flush_current()
    return created_files
