import os
import sys
import secrets
from pathlib import Path
from typing import List, Optional, Union, Any
from datetime import timedelta

from dynaconf import Dynaconf, Validator
from pydantic import BaseModel, Field, PostgresDsn, AnyHttpUrl

ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_UNSAFE_SECRET_KEY_IN_TOML = "!!!CHANGE_ME_PLEASE_I_AM_NOT_SECURE_IN_TOML!!!"


def generate_and_save_key(filepath: Path, length_bytes: int = 32) -> bytes:
    """Генерирует ключ, сохраняет в файл и возвращает его."""
    print(f"INFO: Generating new secret key for '{filepath.name}'...")
    key = secrets.token_bytes(length_bytes)
    try:
        with open(filepath, 'wb') as f:
            f.write(key)
        print(f"INFO: New secret key saved to {filepath}")
        if sys.platform != "win32":
            os.chmod(filepath, 0o600)
    except IOError as e:
        print(f"ERROR: Could not write secret key to {filepath}: {e}")
        print("       Please ensure the application has write permissions or set the key via environment variables.")
    return key


# --- Pydantic модели для конфигурации ---
class AppInfoConfig(BaseModel):
    name: str = Field(..., alias="NAME")
    description: str = Field(..., alias="DESCRIPTION")
    docs_url: str = Field(..., alias="DOCS_URL")


class AppConfig(BaseModel):
    debug: bool = Field(..., alias="DEBUG")
    log_level: str = Field(..., alias="LOG_LEVEL")
    secret_key_filename: str = Field(..., alias="SECRET_KEY_FILENAME")
    cookie_secure_flag: bool = Field(..., alias="COOKIE_SECURE_FLAG")
    access_token_expire_minutes: int = Field(..., alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    access_token_cookie_name: str = Field(..., alias="ACCESS_TOKEN_COOKIE_NAME")

    _secret_key_bytes: Optional[bytes] = None

    @property
    def app_version(self) -> str:
        version_file_path = ROOT_DIR / 'version.txt'
        max_version = '0.0.0'
        try:
            if version_file_path.exists():
                with open(version_file_path, 'r', encoding='utf-8') as vf:
                    lines = vf.readlines()
                    if lines:
                        first_line = lines[0].strip()
                        parts = first_line.split('\t-\t')
                        if parts:
                            max_version = parts[0]
        except Exception as e:
            print(f"WARNING: Could not read version from {version_file_path}: {e}")
        return max_version

    @property
    def secret_key(self) -> bytes:
        """Загружает или генерирует секретный ключ."""
        if self._secret_key_bytes is None:
            key_filepath = ROOT_DIR / self.secret_key_filename

            env_secret_key_str = os.getenv(f"APP_CONFIG_SECRET_KEY_B64")
            if env_secret_key_str:
                print(f"INFO: Using SECRET_KEY from environment variable APP_CONFIG_SECRET_KEY_B64.")
                try:
                    import base64
                    self._secret_key_bytes = base64.urlsafe_b64decode(env_secret_key_str.encode('utf-8'))
                    if len(self._secret_key_bytes) < 32:  # Проверка минимальной длины
                        print(
                            f"WARNING: SECRET_KEY from ENV is too short ({len(self._secret_key_bytes)} bytes). Recommended 32+ bytes.")
                    return self._secret_key_bytes
                except Exception as e:
                    print(f"ERROR: Could not decode SECRET_KEY from environment variable: {e}. Falling back.")

            # Попытка прочитать из файла
            if key_filepath.exists():
                print(f"INFO: Reading secret key from {key_filepath}")
                with open(key_filepath, 'rb') as f:
                    self._secret_key_bytes = f.read()
                if not self._secret_key_bytes or len(self._secret_key_bytes) < 32:
                    print(
                        f"WARNING: Secret key file '{key_filepath}' is empty or key is too short."
                        f" Will attempt to regenerate.")
                    self._secret_key_bytes = generate_and_save_key(key_filepath)
            else:
                print(f"WARNING: Secret key file '{key_filepath}' not found.")
                self._secret_key_bytes = generate_and_save_key(key_filepath)

        if not self._secret_key_bytes:  # Крайний случай, если генерация не удалась и ничего нет
            print("CRITICAL: SECRET KEY COULD NOT BE LOADED OR GENERATED. Using an unsafe default.")
            return b"unsafe_fallback_secret_key_32_bytes_long_or_longer"

        return self._secret_key_bytes

    @property
    def algorithm(self) -> str:
        return "HS256"


class DBSettings(BaseModel):
    type: str = Field(..., alias="TYPE")
    host: str = Field(..., alias="HOST")
    port: int = Field(..., alias="PORT")
    user: str = Field(..., alias="USER")
    password: str = Field(..., alias="PASSWORD")
    name: str = Field(..., alias="NAME")
    echo: bool = Field(False, alias="DB_ECHO")
    echo_pool: bool = Field(False, alias="DB_ECHO_POOL")
    pool_size: int = Field(10, alias="DB_POOL_SIZE")
    max_overflow: int = Field(20, alias="DB_MAX_OVERFLOW")

    @property
    def url(self) -> str:
        return f"{self.type}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class CorsSettings(BaseModel):
    allow_origins_str: str = Field("", alias="ALLOW_ORIGINS_STR")
    allow_credentials: bool = Field(True, alias="ALLOW_CREDENTIALS")
    allow_methods_str: str = Field("*", alias="ALLOW_METHODS")
    allow_headers_str: str = Field("*", alias="ALLOW_HEADERS")

    @property
    def allow_origins(self) -> List[str]:
        return [origin.strip() for origin in self.allow_origins_str.split(',') if origin.strip()]

    @property
    def allow_methods(self) -> List[str]:
        if self.allow_methods_str == "*":
            return ["*"]
        return [method.strip().upper() for method in self.allow_methods_str.split(',') if method.strip()]

    @property
    def allow_headers(self) -> List[str]:
        if self.allow_headers_str == "*":
            return ["*"]
        return [header.strip() for header in self.allow_headers_str.split(',') if header.strip()]


class Settings(BaseModel):
    app_info: AppInfoConfig
    app: AppConfig
    db: DBSettings
    cors: CorsSettings
    active_env: str


# --- Загрузка конфигурации с помощью Dynaconf ---
dyna_loader = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=[ROOT_DIR / 'settings.toml'],
    environments=True,
    load_dotenv=True,
    env_switcher="ENVIRONMENT__ACTIVE"
)

