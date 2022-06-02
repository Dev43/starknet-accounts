import os
import json

from pathlib import Path
from starknet_py.contract import Contract
from starknet_py.net.client import Client, InvokeFunction
from starkware.python.utils import from_bytes
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.core.os.transaction_hash.transaction_hash import TransactionHashPrefix, calculate_transaction_hash_common

VERSION = 0
MAX_FEE = 0
TESTNET = from_bytes(b"SN_GOERLI")
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNT_FILE = os.path.join(ROOT_DIR, 'account.json')

def invoke_tx_hash(addr, calldata):
    exec_selector = get_selector_from_name("__execute__")
    return calculate_transaction_hash_common(
        tx_hash_prefix=TransactionHashPrefix.INVOKE,
        version=VERSION,
        contract_address=addr,
        entry_point_selector=exec_selector,
        calldata=calldata,
        max_fee=MAX_FEE,
        chain_id=TESTNET,
        additional_data=[],
    )

def mission_statement():
    print("\u001b[34;1m\u001b[4mYour mission:\u001b[0m\u001b[34m")
    return

async def print_n_wait(client: Client, invocation: InvokeFunction):
    print("\u001b[35mTransaction Hash: {}\u001b[0m\n".format(invocation.hash))
    await invocation.wait_for_acceptance()

    res = await client.get_transaction_status(invocation.hash)
    if "ACCEPT" in res["tx_status"]:
        print("\u001b[32;1mTx Results: Payday-{}".format(res["tx_status"]))
    else:
        print("\u001b[31;1mTx Results: {}".format(res["tx_status"]))
    
    print("\u001b[0m")

    return

async def deploy_testnet(contract_path="", constructor_args=[]):
    CONTRACT_ADDRESS="{}_ADDRESS".format(contract_path.upper())
    data = dict()
    if os.stat(ACCOUNT_FILE).st_size > 0 and os.getenv('ACCOUNT_CACHE') is None:
        with open(ACCOUNT_FILE) as json_file:
            data = json.load(json_file)
            if CONTRACT_ADDRESS in data:
                print("\u001b[35mFound local contract: {}\u001b[0m\n".format(data[CONTRACT_ADDRESS]))
                return int(data[CONTRACT_ADDRESS], 16)

    client = Client("testnet")

    os.system("starknet-compile --account_contract {}.cairo --output {}_compiled.json --abi {}_abi.json".format(contract_path, contract_path, contract_path))

    compiled = Path("{}_compiled.json".format(contract_path)).read_text()
    deployment_result = await Contract.deploy(
        client, compiled_contract=compiled, constructor_args=constructor_args
    )
    os.system("rm {}_compiled.json".format(contract_path))

    if not deployment_result.hash:
        raise ValueError("Failed to deploy contract")
        return ""

    print("\u001b[35mDeployment Initialized: ", deployment_result.hash)
    print("\tWaiting for successful deployment...")
    print("\tPatience is bitter, but its fruit is sweet...")

    await client.wait_for_tx(deployment_result.hash)
    res = await client.get_transaction(deployment_result.hash)

    data[CONTRACT_ADDRESS] = "0x{:02x}".format(res.transaction.contract_address)
    with open(ACCOUNT_FILE, 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4)
    print("\tSuccess - cached in accounts.json\u001b[0m\n")

    return res.transaction.contract_address