import os
import getpass

from dotenv import load_dotenv


# Read in .env file if it exists locally, else look to env vars
load_dotenv(verbose=True)


# PostgreSQL
PSQL_DATABASE = "nutra"

PSQL_USER = os.getenv("PSQL_USER", getpass.getuser())
PSQL_PASSWORD = os.getenv("PSQL_PASSWORD", "password")

PSQL_HOST = os.getenv("PSQL_HOST", "localhost")


# Stripe API Key
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