# Определяем активное окружение
active_env = dyna_loader.get("environment.active", "development").lower()
print(f"INFO: Loading configuration for environment: '{active_env}'")


try:
    env_config = dyna_loader.from_env(active_env)

    app_info_data = dyna_loader.get("app_info", {})

    app_config_data = env_config.to_dict()
    db_settings_data = env_config.get("db_settings", {})
    cors_settings_data = env_config.get("cors_settings", {})

    settings = Settings(
        app_info=AppInfoConfig(**app_info_data),
        app=AppConfig(**app_config_data),
        db=DBSettings(**db_settings_data, **env_config),
        cors=CorsSettings(**cors_settings_data),
        active_env=active_env
    )
except Exception as e:
    print(f"FATAL: Error loading or validating application configuration: {e}")
    print("       Please check your settings.toml and environment variables.")
    raise Exception(f"Configuration error: {e}")

# --- Вывод информации о конфигурации (для отладки) ---
print(f"INFO: Application Name: {settings.app_info.name} v{settings.app.app_version}")
print(f"INFO: Debug Mode: {settings.app.debug}")
print(f"INFO: Log Level: {settings.app.log_level}")
db_url_censored = f"{settings.db.type}://{settings.db.user}:*****@{settings.db.host}:{settings.db.port}/{settings.db.name}"
print(f"INFO: Database URL: {db_url_censored}")
print(f"INFO: Secret Key File: {settings.app.secret_key_filename} (Key loaded/generated)")
print(f"INFO: CORS Origins: {settings.cors.allow_origins}")
