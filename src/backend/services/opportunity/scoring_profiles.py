from enum import Enum

class ScoringProfile(str, Enum):
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"     # Default
    AGGRESSIVE = "aggressive"