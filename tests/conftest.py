import sys
from pathlib import Path

# Adiciona o diretório raiz do projeto ao sys.path
# para que os módulos em 'converter' possam ser encontrados pelos testes.
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
