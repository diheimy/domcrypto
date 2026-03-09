import asyncio
import logging
import json
from contextlib import asynccontextmanager, suppress
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
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

# --- Globais ---
pipeline = None
risk_state = None
execution_engine = None
scanner_lock = asyncio.Lock()

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
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Erro no broadcast: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

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

async def scanner_loop():
    logger.info("💓 Scanner iniciado (Loop Principal).")
    while True:
        async with scanner_lock:
            try:
                if pipeline:
                    # 1. Executa o Pipeline Completo
                    # logger.info("⏳ Buscando dados nas exchanges...") # Descomente se quiser ver o inicio
                    opportunities = await pipeline.run()
                    
                    count = len(opportunities)
                    
                    # 2. Serialização
                    data_to_send = [op.to_dict() for op in opportunities]
                    
                    # 3. LOG DIAGNÓSTICO (Aqui estava o silêncio!)
                    if count > 0:
                        logger.info(f"📡 Enviando {count} oportunidades para o Frontend.")
                    else:
                        logger.info("⚠️ Scanner rodou mas encontrou 0 oportunidades (Mercado parado ou Filtro Hard).")

                    # 4. Envia SEMPRE (Mesmo vazio, para atualizar status/ping no front)
                    await manager.broadcast(json.dumps(data_to_send))

            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"🔥 Erro Crítico no Loop Scanner: {e}")
        
        # Intervalo entre ciclos
        await asyncio.sleep(10)

app = FastAPI(title="DomArb Crypto Bot", version="2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Rotas
app.include_router(routes.router)

@app.get("/spot-futuros", response_class=HTMLResponse)
async def view_spot_futuros(request: Request):
    return templates.TemplateResponse("spot-futuros.html", {"request": request})

@app.websocket("/ws/opportunities")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(10) 
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket fechado com erro: {e}")
        manager.disconnect(websocket)