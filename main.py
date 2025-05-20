import uvicorn
import asyncio

from app.core.config import settings
from app.core.app import get_app
from app.core.db import create_tables


if __name__ == '__main__':
    # asyncio.run(create_tables()) #Раскомментировать если требуется создать таблицы
    app = get_app(name='Transaction Service')
    app.mount(settings.app.app_mount, app)

    uvicorn.run(app, host=settings.app.app_host, port=settings.app.app_port)