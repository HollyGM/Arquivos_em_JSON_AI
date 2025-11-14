"""Indexador baseado em TF-IDF para busca de texto relevante.

Estratégia:
- Usa TfidfVectorizer do scikit-learn para criar uma representação numérica dos textos.
- Constrói uma matriz TF-IDF onde cada linha é um chunk de documento.
- Salva o `vectorizer` treinado, a matriz TF-IDF e os metadados dos chunks.
- A consulta é feita transformando a query com o mesmo vectorizer e calculando
  a similaridade de cosseno com todos os chunks para encontrar os mais relevantes.
"""
from pathlib import Path
import json
import joblib
from typing import List, Dict, Any
import logging

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    TfidfVectorizer = None
    cosine_similarity = None


logger = logging.getLogger(__name__)


def build_index(out_dir: Path, json_files: List[str]) -> Path:
    """Constrói e salva um índice TF-IDF a partir dos arquivos JSON gerados.

    Salva três arquivos no diretório de índice:
    - `tfidf_vectorizer.joblib`: O objeto TfidfVectorizer treinado.
    - `tfidf_matrix.joblib`: A matriz TF-IDF esparsa.
    - `metadata.json`: Uma lista de metadados para cada documento/chunk.

    Args:
        out_dir: Diretório onde salvar o índice.
        json_files: Lista de caminhos para os arquivos JSON.

    Returns:
        Path para o diretório do índice.
    """
    if TfidfVectorizer is None:
        raise RuntimeError("scikit-learn não está instalado. Execute: pip install scikit-learn")

    # Nome mais descritivo para o diretório do índice
    index_dir = out_dir / "indice_busca_tfidf"
    index_dir.mkdir(exist_ok=True)

    corpus = []
    metadata = []
    
    for jf_name in json_files:
        jf_path = out_dir / jf_name if not Path(jf_name).is_absolute() else Path(jf_name)
        try:
            with open(jf_path, "r", encoding="utf-8") as f:
                batch = json.load(f)
        except Exception as e:
            logger.warning(f"Falha ao ler JSON para indexação: {jf_path}: {e}")
            continue

        for doc_pos, doc in enumerate(batch.get("documents", [])):
            corpus.append(doc.get("text", ""))
            metadata.append({
                "json_file": jf_path.name,
                "doc_pos": doc_pos,
                "chunk_index": doc.get("chunk_index", 0),
                "filename": doc.get("filename"),
                "char_count": doc.get("char_count", len(doc.get("text", ""))),
            })

    if not corpus:
        logger.warning("Nenhum texto encontrado para indexar.")
        return index_dir

    # Configura o vectorizer TF-IDF
    # Ajustamos os parâmetros para funcionar com qualquer tamanho de corpus
    num_docs = len(corpus)
    
    # Para corpus muito pequenos (1-2 documentos), ajustamos max_df e min_df
    if num_docs == 1:
        max_df_value = 1.0
        min_df_value = 1
    elif num_docs == 2:
        max_df_value = 1.0
        min_df_value = 1
    else:
        # Para corpus maiores, usamos configurações mais restritivas
        max_df_value = 0.85
        min_df_value = 1
    
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2), 
        max_df=max_df_value, 
        min_df=min_df_value, 
        stop_words=None # Pode ser personalizado com uma lista de stop words
    )
    
    logger.info(f"Criando matriz TF-IDF para {num_docs} documentos...")
    tfidf_matrix = vectorizer.fit_transform(corpus)
    logger.info(f"Matriz criada com shape: {tfidf_matrix.shape}")

    # Salvar os artefatos do índice
    try:
        joblib.dump(vectorizer, index_dir / "tfidf_vectorizer.joblib")
        joblib.dump(tfidf_matrix, index_dir / "tfidf_matrix.joblib")
        with open(index_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        logger.info(f"Índice TF-IDF salvo em {index_dir}")
    except Exception as e:
        logger.exception(f"Erro ao salvar índice TF-IDF: {e}")
        raise

    return index_dir


def query_index(index_dir: Path, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Consulta o índice TF-IDF e retorna os chunks mais relevantes.

    Args:
        index_dir: Diretório onde o índice TF-IDF está salvo.
        query: A string de busca.
        top_k: O número de resultados a retornar.

    Returns:
        Uma lista de dicionários, cada um contendo o metadado do chunk e o score de similaridade.
    """
    if cosine_similarity is None:
        raise RuntimeError("scikit-learn não está instalado.")

    try:
        vectorizer = joblib.load(index_dir / "tfidf_vectorizer.joblib")
        tfidf_matrix = joblib.load(index_dir / "tfidf_matrix.joblib")
        with open(index_dir / "metadata.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)
    except FileNotFoundError:
        logger.error(f"Índice não encontrado em {index_dir}. Execute a indexação primeiro.")
        return []
    except Exception as e:
        logger.exception(f"Erro ao carregar índice de {index_dir}: {e}")
        return []

    if not query.strip():
        return []

    # Transformar a query usando o mesmo vectorizer
    query_vector = vectorizer.transform([query])

    # Calcular similaridade de cosseno
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()

    # Obter os top_k resultados
    # argsort retorna os índices do menor para o maior, então pegamos os últimos k e invertemos
    relevant_indices = cosine_similarities.argsort()[-top_k:][::-1]

    results = []
    for i in relevant_indices:
        # Ignorar resultados com score muito baixo
        if cosine_similarities[i] > 0.01:
            result = metadata[i]
            result["score"] = float(cosine_similarities[i])
            results.append(result)
            
    return results
