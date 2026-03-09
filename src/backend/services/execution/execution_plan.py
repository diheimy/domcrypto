class ExecutionPlanBuilder:
    """F7.2 - Construtor de Plano de Fatiamento (Slicing)"""
    @staticmethod
    def build(op):
        total_usd = getattr(op, 'order_recommend_usd', 0)
        if total_usd <= 0:
            return []
            
        # Divide em fatias de max 25% da ordem ou $500
        slice_usd = min(total_usd * 0.25, 500)
        slices = []
        
        remaining = total_usd
        while remaining > 0.01: # Margem de arredondamento
            current = min(slice_usd, remaining)
            slices.append(current)
            remaining -= current
            
        return slices