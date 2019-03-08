#!/usr/bin/env python

from web3 import HTTPProvider, Web3, eth
from ethWrapper import ContractWrapper, gas_price
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
            _ = data['registrar']
        except:
            print("No contract address")
            return

        contract = None
        try:
            ethWrapper.user_priv_key = pk
            web3.eth.defaultAccount = addr
            contract = ContractWrapper(w3=web3, abi=registrar_ABI, address=data['registrar']['address'])
            res = contract.isInAddPending() or contract.getByAddr(addr) != ""
            if res:
                print("Registration request already sent")
                return
        except Exception:
            print("Seems that the contract address is not the registrar contract")
            return

        try:
            res = contract.add(args[1])
            print("Registration request sent by", res['transactionHash'].hex())
        except:
            print("No funds to send the request")
            return
    else:
        print("Incorrect phone number")


def send_del_user(args):
    addr, pk = None, None
    try:
        pk = get_private_key(parceJson('person.json')['id'], args[0])
        addr = toAddress(pk)
    except TypeError:
        print("ID is not found")
        return

    data = None
    try:
        data = parceJson('registrar.json')
        _ = data['registrar']
    except:
        print("No contract address")
        return

    contract = None
    try:
        ethWrapper.user_priv_key = pk
        web3.eth.defaultAccount = addr
        contract = ContractWrapper(w3=web3, abi=registrar_ABI, address=data['registrar']['address'])
        if contract.getByAddr(addr) == "":
            print("Account is not registered yet")
            return
        if contract.isInDelPending():
            print("Unregistration request already sent")
            return
    except Exception:
        print("Seems that the contract address is not the registrar contract.")
        return

    try:
        res = contract.dlt()
        print("Unregistration request sent by", res['transactionHash'].hex())
    except:
        print("No funds to send the request")
        return


def send_cancel_user(args):
    addr, pk = None, None
    try:
        pk = get_private_key(parceJson('person.json')['id'], args[0])
        addr = toAddress(pk)
    except TypeError:
        print("ID is not found")
        return

    data = None
    try:
        data = parceJson('registrar.json')
        _ = data['registrar']
    except:
        print("No contract address")
        return

    contract, mode = None, -1
    try:
        ethWrapper.user_priv_key = pk
        web3.eth.defaultAccount = addr
        contract = ContractWrapper(w3=web3, abi=registrar_ABI, address=data['registrar']['address'])
        mode = contract.isInAddPending()
        if not mode and not contract.isInDelPending():
            print("No requests found")
            return
    except Exception:
        print("Seems that the contract address is not the registrar contract.")
        return

    try:
        res = contract.cancel()
        print(("R" if mode else "Unr") + "egistration canceled by", res['transactionHash'].hex())
    except Exception as ex:
        print("No funds to send the request", ex)
        return


def send(pin, phone, val):
    priv_key = get_private_key(parceJson('person.json')['id'], pin)

    registrar = ContractWrapper(w3=web3, abi=registrar_ABI, address=contracts_data['registrar']['address'])

    sendto_addr = registrar.get(phone)

    if sendto_addr != '0x0000000000000000000000000000000000000000':
        try:
            transaction = {
            'to': sendto_addr,
            'value': val,
            'gas': 21000,
            'gasPrice': gas_price,
            'nonce': web3.eth.getTransactionCount(web3.eth.defaultAccount)
            }

            signed = web3.eth.account.signTransaction(transaction, priv_key)
            web3.eth.sendRawTransaction(signed.rawTransaction)

            print()
        except:
            print('No funds to send the payment')
    else:
        print('No account with the phone number: ' + phone)



commands = {
    'balance': request_balance,
    'add': send_add_user,
    'del': send_del_user,
    'cancel': send_cancel_user,
    'send': send
}

# === Entry point === #
if __name__ == '__main__':
    try:
        commands[argv[1][2:]](argv[2:])
    except IndexError:
        pass
