import pytest
from pathlib import Path
import json
import shutil
from converter import indexer

# Amostra de documentos para os testes
DOCS_SAMPLE = [
    {"text": "A raposa marrom rápida pula sobre o cão preguiçoso."},
    {"text": "O cão preguiçoso dorme o dia todo."},
    {"text": "A inteligência artificial está transformando o mundo."},
    {"text": "O processamento de linguagem natural é um campo da inteligência artificial."}
]

@pytest.fixture
def temp_output_dir(tmp_path):
    """Cria um diretório de saída temporário para os testes."""
    output_dir = tmp_path / "test_output"
    output_dir.mkdir()
    
    # Criar arquivos JSON de amostra
    json_files = []
    for i, doc in enumerate(DOCS_SAMPLE):
        batch = {
            "batch_id": f"batch_{i}",
            "documents": [{
                "text": doc["text"],
                "filename": f"doc_{i}.txt",
                "chunk_index": 0,
                "char_count": len(doc["text"]),
                "doc_pos": 0 
            }]
        }
        json_path = output_dir / f"output_{i+1:04d}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(batch, f)
        json_files.append(json_path.name)
        
    yield output_dir, json_files
    
    # Limpeza
    shutil.rmtree(output_dir)

def test_build_tfidf_index(temp_output_dir):
    """Testa se a construção do índice TF-IDF cria os arquivos esperados."""
    output_dir, json_files = temp_output_dir
    
    index_dir = indexer.build_index(output_dir, json_files)
    
    assert index_dir.is_dir()
    assert (index_dir / "tfidf_vectorizer.joblib").exists()
    assert (index_dir / "tfidf_matrix.joblib").exists()
    assert (index_dir / "metadata.json").exists()

    with open(index_dir / "metadata.json", "r") as f:
        metadata = json.load(f)
    assert len(metadata) == len(DOCS_SAMPLE)
    assert metadata[0]["filename"] == "doc_0.txt"

def test_query_tfidf_index(temp_output_dir):
    """Testa a consulta ao índice TF-IDF."""
    output_dir, json_files = temp_output_dir
    index_dir = indexer.build_index(output_dir, json_files)
    
    # Query que deve ter alta similaridade com os documentos 2 e 3
    query = "inteligência artificial e linguagem"
    results = indexer.query_index(index_dir, query, top_k=2)
    
    assert len(results) == 2
    
    # O primeiro resultado deve ser o mais relevante.
    # Usamos pytest.approx para evitar falhas por pequenas diferenças de ponto flutuante.
    assert results[0]["score"] >= results[1]["score"]
    
    # Verificar se os documentos corretos foram retornados (a ordem pode variar se os scores forem idênticos)
    returned_filenames = {res["filename"] for res in results}
    expected_filenames = {"doc_2.txt", "doc_3.txt"}
    assert returned_filenames == expected_filenames

    # Verificar a estrutura do resultado
    first_result = results[0]
    assert "filename" in first_result
    assert "score" in first_result
    assert "json_file" in first_result
    assert "doc_pos" in first_result

def test_query_with_no_match(temp_output_dir):
    """Testa uma consulta que não deve encontrar resultados."""
    output_dir, json_files = temp_output_dir
    index_dir = indexer.build_index(output_dir, json_files)
    
    query = "termo inexistente xyz"
    results = indexer.query_index(index_dir, query, top_k=5)
    
    assert len(results) == 0
