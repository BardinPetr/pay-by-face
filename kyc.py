#!/usr/bin/env python

### Put your code below this comment ###
import sys
from requests import get as getData
from ethWrapper import ContractWrapper
import ethWrapper
from tools import parceJson, toAddress
from web3 import Web3, HTTPProvider
from json import dump


# === Init === #




# === Commands === #
def get(phone_number):
    pass

commands = {
    'get': get
}


# === Entry point === #
if __name__ == '__main__':
    commands[sys.argv[1][2:]](*sys.argv[2:])
