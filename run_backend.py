#!/usr/bin/env python
"""
Script para inicializar o backend DomCrypto.
Executar a partir da raiz do projeto.
"""

import sys
import os

# Adicionar a raiz do projeto ao PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')

if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Agora importar e rodar o backend
from backend.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
