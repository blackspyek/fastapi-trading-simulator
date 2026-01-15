"""
Pakiet kontrolerów REST API.
"""

from app.api.controllers.trade_controller import router as trade_router
from app.api.controllers.auth_controller import router as auth_router
from app.api.controllers.asset_controller import router as asset_router

__all__ = ["trade_router", "auth_router", "asset_router"]
