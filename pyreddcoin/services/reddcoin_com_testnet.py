# -*- coding: utf-8 -*-
"""
    pybitcoin
    ~~~~~

    :copyright: (c) 2014 by Halfmoon Labs
    :license: MIT, see LICENSE for more details.
"""

import json, requests, traceback
from ..hash import reverse_hash

REDDCOIN_API_BASE_URL = "http://reddcoin-insight:3001"

from ..constants import SATOSHIS_PER_COIN

from .blockchain_client import BlockchainClient

class ReddcoinComTestnetClient(BlockchainClient):
    def __init__(self, api_key=None):
        self.type = 'reddcoin.com'
        if api_key:
            self.auth = (api_key, '')
        else:
            self.auth = None

def format_unspents(unspents):
    """ Unconfirmed transactions missing confirmation count -> add as zero
    """
    for s in unspents:
        if "confirmations" not in s:
            s["confirmations"] = 0

    print unspents

    return [{
        "transaction_hash": s["txid"],
        "output_index": s["vout"],
        "value": int(round(s["amount"] * SATOSHIS_PER_COIN)),
        "script_hex": s["scriptPubKey"],
        "confirmations": s["confirmations"]
        }
        for s in unspents
    ]

def get_unspents(address, blockchain_client=ReddcoinComTestnetClient()):
    """ Get the spendable transaction outputs, also known as UTXOs or
        unspent transaction outputs.
    """
    if not isinstance(blockchain_client, ReddcoinComTestnetClient):
        raise Exception('A ReddcoinComTestnetClient object is required')

    url = REDDCOIN_API_BASE_URL + "/api/addr/"+ address +"/utxo?noCache=1"

    auth = blockchain_client.auth
    if auth and len(auth) == 2 and isinstance(auth[0], str):
        url = url + "&api_code=" + auth[0]

    r = requests.get(url, auth=auth)
    try:
        unspents = r.json()
    except ValueError, e:
        raise Exception('Invalid response from testnet reddcoin.com.')
    print unspents
    return format_unspents(unspents)

def broadcast_transaction(hex_tx, blockchain_client=ReddcoinComTestnetClient()):
    """ Dispatch a raw transaction to the network.
    """
    url = REDDCOIN_API_BASE_URL + '/api/tx/send'
    payload = {'rawtx': hex_tx}
    #r = requests.post(url, data=payload, auth=blockchain_client.auth)
    r = requests.post(url, data=payload)

    print r.text

    try:
        data = r.json()
    except ValueError, e:
        raise Exception('Received non-JSON from testnet reddcoin.com.')
            
    if 'txid' in data:
        reply = {}
        reply['tx_hash'] = data['txid']
        reply['success'] = True
        return reply
    else:
        raise Exception('Invalid response from testnet reddcoin.com.')


