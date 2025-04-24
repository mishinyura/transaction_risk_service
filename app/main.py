import uvicorn
import asyncio

from app.core.app import get_app
from config import settings

app = get_app('transaction_risk_service')


if __name__ == '__main__':
    uvicorn.run(app, host=settings.app.app_host, port=settings.app.app_port)
