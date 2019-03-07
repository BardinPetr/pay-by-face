from eth_account import Account
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
    return Account.privateKeyToAccount('0x' + priv_key).address


def get_private_key(uid, pin):
    pin = map(int, str(pin))
    u = uuid.UUID(uid)
    a = Web3.sha3(text="")
    for _ in range(4):
        a = Web3.sha3(a + u.bytes + pin.__next__().to_bytes(1, "little"))
    return a.hex()

