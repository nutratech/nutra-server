#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 17:15:30 2020

@author: shane
"""


import os

from tempfile import NamedTemporaryFile

from InvoiceGenerator.api import Invoice, Item, Client, Provider, Creator


class PDFInvoice:
    def __init__(self, order_id=None, customer_id=None,):
    # choose english as language
    os.environ["INVOICE_LANG"] = "en"

    client = Client("Client company")
    provider = Provider("Nutra, LLC", bank_account="N/A", city="Detroit", country="US")
    creator = Creator("Shane & Kyle")

    invoice = Invoice(client, provider, creator)
    # set currency and other details
    invoice.currency_locale = "en_US.UTF-8"
    invoice.currency = "$"
    invoice.number = order_id

    invoice.add_item(Item(32, 600, description="Item 1"))
    invoice.add_item(Item(60, 50, description="Item 2", tax=21))
    invoice.add_item(Item(50, 60, description="Item 3", tax=0))
    invoice.add_item(Item(5, 600, description="Item 4", tax=15))

    from InvoiceGenerator.pdf import SimpleInvoice

    pdf = SimpleInvoice(invoice)
    pdf.gen("invoice.pdf", generate_qr_code=True)
