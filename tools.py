from eth_account import Account
from math import ceil
from json import load
from web3 import Web3
import uuid


def parceJson(file_path):
    try:
        with open(file_path) as f:
            content = load(f)
        return content
    except FileNotFoundError:
        return None


def toAddress(priv_key):
    prefix = '' if priv_key.startswith('0x') else '0x'
    return Account.privateKeyToAccount(prefix + priv_key).address


def get_private_key(uid, pin):
    pin = map(int, str(pin))
    u = uuid.UUID(uid)
    a = Web3.sha3(text="")
    for _ in range(4):
        a = Web3.sha3(a + u.bytes + pin.__next__().to_bytes(1, "little"))
    return a.hex()


nominal = ['kwei', 'mwei', 'gwei', 'szabo', 'finney', 'poa']


def weighing(val):
    k = min(ceil(len(str(val)) / 3) - 1, 6)
    val = round(int(val) / 10 ** (k * 3), 6)
    return str(val).rstrip('0').rstrip('.'), nominal[k - 1] if k != 0 else ("poa" if val == 0 else "wei")
