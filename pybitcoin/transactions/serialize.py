# -*- coding: utf-8 -*-
"""
    pybitcoin
    ~~~~~

    :copyright: (c) 2014-2016 by Halfmoon Labs, Inc.
    :license: MIT, see LICENSE for more details.
"""

import bitcoin
import struct
import time

from binascii import hexlify, unhexlify

from .utils import flip_endian, variable_length_int
from ..constants import UINT_MAX, TX_VERSION


def serialize_input(input, signature_script_hex=''):
    """ Serializes a transaction input.
    """
    if not (isinstance(input, dict) and 'transaction_hash' in input \
            and 'output_index' in input):
        raise Exception('Required parameters: transaction_hash, output_index')

    if not 'sequence' in input:
        input['sequence'] = UINT_MAX

    return ''.join([
        flip_endian(input['transaction_hash']),
        hexlify(struct.pack('<I', input['output_index'])),
        hexlify(variable_length_int(len(signature_script_hex)/2)),
        signature_script_hex,
        hexlify(struct.pack('<I', input['sequence']))
    ])


def serialize_output(output):
    """ Serializes a transaction output.
    """
    if not ('value' in output and 'script_hex' in output):
        raise Exception('Invalid output')

    return ''.join([
        hexlify(struct.pack('<Q', output['value'])), # pack into 8 bites
        hexlify(variable_length_int(len(output['script_hex'])/2)),
        output['script_hex']
    ])


def serialize_transaction(inputs, outputs, lock_time=0, version=TX_VERSION):
    """ Serializes a transaction.
    """
    # add in the inputs
    serialized_inputs = ''.join([serialize_input(input) for input in inputs])

    # add in the outputs
    serialized_outputs = ''.join([serialize_output(output) for output in outputs])

    timestamp = int(time.time())

    return ''.join([
        # add in the version number
        hexlify(struct.pack('<I', version)),
        # add in the number of inputs
        hexlify(variable_length_int(len(inputs))),
        # add in the inputs
        serialized_inputs,
        # add in the number of outputs
        hexlify(variable_length_int(len(outputs))),
        # add in the outputs
        serialized_outputs,
        # add in the lock time
        hexlify(struct.pack('<I', lock_time)),
        # add in the PoSV time
        hexlify(struct.pack('<I', timestamp)),
    ])


def deserialize_transaction(tx_hex):
    """
        Given a serialized transaction, return its inputs, outputs,
        locktime, and version

        Each input will have:
        * transaction_hash: string
        * output_index: int
        * [optional] sequence: int
        * [optional] script_sig: string

        Each output will have:
        * value: int
        * script_hex: string
    """

    tx = bitcoin.deserialize(str(tx_hex))

    inputs = tx["ins"]
    outputs = tx["outs"]

    ret_inputs = []
    ret_outputs = []

    for inp in inputs:
        ret_inp = {
            "transaction_hash": inp["outpoint"]["hash"],
            "output_index": int(inp["outpoint"]["index"]),
        }

        if "sequence" in inp:
            ret_inp["sequence"] = int(inp["sequence"])

        if "script" in inp:
            ret_inp["script_sig"] = inp["script"]

        ret_inputs.append(ret_inp)

    for out in outputs:
        ret_out = {
            "value": out["value"],
            "script_hex": out["script"]
        }

        ret_outputs.append(ret_out)

    return ret_inputs, ret_outputs, tx["locktime"], tx["version"], tx["time"]
