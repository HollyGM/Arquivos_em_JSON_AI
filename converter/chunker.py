"""Agrupa documentos em arquivos JSON respeitando um limite máximo de bytes por JSON.

Estratégia: iterar sobre documentos (cada doc é um dicionário com metadata + texto),
gerar chunks por tamanho aproximado (medido em bytes ao serializar em UTF-8)
e escrever arquivos JSON sequenciais.

Otimizações:
- Estimativa rápida de bytes sem serialização completa
- Divisão eficiente de documentos grandes
- Tratamento robusto de erros
"""
from pathlib import Path
import json
import uuid
from datetime import datetime
from typing import Iterable, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def _estimate_bytes(obj: Any) -> int:
    """Estima o tamanho em bytes de um objeto JSON.

    Usa serialização completa para garantir precisão.
    Para objetos grandes, isso pode ser otimizado com estimativas.
    """
    try:
        return len(json.dumps(obj, ensure_ascii=False).encode("utf-8"))
    except Exception as e:
        logger.error(f"Erro ao estimar bytes do objeto: {e}")
        # Estimativa conservadora
        return len(str(obj).encode("utf-8")) * 2


def chunk_and_write(documents: Iterable[Dict[str, Any]], out_dir: Path, max_size_bytes: int, embed_index: bool = False) -> List[str]:
    """Agrupa documentos em arquivos JSON respeitando limite de tamanho.

    Args:
        documents: Iterável de dicionários com documentos processados
        out_dir: Diretório de saída para os arquivos JSON
        max_size_bytes: Tamanho máximo em bytes por arquivo JSON

    Returns:
        Lista com caminhos dos arquivos JSON criados

    Raises:
        ValueError: Se max_size_bytes for muito pequeno (< 1024)
        OSError: Se houver problemas ao criar diretório ou escrever arquivos
    """
    if max_size_bytes < 1024:
        raise ValueError(f"max_size_bytes deve ser pelo menos 1024 bytes, recebido: {max_size_bytes}")

    out_dir = Path(out_dir)
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.error(f"Erro ao criar diretório de saída {out_dir}: {e}")
        raise

    batch = {
        "batch_id": str(uuid.uuid4()),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "documents": [],
    }
    current_size = _estimate_bytes(batch)  # base overhead
    file_index = 1
    created_files = []

    def flush_current():
        """Escreve o batch atual em arquivo e reseta para novo batch."""
        nonlocal batch, current_size, file_index, created_files
        if not batch["documents"]:
            return

        # Gerar nome mais descritivo baseado no primeiro documento do batch
        first_doc = batch["documents"][0]
        doc_name = first_doc.get("filename", "documento")
        # Remover extensão e caracteres problemáticos
        doc_name = Path(doc_name).stem
        doc_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in doc_name)
        doc_name = doc_name[:50]  # Limitar tamanho
        
        # Formato: batch_XXXX_nome-do-documento.json
        out_path = out_dir / f"batch_{file_index:04d}_{doc_name}.json"
        try:
            # Se solicitado, construir índice local para o batch antes de salvar
            if embed_index and batch.get("documents"):
                try:
                    # índice simples: termo -> lista de refs
                    from collections import defaultdict
                    import re
                    token_re = re.compile(r"\w+", re.UNICODE)
                    postings = defaultdict(list)
                    for pos, d in enumerate(batch.get("documents", [])):
                        text = d.get("text", "") or ""
                        tokens = token_re.findall(text.lower())
                        if not tokens:
                            continue
                        counts = {}
                        for t in tokens:
                            counts[t] = counts.get(t, 0) + 1
                        ref = {
                            "doc_pos": pos,
                            "chunk_index": d.get("chunk_index", 0),
                            "filename": d.get("filename"),
                            "char_count": d.get("char_count", len(text)),
                        }
                        for term, freq in counts.items():
                            entry = dict(ref)
                            entry["occurrences"] = freq
                            postings[term].append(entry)
                    batch["local_index"] = {k: v for k, v in postings.items()}
                except Exception:
                    logger.exception("Falha ao construir índice local para batch")

            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(batch, f, ensure_ascii=False, indent=2)
            created_files.append(str(out_path))
            logger.info(f"Arquivo JSON criado: {out_path} ({len(batch['documents'])} documentos)")
            file_index += 1
        except Exception as e:
            logger.error(f"Erro ao escrever arquivo {out_path}: {e}")
            raise

        # Reset para novo batch
        batch = {
            "batch_id": str(uuid.uuid4()),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "documents": [],
        }
        current_size = _estimate_bytes(batch)

    doc_count = 0
    for doc in documents:
        doc_count += 1
        # Cada doc pode ser grande; se um único doc > max_size_bytes, dividir em chunks menores
        doc_text = doc.get("text", "") or ""

        # Preparar metadata base
        base_meta = {k: doc.get(k) for k in ("source_path", "filename", "filetype")}

        # Adicionar ID único ao documento se não existir
        if "id" not in base_meta:
            base_meta["id"] = str(uuid.uuid4())

        # Se pequeno o suficiente para adicionar como está
        candidate = {**base_meta, "chunk_index": 0, "text": doc_text, "char_count": len(doc_text)}
        candidate_size = _estimate_bytes(candidate)

        if candidate_size > max_size_bytes:
            # Dividir documento grande em chunks menores
            logger.info(f"Documento {base_meta.get('filename', 'unknown')} é muito grande ({candidate_size} bytes), dividindo...")

            # Calcular tamanho aproximado por chunk
            approx_chars_per_chunk = max(1024, int(len(doc_text) * (max_size_bytes / max(candidate_size, 1))))
            idx = 0
            start = 0

            while start < len(doc_text):
                part = doc_text[start:start + approx_chars_per_chunk]
                candidate = {**base_meta, "chunk_index": idx, "text": part, "char_count": len(part)}
                cand_size = _estimate_bytes(candidate)

                # Se ainda muito grande, reduzir pela metade iterativamente
                shrink_attempts = 0
                while cand_size > max_size_bytes and len(part) > 100 and shrink_attempts < 10:
                    part = part[:len(part)//2]
                    candidate = {**base_meta, "chunk_index": idx, "text": part, "char_count": len(part)}
                    cand_size = _estimate_bytes(candidate)
                    shrink_attempts += 1

                if cand_size > max_size_bytes:
                    logger.warning(f"Chunk ainda muito grande após {shrink_attempts} tentativas. Usando mesmo assim.")

                # Verificar se adicionar cabe no JSON atual
                if current_size + cand_size > max_size_bytes and batch["documents"]:
                    flush_current()

                batch["documents"].append(candidate)
                current_size += cand_size
                idx += 1
                start += len(part)
        else:
            # Cabe como chunk único
            if current_size + candidate_size > max_size_bytes and batch["documents"]:
                flush_current()
            batch["documents"].append(candidate)
            current_size += candidate_size

    # Flush final para escrever documentos restantes
    flush_current()

    logger.info(f"Processamento concluído: {doc_count} documentos em {len(created_files)} arquivo(s) JSON")
    return created_files
