from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from app.routes import auth, protected

app = FastAPI(
    debug=settings.app.debug,
    title=settings.app_info.name,
    description=settings.app_info.description,
    docs_url=settings.app_info.docs_url,
    openapi_url=f"{settings.app_info.docs_url}/openapi.json",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_app() -> FastAPI:
    app.include_router(auth.router)
    app.include_router(protected.router)

    from app.models.db_helper import db_manager

    @app.on_event("startup")
    async def startup_event():
        print("Запуск приложения...")
        await db_manager.create_database_tables()
        print("Таблицы базы данных проверены/созданы.")

    @app.on_event("shutdown")
    async def shutdown_event():
        print("Остановка приложения...")
        await db_manager.dispose()
        print("Соединения с базой данных закрыты.")

    return app
