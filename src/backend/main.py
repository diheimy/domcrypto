import asyncio
import logging
import json
import math
import time
import os
from contextlib import asynccontextmanager, suppress
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Query, HTTPException
from starlette.websockets import WebSocketState
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# --- Imports do Core ---
from src.backend.services.risk.portfolio_state import PortfolioRiskState
from src.backend.services.execution.execution_engine import ExecutionEngine
from src.backend.pipeline.opportunity_pipeline import OpportunityPipeline
from src.backend.api import routes

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DomArb-v2")


def _json_sanitize(obj):
    """Recursively sanitize objects so payload is strict JSON.

    - Converte NaN/Infinity em None (JSON null)
    - Converte datetime-like via .timestamp() quando for detectável
    - Evita derrubar o broadcast por tipos não serializáveis
    """
    try:
        # Fast path for common primitives
        if obj is None or isinstance(obj, (str, bool, int)):
            return obj
        if isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return None
            return obj
        if isinstance(obj, dict):
            return {str(k): _json_sanitize(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple, set)):
            return [_json_sanitize(v) for v in obj]
    except Exception:
        return None

    # Fallback: try to coerce
    try:
        if hasattr(obj, "timestamp") and callable(getattr(obj, "timestamp")):
            # datetime
            return float(obj.timestamp())
        if hasattr(obj, "dict") and callable(getattr(obj, "dict")):
            return _json_sanitize(obj.dict())
    except Exception:
        pass
    try:
        return str(obj)
    except Exception:
        return None

# --- Globais ---
pipeline = None
risk_state = None
execution_engine = None
scanner_lock = asyncio.Lock()

# Ciclo incremental para telemetria.
_CYCLE_ID = 0

# --- Gerenciador de WebSocket ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"🔌 Cliente conectado. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"❌ Cliente desconectado. Total: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        disconnected = []
        for connection in list(self.active_connections):
            try:
                # `WebSocketState` vem de starlette.websockets
                state = getattr(connection, "client_state", None) or getattr(connection, "application_state", None)
                if state is not None and state != WebSocketState.CONNECTED:
                    disconnected.append(connection)
                    continue
                await connection.send_text(message)
                logger.debug("📤 WS enviado para 1 cliente.")
            except Exception as e:
                logger.warning(f"Erro no broadcast (desconectando cliente): {repr(e)}")
                disconnected.append(connection)

        for connection in disconnected:
            self.disconnect(connection)

        logger.info(f"✅ Broadcast concluído. Clientes ativos: {len(self.active_connections)}")

manager = ConnectionManager()

# Snapshot do último payload (string JSON) enviado via WebSocket.
# Isso permite que um cliente recém-conectado receba dados imediatamente.
_LAST_WS_PAYLOAD: str | None = None

# Application state for API endpoints
_app_state: Dict[str, Any] = {
    "settings": {
        "profile_name": "default",
        "min_spread_pct": 0.5,
        "min_score": 50,
        "min_volume_usd": 100000,
        "min_persistence_min": 0,
        "bankroll_usd": 10000.0,
        "hedge_pct": 100.0,
        "entry_min_usd": 100.0,
        "entry_max_usd": 1000.0,
        "hide_blocked": False,
        "allow_cross": True,
        "allow_same": True,
        "spots": ["binance", "mexc", "bybit"],
        "futures": ["binance_futures", "mexc_futures"],
        "blocked_coins": [],
    },
    "pnl_history": [],
    "snapshots": [],
}

# =============================================================================
# API V1 ENDPOINTS
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline, risk_state, execution_engine
    logger.info("🚀 INICIANDO SERVIDOR DOMARB V2 (INSTITUCIONAL)...")

    # 1. Inicializa Estados
    risk_state = PortfolioRiskState(total_capital=1000.0)

    # 2. Inicializa Engine (Com os argumentos obrigatórios F7)
    execution_engine = ExecutionEngine(router_map={}, portfolio_state=risk_state)

    # 3. Inicializa Pipeline Completo (F1-F17)
    logger.info("🛡️ Inicializando Governança de Risco e Motor de Execução...")
    pipeline = OpportunityPipeline(risk_state, execution_engine)
    logger.info("✅ Pipeline Global injetado.")

    # 4. Inicia Scanner Loop
    scan_task = asyncio.create_task(scanner_loop())

    yield

    # Shutdown
    logger.info("🛑 Desligando servidor...")
    scan_task.cancel()
    with suppress(asyncio.CancelledError):
        await scan_task
    if pipeline:
        await pipeline.fetch_service.close_all()

# =============================================================================
# FASTAPI APP
# =============================================================================

