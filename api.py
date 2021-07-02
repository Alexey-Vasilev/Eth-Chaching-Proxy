
"""A script that implements caching proxy for Cloudflare Eth Gateway."""

import requests
from functools import lru_cache
import random
from flask import Flask, jsonify

# Ethereum Gateway address
URL = 'https://cloudflare-eth.com'


def get_last_block_number():
    """Find a number of the last block."""
    x = requests.post(URL, json = {"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":83})
    return int(x.json()['result'], 16)


def do_request(_block_number, _tx):
    """Uncached request for last 20 blocks that may be reorg."""
    # Make request for the Gateway
    myobj = {"jsonrpc":"2.0","method":"eth_getBlockByNumber", "params": [_block_number, True], "id": 1}
    response = requests.post(URL, json = myobj)
    # Return transaction data
    # If tx hash was given
    if isinstance(_tx, str):
        for t in response.json()["result"]["transactions"]:
            # look for transaction
            if "hash" in  t.keys():
                if t["hash"] == _tx:
                    return t
            else:
                return "there is no tx"
        return "wrong tx hash"
    # If tx index was given
    else:
        if len(response.json()["result"]["transactions"]) == 0:
            return "there is no tx"
        elif len(response.json()["result"]["transactions"]) < _tx :
            return "transmission number is out of range"
        else:
            return response.json()["result"]["transactions"][_tx]


@lru_cache()
def do_cached_request(_block_number, _tx):
    """Cached request for the rest of blocks."""
    # Make request for the Gateway
    myobj = {"jsonrpc":"2.0","method":"eth_getBlockByNumber", "params": [_block_number, True], "id": 1}
    response = requests.post(URL, json = myobj)

    # Return transaction data
    # If tx hash was given
    if isinstance(_tx, str):
        for t in response.json()["result"]["transactions"]:
            # look for transaction
            if "hash" in  t.keys():
                if t["hash"] == _tx:
                    return t
            else:
                return "there is no tx"
        return "wrong tx hash"
    # If tx index was given
    else:
        if len(response.json()["result"]["transactions"]) == 0:
            return "there is no tx"
        elif len(response.json()["result"]["transactions"]) < _tx :
            return "transmission number is out of range"
        else:
            return response.json()["result"]["transactions"][_tx]

"""Create the Flask application object."""
app = Flask(__name__)


@app.route('/')
def index():
    """Set up dummy home page."""
    return "Home page"


@app.route("/block/<block_number>/txs/<transaction>", methods=['GET'])
def run_api(block_number, transaction):
    """Process user request."""
    # Check the number of the last block
    last_block_number = get_last_block_number()

    # Convert to int if block_number is an index
    if block_number not in ['latest', 'earliest', 'pending']:
        block_number = int(block_number)

    # Convert to hex if it is a hash
    if transaction[0:2] == ("0x"):
        transaction = hex(int(transaction, 16))
    # Convert to int if transaction is an index
    else:
        transaction = int(transaction)

    if block_number in ["latest", "pending"]:
        # For last 20 blocks that may be reorganised
        return jsonify({'result':do_request(block_number, transaction)})
    elif block_number == "earliest":
        # For the stable blocks
        return jsonify({'result':do_cached_request(block_number, transaction)})
    elif block_number > (last_block_number - 20):
        # For last 20 blocks that may be reorganised
        return jsonify({'result':do_request(hex(block_number), transaction)})
    else:
        # For the stable blocks
        return jsonify({'result':do_cached_request(hex(block_number), transaction)})

# Run the application server
if __name__ == "__main__":
    app.run(debug=True)
