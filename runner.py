import uvicorn
from config import settings
from app import app

if __name__ == "__main__":
    log_level = settings.app.log_level.lower()  # Uvicorn ожидает lowercase
    run_port = getattr(settings.app_info, 'port', getattr(settings.app, 'port', 5000))

    uvicorn.run(
        app="app:app",
        host="0.0.0.0",
        port=run_port,
        reload=settings.app.debug,
        log_level=log_level,
    )