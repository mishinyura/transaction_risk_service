from fastapi import FastAPI

ROUTES = {

}


def setting_routes(app: FastAPI) -> None:
    for prefix, router in ROUTES.items():
        app.include_router(prefix=prefix, router=router)


def get_app(name: str) -> FastAPI:
    app = FastAPI(title=name)
    setting_routes(app)
    return app