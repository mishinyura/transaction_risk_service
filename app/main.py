import uvicorn
import asyncio

from app.core.app import get_app
from config import settings


if __name__ == '__main__':
    app = get_app('transaction_risk_service')
    app.mount(settings.app.app_mount, app)
    uvicorn.run(app, host=settings.app.app_host, port=settings.app.app_port)