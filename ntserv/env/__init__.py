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

DEFAULT_N_WORKERS = 1 if DEBUG else 2
N_WORKERS = int(os.getenv("NTSERV_N_WORKERS", str(DEFAULT_N_WORKERS)))

# Log level
DEFAULT_LOG_LEVEL = 10 if DEBUG else 20
LOG_LEVEL = int(os.getenv("NTSERV_LOG_LEVEL", str(DEFAULT_LOG_LEVEL)))

# Self-referential hooks
BASE_HOST = os.getenv("NTSERV_SERVER_HOST", "http://127.0.0.1")
BASE_HOST_PROD = "https://nutra.tk"
SERVER_HOST_PROD = "https://nutra.tk/api"
BASE_HOST_DEV = "https://dev.nutra.tk"
SERVER_HOST_DEV = "https://dev.nutra.tk/api"

ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "https://nutra.tk",
    "https://dev.nutra.tk",
]

UI_PORT = 3000
SERVER_PORT = 20000
BLOG_PORT = 2368
UI_HOST = f"{BASE_HOST}:{UI_PORT}" if DEBUG else BASE_HOST
SERVER_HOST_BASE = f"{BASE_HOST}:{SERVER_PORT}" if DEBUG else f"{BASE_HOST}"
SERVER_HOST = f"{BASE_HOST}:{SERVER_PORT}/api" if DEBUG else f"{BASE_HOST}/api"
BLOG_HOST = f"{BASE_HOST}:{BLOG_PORT}" if DEBUG else f"{BASE_HOST}/blog"
UI_HOST = f"http://127.0.0.1:{UI_PORT}" if DEBUG else BASE_HOST

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
