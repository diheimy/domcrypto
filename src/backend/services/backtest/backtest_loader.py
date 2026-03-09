import json
import os
from typing import List, Dict, Any

class BacktestLoader:
    """
    Carrega dados históricos para o motor de replay.
    """

    @staticmethod
    def load_from_json(file_path: str) -> List[Dict[str, Any]]:
        """
        Lê um arquivo JSON contendo uma lista de estados de mercado (frames).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset não encontrado: {file_path}")

        print(f"📂 Carregando dataset: {file_path}...")
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("O Dataset deve ser uma LISTA de frames (snapshots do mercado).")

        print(f"✅ Carregado: {len(data)} frames de mercado.")
        return data