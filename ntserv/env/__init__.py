"""Anything that is dotenv-specific (user in development with .env file)"""
import getpass
import os
from datetime import timedelta

from dotenv import load_dotenv

# Read in .env file if it exists locally, else look to env vars
load_dotenv(verbose=True)

# Environment and run config
ENV = os.environ.get("NTSERV_ENV", "local")
PORT = int(os.getenv("NTSERV_PORT", str(20000)))

DEBUG = bool(ENV == "local")

# Log level
DEFAULT_LOG_LEVEL = 10 if DEBUG else 20
LOG_LEVEL = int(os.getenv("NTSERV_LOG_LEVEL", str(DEFAULT_LOG_LEVEL)))

# Self-referential hostname pointers
# BASE_HOST = os.getenv("NTSERV_SERVER_HOST", "http://127.0.0.1")
# # SCHEME = "http://" if DEBUG else "https://"
# BASE_HOST_PROD = "https://nutra.tk"
# SERVER_HOST_PROD = "https://api.nutra.tk"
# BASE_HOST_DEV = "https://dev.nutra.tk"
# SERVER_HOST_DEV = "https://api.dev.nutra.tk"

LOCAL_UI_PORT = 5173
LOCAL_API_PORT = 20000
LOCAL_BLOG_PORT = 8000

HOST_ENV_DICT = {
    "local": {
        "ui": f"http://localhost:{LOCAL_UI_PORT}",
        "blog": f"http://localhost:{LOCAL_BLOG_PORT}",
        "api": f"http://localhost:{LOCAL_API_PORT}",
    },
    "dev": {
        "ui": "https://dev.nutra.tk",
        "blog": "https://dev.nutra.tk/blog/",
        "api": "https://api.dev.nutra.tk",
    },
    "prod": {
        "ui": "https://nutra.tk",
        "blog": "https://nutra.tk/blog/",
        "api": "https://api.nutra.tk",
    }
}

# UI_HOST = f"{BASE_HOST}:{LOCAL_UI_PORT}" if DEBUG else BASE_HOST
# SERVER_HOST = f"{BASE_HOST}:{LOCAL_API_PORT}" if DEBUG else f"api.{BASE_HOST}"
# BLOG_HOST = f"{BASE_HOST}:{LOCAL_BLOG_PORT}" if DEBUG else f"{BASE_HOST}/blog"

ALLOWED_ORIGINS = [
    # Local development (TODO only expose these in local)
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    # Deployed environments (TODO only expose these in respective environments)
    "https://nutra.tk",
    "https://dev.nutra.tk",
]

# PostgreSQL
PSQL_DATABASE = os.getenv("NTSERV_PSQL_DB_NAME", "nt")
PSQL_SCHEMA = os.getenv("NTSERV_PSQL_SCHEMA_NAME", "nt")

PSQL_USER = os.getenv("NTSERV_PSQL_USER", getpass.getuser())
PSQL_PASSWORD = os.getenv("NTSERV_PSQL_PASSWORD", "password")

PSQL_HOST = os.getenv("NTSERV_PSQL_HOST", "localhost")

# Server secrets
JWT_SECRET = os.getenv("NTSERV_JWT_SECRET", "secret123")
PROXY_SECRET = os.getenv("NTSERV_PROXY_SECRET", "secret123")

# Email creds
# TODO: warning message if undefined or empty str()
PROD_EMAIL = os.getenv("NTSERV_PROD_EMAIL", str())
PROD_EMAIL_PASS = os.getenv("NTSERV_PROD_EMAIL_PASS", str())

# NOTE: are these used?
# Other configurations
TOKEN_EXPIRY = timedelta(weeks=520)
