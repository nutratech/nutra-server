import getpass
import os
from datetime import timedelta

from dotenv import load_dotenv

# Read in .env file if it exists locally, else look to env vars
load_dotenv(verbose=True)


# Stripe API Key
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")

# PostgreSQL
PSQL_DATABASE = os.getenv("PSQL_DB_NAME", "nutra")
PSQL_SCHEMA = "nt"

PSQL_USER = os.getenv("PSQL_USER", getpass.getuser())
PSQL_PASSWORD = os.getenv("PSQL_PASSWORD", "password")

PSQL_HOST = os.getenv("PSQL_HOST", "localhost")

# Other
JWT_SECRET = os.getenv("JWT_SECRET", "secret123")
TOKEN_EXPIRY = timedelta(days=1)
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SEARCH_LIMIT = 100