app = FastAPI(title="DomCrypto Bot", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/opportunities")
async def list_opportunities(
    status: str = Query(default="all", description="Filter by status"),
    min_score: int = Query(default=0, ge=0, le=100, description="Minimum score"),
    min_spread: float = Query(default=0, ge=0, description="Minimum spread %"),
    limit: int = Query(default=100, ge=1, le=500, description="Max items to return")
):
    """List current arbitrage opportunities."""
    global _LAST_WS_PAYLOAD

    # Parse last payload if available
    items = []
    if _LAST_WS_PAYLOAD:
        try:
            data = json.loads(_LAST_WS_PAYLOAD)
            items = data.get("items", [])
        except Exception:
            items = []

    # Apply filters
    filtered = items

    if status != "all":
        filtered = [o for o in filtered if o.get("status", "").upper() == status.upper()]

    filtered = [o for o in filtered if o.get("score", 0) >= min_score]
    filtered = [o for o in filtered if o.get("spread_net_pct", 0) >= min_spread]

    # Apply limit
    filtered = filtered[:limit]

    # Build meta from last payload
    meta = {
        "cycle_id": _CYCLE_ID,
        "ts": int(time.time() * 1000),
        "counts": {
            "total": len(items),
            "active": len([o for o in items if o.get("status") in ("ACTIVE", "READY")]),
            "obs": len([o for o in items if o.get("status") == "OBSERVATION_ONLY"]),
            "killed": len([o for o in items if o.get("status") == "KILLED"]),
        },
        "pipeline_latency_ms": 0,
    }

    return {"items": filtered, "meta": meta}


@app.get("/api/v1/opportunities/{opportunity_id}")
async def get_opportunity(opportunity_id: str):
    """Get details of a specific opportunity."""
    global _LAST_WS_PAYLOAD

    if _LAST_WS_PAYLOAD:
        try:
            data = json.loads(_LAST_WS_PAYLOAD)
            items = data.get("items", [])
            for opp in items:
                if opp.get("id") == opportunity_id:
                    return {"item": opp, "exists": True}
        except Exception:
            pass

    return {"item": {"id": opportunity_id}, "exists": False}


@app.get("/api/v1/settings")
async def get_settings():
    """Get current user settings."""
    return _app_state["settings"]


@app.put("/api/v1/settings")
async def update_settings(request: Request):
    """Update user settings."""
    try:
        body = await request.json()
        _app_state["settings"].update(body)
        return _app_state["settings"]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/pnl")
async def get_pnl_history(
    days: int = Query(default=30, ge=1, le=365, description="Number of days"),
    status: str = Query(default="all", description="Filter by status")
):
    """Get PnL history."""
    items = _app_state.get("pnl_history", [])

    return {
        "items": items,
        "total": len(items),
        "summary": {
            "total_pnl_usd": sum(r.get("pnl_usd", 0) or 0 for r in items),
            "trades_count": len(items),
        }
    }


@app.get("/api/v1/snapshots")
async def get_pipeline_snapshots(
    limit: int = Query(default=50, ge=1, le=500, description="Max snapshots")
):
    """Get pipeline snapshots."""
    snapshots = _app_state.get("snapshots", [])
    return {"items": snapshots[-limit:], "total": len(snapshots)}


# =============================================================================
# SCANNER LOOP
# =============================================================================

async def scanner_loop():
    logger.info("💓 Scanner iniciado (Loop Principal).")
    while True:
        async with scanner_lock:
            try:
                if pipeline:
                    global _CYCLE_ID
                    _CYCLE_ID += 1

                    # 1. Executa o Pipeline Completo
                    # logger.info("⏳ Buscando dados nas exchanges...") # Descomente se quiser ver o inicio
                    t0 = asyncio.get_event_loop().time()
                    opportunities = await pipeline.run()
                    t_build_ms = int((asyncio.get_event_loop().time() - t0) * 1000)
                    
                    count = len(opportunities)
                    
                    # 2. Serialização (sempre em envelope: {items, meta})
                    t1 = asyncio.get_event_loop().time()
                    items = [op.to_dict() for op in opportunities]
                    safe_items = _json_sanitize(items)

                    # Contadores para telemetria/diagnóstico (F7/P0)
                    counts = {"raw": count, "active": 0, "obs": 0, "killed": 0}
                    for op in opportunities:
                        st = getattr(op, "status", None)
                        if st in ("ACTIVE", "READY"):
                            counts["active"] += 1
                        elif st == "OBSERVATION_ONLY":
                            counts["obs"] += 1
                        elif st == "KILLED":
                            counts["killed"] += 1

                    payload_obj = {
                        "items": safe_items or [],
                        "meta": {
                            "ts": time.time(),
                            "cycle_id": _CYCLE_ID,
                            "counts": counts,
                            "timing_ms": {"build": t_build_ms},
                            "status": "ACTIVE" if counts["killed"] == 0 else "DEGRADED",
                            "notes": [],
                        },
                    }

                    # Nota: json.dumps(allow_nan=False) exige que sanitize tenha removido NaN/Inf
                    payload_text = json.dumps(payload_obj, ensure_ascii=False, allow_nan=False)
                    t_adapt_ms = int((asyncio.get_event_loop().time() - t1) * 1000)

                    # Atualiza timing e tamanho do payload
                    payload_bytes = len(payload_text.encode("utf-8"))
                    payload_obj["meta"]["timing_ms"]["adapt"] = t_adapt_ms
                    payload_obj["meta"]["payload_bytes"] = payload_bytes
                    payload_text = json.dumps(payload_obj, ensure_ascii=False, allow_nan=False)

                    # 3. LOG DIAGNÓSTICO (Aqui estava o silêncio!)
                    if count > 0:
                        logger.info(f"📡 Enviando {count} oportunidades para o Frontend.")
                    else:
                        logger.info("⚠️ Scanner rodou mas encontrou 0 oportunidades (Mercado parado ou Filtro Hard).")

                    # 4. Envia SEMPRE (Mesmo vazio, para atualizar status/ping no front)
                    # Atualiza snapshot antes do broadcast.
                    global _LAST_WS_PAYLOAD
                    _LAST_WS_PAYLOAD = payload_text

                    # Store snapshot for API endpoint
                    snapshot = {
                        "id": _CYCLE_ID,
                        "cycle_id": _CYCLE_ID,
                        "ts": datetime.utcnow(),
                        "count_raw": counts["raw"],
                        "count_active": counts["active"],
                        "count_obs": counts["obs"],
                        "count_killed": counts["killed"],
                        "top_spread": max((o.spread_net_pct for o in opportunities), default=0),
                        "top_symbol": max(opportunities, key=lambda o: o.spread_net_pct).symbol if opportunities else "",
                        "meta": {"latency_ms": t_build_ms}
                    }
                    _app_state["snapshots"].append(snapshot)

                    # Keep only last 100 snapshots
                    if len(_app_state["snapshots"]) > 100:
                        _app_state["snapshots"] = _app_state["snapshots"][-100:]

                    t2 = asyncio.get_event_loop().time()
                    await manager.broadcast(payload_text)
                    t_broadcast_ms = int((asyncio.get_event_loop().time() - t2) * 1000)
                    logger.info(
                        f"📈 Cycle={_CYCLE_ID} counts={counts} bytes={payload_bytes} "
                        f"timing_ms={{build:{t_build_ms},adapt:{t_adapt_ms},broadcast:{t_broadcast_ms}}}"
                    )

            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"🔥 Erro Crítico no Loop Scanner: {e}")
        
        # Intervalo entre ciclos
        await asyncio.sleep(10)


