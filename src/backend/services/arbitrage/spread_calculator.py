def calculate_spread(spot_price: float, futures_price: float) -> float:
    if spot_price == 0:
        return 0.0
    return ((futures_price - spot_price) / spot_price) * 100