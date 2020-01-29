import json
import os
import sys
import traceback

import stripe
from dotenv import load_dotenv

# Read in .env file if it exists locally, else look to env vars
load_dotenv(verbose=True)

STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
stripe.api_key = STRIPE_API_KEY

# change to script's dir
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def main(args):

    # Decide input args
    if len(args):
        skus = args.split(",")
    else:
        skus = None

    # Add each customer
    customers = []
    for customer in stripe.Customer.auto_paging_iter():
        customers.append(customer)

    # Save
    json.dump(
        customers, open(f"customers.json", "w+"), default=lambda x: x.__dict__, indent=2
    )


# Make script executable
if __name__ == "__main__":
    main(sys.argv[1:])
