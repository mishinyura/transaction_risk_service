from typing import Optional
from pydantic import BaseModel
import uuid


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    user_id: Optional[uuid.UUID] = None