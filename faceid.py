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

api_data = parceJson("faceapi.json")
key = api_data["key"]
base_url = api_data["serviceUrl"]
cf.Key.set(key)
cf.BaseUrl.set(base_url)
g_id = api_data["groupId"]

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
            contract.add(args[1])
            print("Registration request sent by", addr)
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
        contract.dlt()
        print("Unregistration request sent by", addr)
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

    contract, type = None, -1
    try:
        ethWrapper.user_priv_key = pk
        web3.eth.defaultAccount = addr
        contract = ContractWrapper(w3=web3, abi=registrar_ABI, address=data['registrar']['address'])
        if contract.getWaitingAdditionCnt() + contract.getWaitingDeletionCnt() == 0:
            print("No requests found")
            return
    except Exception:
        print("Seems that the contract address is not the registrar contract.")
        return

    try:
        contract.cancel()
    except:
        print("No funds to send the request")
        return

def send(pin, phone, val):
    pass


def idetify_person(video):
    simple = not os.path.exists("actions.json")
    if exist_group():
        res = check_all_right(cf.person_group.get, g_id)
        if res.setdefault("userData") == "trained":
            if simple:
                faces = create_frames_simple(video)
                if faces:
                    candidate = get_predict(faces)
                    if candidate:
                        open("person.json", "w").write(str({"id": candidate}))
                    else:
                        print("The person was not found")
                    clear(5)
                else:
                    print("The video does not follow requirements")
            else:
                pass
        else:
            print("The service is not ready")
            if os.path.exists("person.json"):
                os.remove("person.json")
    else:
        print("The service is not ready")


commands = {
    'balance': request_balance,
    'add': send_add_user,
    'del': send_del_user,
    'cancel': send_cancel_user,
    'send': send,
    'find': idetify_person
}
# === Entry point === #
if __name__ == '__main__':
    try:
        commands[argv[1][2:]](argv[2:])
    except IndexError:
        pass
