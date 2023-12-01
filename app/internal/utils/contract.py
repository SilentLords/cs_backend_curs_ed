import decimal

from web3 import Web3

from app.configuration.settings import settings
from app.internal.utils import bscscan
from app.internal.utils.bsc import call_contract_function_via_wallet



def withdraw_money_to_address(address, amount_in_evo):
    print(f"amount_in_evo: {amount_in_evo}")
    bsc = settings.bsc_node_url
    web3 = Web3(Web3.HTTPProvider(bsc))

    abi = bscscan.get_ABI(settings.corporate_payouts_contract_address)
    res = call_contract_function_via_wallet(settings.corporate_contract_admin_private_key, settings.corporate_contract_admin_address, abi, settings.corporate_payouts_contract_address, "transferFromContract",
                                            [web3.to_checksum_address(address), amount_in_evo])

    return True