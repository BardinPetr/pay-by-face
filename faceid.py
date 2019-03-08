#!/usr/bin/env python

from web3 import HTTPProvider, Web3, eth
from sys import argv
from tools import *
import re

### Put your code below this comment ###

web3 = Web3(HTTPProvider(parceJson('network.json')['rpcUrl']))


def request_balance(args):
    try:
        addr = toAddress(get_private_key(parceJson('person.json')['id'], args[0]))
        print("Your balance is " + ' '.join(weighing(web3.eth.getBalance(addr))))
    except TypeError:
        print("ID is not found")


def send_add_user(args):
    try:
        addr = toAddress(get_private_key(parceJson('person.json')['id'], args[0]))
    except TypeError:
        print("ID is not found")
        return
    if len(args) > 1 and re.match("^\+\d{11}$", args[1]):

    else:
        print("Incorrect phone number")




commands = {
    'balance': request_balance,
    'add': send_add_user
}

# === Entry point === #
if __name__ == '__main__':
    try:
        commands[argv[1][2:]](argv[2:])
    except IndexError:
        pass
