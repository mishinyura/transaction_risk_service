import uvicorn
from app import create_app
from config import settings

app_instance = create_app()

if __name__ == "__main__":
    log_level = "debug" if settings.app.debug else "info"
    print(f"Запуск Uvicorn сервера на http://0.0.0.0:8000 с уровнем логирования: {log_level}")
    uvicorn.run(
        app="runner:app_instance",
        host="0.0.0.0",
        port=8000,
        reload=settings.app.debug,
        log_level=log_level
    )