# =============================================================================
# LIFESPAN & ROUTES
# =============================================================================

# Mount static e templates (diretórios opcionais)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(BASE_DIR, "static")
templates_path = os.path.join(BASE_DIR, "templates")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
if os.path.exists(templates_path):
    templates = Jinja2Templates(directory=templates_path)

# Rotas
app.include_router(routes.router)

# Register global exception handler
from src.backend.api.endpoints.http_endpoints import generic_exception_handler
app.add_exception_handler(Exception, generic_exception_handler)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy" if pipeline else "degraded",
        "service": "domcrypto-backend",
        "version": "0.2.0",
        "timestamp": time.time(),
        "services": {
            "pipeline": pipeline is not None,
            "websocket": len(manager.active_connections) > 0,
        }
    }


@app.get("/api/v1/health")
async def health_check_v1():
    """Health check endpoint (v1 API)."""
    from datetime import datetime
    return {
        "status": "healthy" if pipeline else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.2.0",
        "services": {
            "pipeline": pipeline is not None,
            "database": True,
            "websocket": len(manager.active_connections) > 0,
        }
    }


@app.get("/spot-futuros", response_class=HTMLResponse)
async def view_spot_futuros(request: Request):
    if not os.path.exists(templates_path):
        return {"error": "Templates directory not found", "info": "Frontend available at /api/sse/opportunities"}
    return templates.TemplateResponse("spot-futuros.html", {"request": request})

@app.websocket("/ws/opportunities")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Envia snapshot imediatamente (se existir), para o frontend não parecer "morto".
        if _LAST_WS_PAYLOAD:
            try:
                await websocket.send_text(_LAST_WS_PAYLOAD)
            except Exception as e:
                logger.warning(f"Falha ao enviar snapshot inicial via WS: {e}")

        # Mantém a conexão viva e detecta disconnects.
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                # sem mensagens do cliente; apenas mantém a sessão aberta
                continue
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket fechado com erro: {e}")
        manager.disconnect(websocket)