"""
Registro institucional de fees por exchange.
Valores em percentual (%).
Modo MVP: Taker fixo.
"""

FEE_REGISTRY = {
    "mexc": {
        "spot": 0.10,
        "futures": 0.04,
    },
    "gate": {
        "spot": 0.20,
        "futures": 0.05,
    },
    "bitget": {
        "spot": 0.10,
        "futures": 0.06,
    },
    "bingx": {
        "spot": 0.10,
        "futures": 0.06,
    }
}

DEFAULT_FEE = {
    "spot": 0.20,
    "futures": 0.10,
}