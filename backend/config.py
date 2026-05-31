from dotenv import load_dotenv  # type: ignore
import os

load_dotenv()

DATABASE_URL           = os.getenv("DATABASE_URL", "sqlite:///./hrms.db")
APP_HOST               = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT               = int(os.getenv("APP_PORT", 8000))

DEFAULT_ADMIN_NAME     = os.getenv("DEFAULT_ADMIN_NAME", "Super Admin")
DEFAULT_ADMIN_EMAIL    = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@hrms.com")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")