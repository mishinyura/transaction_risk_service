from pydantic import BaseModel, SecretStr


class UserSchema(BaseModel):
    id: int
    username: str
    password: SecretStr