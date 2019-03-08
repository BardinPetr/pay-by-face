#!/usr/bin/env python

from web3 import HTTPProvider, Web3, eth
from ethWrapper import ContractWrapper
from requests import get as getData
from sys import argv
from tools import *
import ethWrapper
import re

### Put your code below this comment ###

web3 = Web3(HTTPProvider(parceJson('network.json')['rpcUrl']))

registrar_ABI = parceJson('contracts/registrar/ABI.json')

network = parceJson('network.json')

try:
    ethWrapper.gas_price = int(getData(network['gasPriceUrl']).json()['fast'] * 1000000000)
except:
    ethWrapper.gas_price = int(network['defaultGasPrice'])


def request_balance(args):
    try:
        print("Your balance is " + ' '.join(weighing(
            get_balance_by_priv(web3, get_private_key(parceJson('person.json')['id'], args[0])))))
    except TypeError:
        print("ID is not found")


def send_add_user(args):
    addr, pk = None, None
    try:
        pk = get_private_key(parceJson('person.json')['id'], args[0])
        addr = toAddress(pk)
    except TypeError:
        print("ID is not found")
        return
    if len(args) > 1 and re.match("^\+\d{11}$", args[1]):
        data = None
        try:
            data = parceJson('registrar.json')
        except TypeError:
            print("No contract address")
            return

        contract = None
        try:
            ethWrapper.user_priv_key = pk
            web3.eth.defaultAccount = addr
            contract = ContractWrapper(w3=web3, abi=registrar_ABI, address=data['registrar']['address'])
            res = contract.isInAddPending()
            if res:
                print("Registration request already sent")
                return
        except:
            print("Seems that the contract address is not the registrar contract")
            return

        try:
            contract.add(args[1])
            print("Registration request sent by", addr)
        except:
            print("No funds to send the request")
            return
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
