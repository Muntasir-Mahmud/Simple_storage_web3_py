import json
import os

from dotenv import load_dotenv
from eth_utils import address
from solcx import compile_standard, install_solc
from web3 import Web3

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

install_solc("0.6.0")

# Compile Our solidity
compile_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled-code.json", "w") as file:
    json.dump(compile_sol, file)


# get Bytecode
bytecode = compile_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get ABI
abi = compile_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# for connecting to Rinkbey
w3 = Web3(
    Web3.HTTPProvider("https://rinkeby.infura.io/v3/5a3bf6cd8ee1469294261c225f81a006")
)
chain_id = 4
my_address = "0xF587fFfe379eC702AE9dBbd8514372fe5a58ce81"
private_key = os.getenv("PRIVATE_KEY")

# Create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# get the latest transaction, not the mining nonce
nonce = w3.eth.getTransactionCount(my_address)

# 1. Bild a tracsaction
transaction = SimpleStorage.constructor().buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce}
)

# 2. Sign the tracsaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# 3. Send the signed transaction
print("Deploying Contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

# block conformation
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")

# Working with new contract
# we need 1. Contract Address, 2. Contract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# There are 2 ways to interect with SC
# 1. Call   -> Simulate making the call and getting a return value (like the blue button of remix)
# 2. Transact   -> Actually make a state change

# Initial value of favourite number
print("Updating contract...")
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce + 1}
)

sign_store_tx = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)

# send the signed contract
send_store_tx = w3.eth.send_raw_transaction(sign_store_tx.rawTransaction)

tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)

print("Updated!")
print(simple_storage.functions.retrieve().call())
