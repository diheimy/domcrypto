import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from src.backend.pipeline.opportunity_pipeline import OpportunityPipeline
from src.backend.api.adapters.opportunity_ui_adapter import OpportunityUIAdapter

router = APIRouter()
logger = logging.getLogger("WebSocket")

@router.websocket("/ws/opportunities")
async def websocket_endpoint(
    websocket: WebSocket,
    exchanges: str = Query(None),
    min_vol: float = Query(0)
):
    await websocket.accept()
    
    pipeline = OpportunityPipeline()

    try:
        while True:
            # 1. Executa Pipeline
            opportunities = await pipeline.run()

            # 2. Filtros de Servidor
            filtered_ops = []
            target_exchanges = exchanges.split(",") if exchanges else []
            
            for op in opportunities:
                if op.volume_24h_usd < min_vol:
                    continue

                if target_exchanges:
                    spot_ok = op.exchange_spot in target_exchanges
                    fut_ok = (op.exchange_futures + "_futures") in target_exchanges
                    
                    # CORREÇÃO DO BUG LÓGICO: pass -> continue
                    if not (spot_ok or fut_ok):
                        continue 

                filtered_ops.append(op)

            # 3. Serialização via Adapter
            try:
                # CORREÇÃO CRÍTICA: .to_dict() direto do modelo (Adapter incompleto)
                data = [op.to_dict() for op in filtered_ops]
            except AttributeError as e:
                logger.error(f"Erro Serialização: {e}")
                data = []

            # 4. Envia
            if data:
                await websocket.send_json(data)
            else:
                await websocket.send_json([])

            await asyncio.sleep(3)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Erro WS: {e}")
        try:
            await websocket.close()
        except:
            pass