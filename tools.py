from eth_account import Account
from math import ceil
from json import load
from web3 import Web3, HTTPProvider
import uuid
import sha3


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


def keccak256(data):
    k = sha3.keccak_256()
    k.update(data)
    return k


def get_private_key(uid, pin):
    pin = map(int, str(pin))
    u = uuid.UUID(uid)
    a = keccak256("".encode())
    for _ in range(4):
        a = keccak256(a.digest() + u.bytes + pin.__next__().to_bytes(1, "little"))
    return a.hexdigest()


nominal = ['wei', 'kwei', 'mwei', 'gwei', 'szabo', 'finney', 'poa']


def weighing(val):
    k = min(ceil(len(str(val)) / 3) - 1, 6)
    val = round(int(val) / 10 ** (k * 3), 6)
    return str(val).rstrip('0').rstrip('.'), nominal[k] if val != 0 else "poa"


def get_balance(web3, addr):
    return web3.eth.getBalance(addr)


def get_balance_by_priv(web3, priv):
    return web3.eth.getBalance(toAddress(priv))
