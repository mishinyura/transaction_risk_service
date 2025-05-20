from fastapi import FastAPI

from app.api.tests_router import test_router
from app.api.transactions import transactions_router
from app.core.db import create_tables
from config import settings

ROUTES = {
    '': test_router,
    '/transactions': transactions_router
}


def set_routes(app: FastAPI) -> None:
    for prefix, router in ROUTES.items():
        app.include_router(router=router, prefix=prefix)


def get_app(name: str) -> FastAPI:
    app = FastAPI(title=name)
    set_routes(app)
    app.mount(settings.app.app_mount, app)
    app.add_event_handler("startup", create_tables)
    return app