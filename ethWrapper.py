# NOTE: данный класс не поддерживает эвенты (но они нам и не нужны),
# а так-же при создании функций из заготовленных атрибутов последние будут переопределяться
# это относится к (gas_price, user_priv_key)
class ContractWrapper:
    gas_price = None
    user_priv_key = None

    def __init__(self, w3=None, **kwargs):
        """
        с w3.eth.defaultAccount будут отправляться транзакции.
        обязательно перед вызовом методов контракта укажите!!
        ContractWrapper.gas_price и ContractWrapper.user_priv_key

        Методы автоматически определяются как call или buildTransaction
        > методы определенные как call возвращают результат функции
        > методы определенные как bT возвращают рецепт отправленной транзакции

        Args:
            w3 (Web3): экземпляр web3 для общения с блокчеином.
            **kwargs (type): парамтры как для eth.contract().
        """

        contract = w3.eth.contract(**kwargs)

        # setup constructor
        def construct(*args, **kwargs):
            tx = contract.constructor(*args, **kwargs).buildTransaction({
                'gasPrice': self.gas_price,
                'nonce': w3.eth.getTransactionCount(w3.eth.defaultAccount)
            })

            signed = w3.eth.account.signTransaction(tx, private_key=self.user_priv_key)
            tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)

            tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

            return tx_receipt

        setattr(self, 'constructor', construct)


        # setup contract methods
        for elem in kwargs['abi']:
            if 'name' in elem:
                # choose call or buildTransaction
                if elem['stateMutability'] == 'view':
                    def funct(name):
                        def func(*args, **kwargs):
                            return getattr(contract.functions, name)(*args, **kwargs).call()
                        return func

                elif elem['stateMutability'] == 'nonpayable':
                    def funct(name):
                        def func(*args, **kwargs):
                            tx = getattr(contract.functions, name)(*args, **kwargs).buildTransaction({
                                'gasPrice': self.gas_price,
                                'nonce': w3.eth.getTransactionCount(w3.eth.defaultAccount)
                                })

                            signed = w3.eth.account.signTransaction(tx, private_key=self.user_priv_key)
                            tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)

                            tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

                            return tx_receipt
                        return func

                setattr(self, elem['name'], funct(elem['name']))