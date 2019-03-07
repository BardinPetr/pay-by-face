#!/usr/bin/env python

from sys import argv
from tools import *
from web3 import HTTPProvider, Web3, eth

### Put your code below this comment ###

web3 = Web3(HTTPProvider(parceJson('network.json')['rpcUrl']))


def request_balance(uid, pin):
    addr = toAddress(get_private_key(uid, pin))
    return web3.eth.getBalance(addr)


if __name__ == '__main__':
    args = argv[1:]
    if len(args) > 0:
        if args[0] == '--balance':
            try:
                print("Your balance is " + ' '.join(weighing(request_balance(parceJson('person.json')['id'], args[1]))))
            except TypeError:
                print("ID is not found")
