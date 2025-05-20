from fastapi import FastAPI

from app.api import accounts_router, transactions_router, auth_router
from app.core.db import create_tables
from app.core.config import settings

ROUTES = {
    '/transactions': transactions_router,
    '/accounts': accounts_router,
    '/auth': auth_router
}


def set_routes(app: FastAPI) -> None:
    for prefix, router in ROUTES.items():
        app.include_router(router=router, prefix=prefix)


def get_app(name: str) -> FastAPI:
    app = FastAPI(title=name)
    set_routes(app)
    app.mount(settings.app.app_mount, app)

    @app.on_event("startup")
    async def startup_event():
        await create_tables()

    return app