import ast
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

    # Loop over SKUs
    for sku in stripe.SKU.auto_paging_iter():
        if skus:
            # Iterate selected
            if id in skus:
                sku_shell(sku)
        else:
            sku_shell(sku)
            # Iterate all


def sku_shell(sku):
    """ Modify the inventory for a particular SKU """

    print(f"\n{sku.attributes.name} ${sku.price / 100}")

    while True:
        _input = input("inventory dict: ")
        if not _input:
            break

        try:
            inventory_attrs = ast.literal_eval(_input)
            stripe.SKU.modify(sku.id, inventory=inventory_attrs)
            break
        except Exception as e:
            stack = "\n".join(traceback.format_tb(e.__traceback__))
            print(f"{repr(e)}\n\n{stack}")


# Make script executable
if __name__ == "__main__":
    main(sys.argv[1:])
