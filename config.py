import os
import secrets
from pydantic import BaseModel, Field
from dynaconf import Dynaconf

# --- Secret Key Generation ---
SECRET_KEY_FILE = "secret_key.txt"


def generate_secret_key_if_not_exists(file_path: str = SECRET_KEY_FILE) -> None:
    if not os.path.exists(file_path):
        print(f"'{file_path}' not found. Generating a new secret key...")
        key = secrets.token_hex(32)
        with open(file_path, 'w') as f:
            f.write(key)
        print(f"New secret key generated and saved to '{file_path}'.")


generate_secret_key_if_not_exists()


# --- Pydantic Models for Configuration ---
class AppConfig(BaseModel):
    debug: bool
    secret_key_file_name: str = Field(default=SECRET_KEY_FILE)
    cookie_name: str
    cookie_max_age_days: int

    @property
    def secret_key(self) -> str:
        try:
            with open(self.secret_key_file_name, 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            raise RuntimeError(f"Secret key file '{self.secret_key_file_name}' not found. Please generate it.")


class AppInfoConfig(BaseModel):
    name: str
    description: str
    docs_url: str


class DatabaseConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str
    db_name: str

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.db_name}"


class Settings(BaseModel):
    app: AppConfig
    app_info: AppInfoConfig
    database: DatabaseConfig


# --- Load Settings using Dynaconf ---
dyna_settings = Dynaconf(
    settings_files=['settings.toml'],
    environments=True,
    load_dotenv=False
)

current_env = dyna_settings.get('current_env', 'development').lower()
print(f"Loading configuration for environment: {current_env}")


settings = Settings(
    app=AppConfig(**dyna_settings.get(f'{current_env}.app', dyna_settings.get('app', {}))),
    app_info=AppInfoConfig(**dyna_settings.get('app_info', {})),
    database=DatabaseConfig(**dyna_settings.get(f'{current_env}.database', dyna_settings.get('database', {})))
)

print(f"Database URL: {settings.database.url}")
print(f"App Debug Mode: {settings.app.debug}")
print(f"Secret Key: {settings.app.secret_key[:10]}...")