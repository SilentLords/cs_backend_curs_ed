import decimal

from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware

from app.configuration.settings import settings
from app.internal.utils import bscscan

from app.internal.utils.blockchain_utils import convert_blockchain_value_to_decimal


def call_contract_function(abi, contract_address, function_name, args):
    # Подключаемся к узлу BSC, можно изменить на другой провайдер
    web3 = Web3(HTTPProvider(settings.bsc_node_url))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Проверяем, что узел подключен
    if not web3.is_connected():
        print("Не удалось подключиться к узлу BSC.")
        return

    # Загружаем ABI смартконтракта
    contract = web3.eth.contract(address=contract_address, abi=abi)

    # Получаем объект функции по имени
    function = contract.functions[function_name]

    # Вызываем функцию с аргументами
    result = function(*args).call()

    # Выводим результат в консоль
    print(f"Результат вызова функции {function_name}: {result}")

    return result


def call_contract_function_via_wallet(private_key, caller, abi, contract_address, function_name, args):
    # Подключаемся к узлу BSC, можно изменить на другой провайдер
    bsc = settings.bsc_node_url
    web3 = Web3(Web3.HTTPProvider(bsc))

    # Проверяем, что узел подключен
    if not web3.is_connected():
        print("Не удалось подключиться к узлу BSC.")
        return

    web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    nonce = web3.eth.get_transaction_count(caller)

    # Загружаем ABI смартконтракта
    contract = web3.eth.contract(address=contract_address, abi=abi)
    function = contract.functions[function_name]
    сhain_id = 56 # bsc

    print(type(function))

    # return function(*args).transact()

    # Call your function
    call_function = function(*args).build_transaction({
        'chainId': сhain_id,
        'nonce': nonce,
        'from': caller
    })

    # Sign transaction
    signed_tx = web3.eth.account.sign_transaction(call_function, private_key=private_key)

    # Send transaction
    send_tx = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    # Wait for transaction receipt
    tx_receipt = web3.eth.wait_for_transaction_receipt(send_tx)
    print(tx_receipt)