import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import psutil

from app.api.controllers import trade_router, auth_router, asset_router
from app.api.services.market_service import MarketService
from app.api.clients.binance_client import BinanceClient
from app.api.core.socket_manager import manager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manages the application lifecycle.

    Starts MarketService in the background at startup
    and stops it at shutdown.

    Args:
        app: FastAPI application instance.

    Yields:
        None - control passes to the application.
    """
    binance_client = BinanceClient()
    market_service = MarketService(
        binance_client=binance_client,
        connection_manager=manager
    )
    
    task = asyncio.create_task(market_service.start_price_updates())
    
    yield
    
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Crypto Trading Simulator",
    description="Cryptocurrency trading simulator with real-time data from Binance",
    version="2.0.0",
    lifespan=lifespan
)

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(trade_router, prefix="/api/trade", tags=["Trading"])
app.include_router(asset_router, prefix="/api/assets", tags=["Assets"])


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for receiving real-time updates.

    Sends server status (CPU, RAM) every 2 seconds.
    Price updates are broadcasted by MarketService.
    You can see server status when you hover over the "Connected" label at the navbar in the frontend.

    Args:
        websocket: Client WebSocket connection.
    """
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(2)
            await websocket.send_json({
                "type": "server_status",
                "cpu": psutil.cpu_percent(),
                "ram": psutil.virtual_memory().percent
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Endpoint for checking application status. Container is restarting if it returns unhealthy.

    Returns:
        Dictionary with application status.
    """
    return {"status": "healthy", "version": "2.0.0"}