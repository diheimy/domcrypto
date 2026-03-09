import logging

logger = logging.getLogger("DepthCalc")

class DepthCalculator:
    """
    F5.2 - Simula execução em profundidade para descobrir o 'Capacity' da oportunidade.
    Versão Calibrada: Flags descritivas e proteção contra falsos positivos.
    """
    
    # Thresholds
    MIN_EXEC_USD = 1000.0  # Mínimo para considerar "saudável"
    MAX_SLIPPAGE_TOLERANCE = 2.0 # % de slippage máximo tolerável antes de marcar TRAP
    
    @staticmethod
    def calculate(spot_book, fut_book, usd_target, fee_pct=0.2):
        """
        Calcula o sweep (varredura) do book de ordens para preencher um usd_target específico.
        Retorna informações detalhadas sobre os níveis de preço e volumes preenchidos.

        Args:
            spot_book (list): Livro de ofertas SPOT (asks para compra). Formato: [[price, qty], ...]
            fut_book (list): Livro de ofertas FUT (bids para venda). Formato: [[price, qty], ...]
            usd_target (float): O valor em USD que se deseja preencher em cada perna.
            fee_pct (float): Percentual de taxa para cálculo do spread líquido.

        Returns:
            dict: Um dicionário contendo as informações de sweep para 'spot' e 'fut',
                  e um 'fill_status'.
                  Ex: {
                        "spot": {"levels": 3, "px_start": 0.24456, "px_limit": 0.24460, "filled_usd": 500},
                        "fut":  {"levels": 4, "px_start": 0.24480, "px_limit": 0.24475, "filled_usd": 500},
                        "fill_status": "OK" | "THIN" | "NO_DEPTH"
                      }
        """
        # Inicialização dos resultados
        result = {
            "spot": {"levels": 0, "px_start": 0.0, "px_limit": 0.0, "filled_usd": 0.0},
            "fut":  {"levels": 0, "px_start": 0.0, "px_limit": 0.0, "filled_usd": 0.0},
            "fill_status": "NO_DEPTH"
        }

        if usd_target <= 0:
            logger.warning("usd_target deve ser maior que zero.")
            return result
            
        if not spot_book or not fut_book:
            logger.info("Books de ordens vazios.")
            return result

        # Simulação para a perna SPOT (compra)
        spot_filled_usd, spot_px_start, spot_px_limit, spot_levels = \
            DepthCalculator._simulate_single_leg(spot_book, usd_target, "buy")

        # Simulação para a perna FUT (venda)
        fut_filled_usd, fut_px_start, fut_px_limit, fut_levels = \
            DepthCalculator._simulate_single_leg(fut_book, usd_target, "sell")

        # Atualiza o dicionário de resultados
        result["spot"].update({
            "levels": spot_levels,
            "px_start": spot_px_start,
            "px_limit": spot_px_limit,
            "filled_usd": spot_filled_usd
        })
        result["fut"].update({
            "levels": fut_levels,
            "px_start": fut_px_start,
            "px_limit": fut_px_limit,
            "filled_usd": fut_filled_usd
        })

        # Determina o fill_status
        if spot_filled_usd >= usd_target and fut_filled_usd >= usd_target:
            result["fill_status"] = "OK"
        elif spot_filled_usd > 0 or fut_filled_usd > 0: # Pelo menos uma perna tem alguma profundidade
            result["fill_status"] = "THIN"
        else:
            result["fill_status"] = "NO_DEPTH"
            
        return result

    @staticmethod
    def _simulate_single_leg(book, usd_target, side):
        """
        Simula a execução de uma única perna (compra ou venda) até atingir o usd_target.

        Args:
            book (list): Livro de ofertas da perna. Formato: [[price, qty], ...]
            usd_target (float): O valor em USD que se deseja preencher.
            side (str): "buy" ou "sell" para determinar a lógica de px_start/px_limit.

        Returns:
            tuple: (filled_usd, px_start, px_limit, levels)
        """
        filled_usd = 0.0
        px_start = 0.0
        px_limit = 0.0
        levels = 0
        current_book_idx = 0

        if not book:
            return filled_usd, px_start, px_limit, levels

        px_start = float(book[0][0]) # O primeiro preço é sempre o px_start

        while current_book_idx < len(book) and filled_usd < usd_target:
            p, q = book[current_book_idx]
            level_usd = p * q

            if filled_usd + level_usd <= usd_target:
                # Consome o nível inteiro
                filled_usd += level_usd
                px_limit = p # Atualiza o px_limit com o preço do último nível consumido
                levels += 1
            else:
                # Consome apenas uma parte do nível para atingir o target
                remaining_usd_to_fill = usd_target - filled_usd
                
                # Para evitar divisão por zero, verifica se o preço é válido
                if p > 0:
                    qty_to_fill = remaining_usd_to_fill / p
                    filled_usd += qty_to_fill * p
                    px_limit = p # O px_limit é o preço deste nível, pois foi parcialmente consumido
                    levels += 1 # Conta este nível como parcialmente utilizado
                else:
                    # Se o preço for zero ou inválido, não podemos preencher mais com este nível
                    break
            
            current_book_idx += 1

        # Ajuste para px_limit se o target não foi completamente preenchido e px_limit não foi setado
        if filled_usd < usd_target and px_limit == 0.0 and px_start != 0.0:
             px_limit = px_start # Se não preencheu, o limit é o start

        # Garante que se nada foi preenchido, os preços limites são 0
        if filled_usd == 0:
            px_start = 0.0
            px_limit = 0.0

        return filled_usd, px_start, px_limit, levels