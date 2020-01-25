#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 18:20:27 2020

@author: shane
"""

import os
import threading
import subprocess

from flask import Flask, request
from flask_cors import CORS

from libserver.shop import GET_stripe_products, GET_stripe_skus, GET_products__product_id__reviews, POST_products_reviews, GET_products_avg_ratings
from libserver.utils.caffeine import caffeinate
from libserver.libserver import Request, Response, get_self_route_rules
from libserver.psql import con

# Export the Flask server for gunicorn
app = Flask(__name__)
CORS(app)
caffeinate()


'''
-------------------------
Routes
-------------------------
'''


@app.route("/")
def get_home_page():
    url_map = get_self_route_rules(app)
    return f"<pre>Welcome to the customer file parser.\n\nEndpoints:\n\n{url_map}<pre>"


@app.route('/logs')
def get_logs():
    LOGS = open(f'app.log').read()
    return f'<pre>{LOGS}</pre>'


'''
-------------------------
Account functions
-------------------------
'''


@app.route('/register', methods=['POST'])
def post_register():
    # return Request(POST_register, request)
    return Response(code=500, data={'error': 'Not implemented'})


@app.route('/login', methods=['POST'])
def post_login():
    # return Request(POST_login, request)
    return Response(code=500, data={'error': 'Not implemented'})


'''
-------------------------
Stripe functions
-------------------------
'''


@app.route('/stripe/products')
def get_stripe_products():
    return Request(GET_stripe_products, request)


@app.route('/stripe/skus')
def get_stripe_skus():
    return Request(GET_stripe_skus, request)


@app.route('/products/<id>/reviews')
def get_products__product_id__reviews(id):
    return Request(GET_products__product_id__reviews, request)


@app.route('/products/reviews', methods=['POST'])
def post_products_reviews():
    return Request(POST_products_reviews, request)


@app.route('/products/avg_ratings')
def get_products_avg_ratings():
    return Request(GET_products_avg_ratings, request)


# Make script executable
if __name__ == "__main__":
    """ Run as file (or debug it in vscode!) """

    print('[__main__] bypassing gunicorn...')
    port = int(os.getenv("PORT", 20000))
    app.run(
        host='127.0.0.1',
        port=port,
        # debug=True,
    )
