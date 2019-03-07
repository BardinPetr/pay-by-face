from eth_account import Account
from json import load



def parceJson(file_path):
    try:
        with open(file_path) as f:
            content = load(f)
        return content
    except FileNotFoundError:
        return None

def toAddress(priv_key):
    return Account.privateKeyToAccount('0x' + priv_key).address