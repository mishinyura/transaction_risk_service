from fastapi import FastAPI

from app.api.tests_router import test_router

ROUTES = {
    '': test_router
}


def set_routes(app: FastAPI) -> None:
    for prefix, router in ROUTES.items():
        print(router)
        app.include_router(router=router, prefix=prefix)


def get_app(name: str) -> FastAPI:
    app = FastAPI(title=name)
    set_routes(app)
    return app