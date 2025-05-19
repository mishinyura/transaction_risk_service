from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from app.models.db_helper import db_helper

from config import settings
from app.routes import auth_router, protected_router
# from app.exceptions.http import internal_server_error, InternalServerException # Если будут кастомные обработчики


_app = FastAPI(
    debug=settings.app.debug,
    title=settings.app_info.name,
    description=settings.app_info.description,
    version=settings.app.app_version, # Используем версию из AppConfig
    docs_url=settings.app_info.docs_url,
    openapi_url=f'{settings.app_info.docs_url.rstrip("/")}/openapi.json',
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("INFO: Application startup: Initializing resources...")
    yield
    print("INFO: Application shutdown: Disposing resources...")
    await db_helper.dispose()

_app.router.lifespan_context = lifespan

# --- Middlewares ---
# CORS Middleware (важно для взаимодействия с фронтендом на другом порту/домене)
if settings.cors.allow_origins:
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allow_origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )
    print(f"INFO: CORS middleware enabled for origins: {settings.cors.allow_origins}")

# GZip Middleware
_app.add_middleware(GZipMiddleware, minimum_size=1000) # Сжимать ответы > 1KB

# --- Подключение роутеров ---
API_PREFIX = "/api/v1"

_app.include_router(auth_router, prefix=API_PREFIX)
_app.include_router(protected_router, prefix=API_PREFIX)


# --- Статические файлы ---
# _app.mount("/static", StaticFiles(directory= Path(__file__).parent / "static"), name="static")

app = _app
