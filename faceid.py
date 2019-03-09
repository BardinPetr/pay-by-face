#!/usr/bin/env python

from network import contracts_data
from ethWrapper import ContractWrapper, gas_price
from sys import argv

from tools import *
import ethWrapper
from requests import get as getData
import re

### Put your code below this comment ###

web3 = Web3(HTTPProvider(parceJson('network.json')['rpcUrl']))

registrar_ABI = parceJson('contracts/registrar/ABI.json')

api_data = parceJson("faceapi.json")
key = api_data["key"]
base_url = api_data["serviceUrl"]
cf.Key.set(key)
cf.BaseUrl.set(base_url)
g_id = api_data["groupId"]


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
            res = contract.add(args[1], cb=lambda tx: print("Registration request sent by", tx.hex()))
        except Exception as ex:
            print("No funds to send the request", ex)
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
        res = contract.dlt(cb=lambda tx: print("Unregistration request sent by", tx.hex()))
    except:
        print("No funds to send the request")
        return


def send_cancel_user(args, ttl=4):
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
        res = contract.cancel(cb=lambda tx: print(("R" if mode else "Unr") + "egistration canceled by", tx.hex()))
    except Exception as ex:
        if str(ex).find('-32016') > -1:
            return
        if ttl > 0:
            send_cancel_user(args, ttl - 1)
        print("No funds to send the request")


def send(a):
    pin = a[0]
    phone = a[1]
    val = a[2]

    if not re.match("^\+\d{11}$", phone):
        print("Incorrect phone number")
        return

    try:
        priv_key = get_private_key(parceJson('person.json')['id'], pin)
        addr = toAddress(priv_key)
    except TypeError:
        print("ID is not found")
        return

    ethWrapper.user_priv_key = priv_key
    web3.eth.defaultAccount = addr
    registrar = ContractWrapper(w3=web3, abi=registrar_ABI, address=contracts_data['registrar']['address'])

    sendto_addr = registrar.get(phone)

    if sendto_addr != '0x0000000000000000000000000000000000000000':
        try:
            transaction = {
                'to': sendto_addr,
                'value': int(val),
                'gas': 21000,
                'gasPrice': gas_price,
                'nonce': web3.eth.getTransactionCount(web3.eth.defaultAccount)
            }

            signed = web3.eth.account.signTransaction(transaction, priv_key)
            tx_hash = web3.eth.sendRawTransaction(signed.rawTransaction)

            tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

            val, tp = weighing(val)

            print('Payment of {} {} to {} scheduled'.format(val, tp, phone))
            print('Transaction Hash: ' + web3.toHex(tx_hash))
        except Exception as ex:
            print('No funds to send the payment', ex)
    else:
        print('No account with the phone number: ' + phone)


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


def ops(a):
    pvk = get_private_key(parceJson('person.json')['id'], a[0])
    addr = toAddress(pvk)

    response = getData('https://blockscout.com/poa/sokol/api', params={
        'module':'account',
        'action':'txlist',
        'address': addr,
        'startblock': parceJson('registrar.json')['registrar']['startBlock']}).json()

    print(response['result'])




commands = {
    'balance': request_balance,
    'add': send_add_user,
    'del': send_del_user,
    'cancel': send_cancel_user,
    'send': send,
    'find': idetify_person,
    'ops': ops
}
# === Entry point === #
if __name__ == '__main__':
    try:
        commands[argv[1][2:]](argv[2:])
    except IndexError:
        pass
