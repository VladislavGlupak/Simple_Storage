
import json

from web3 import Web3
from solcx import compile_standard, install_solc
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

install_solc("0.6.0")

# Solidity source code
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]
# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# connect provider
#w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545"))
w3 = Web3(Web3.HTTPProvider("https://rinkeby.infura.io/v3/87384ed0ec934dc0a234ced9d6b43676"))

#chain_id = 1337
chain_id = 4 # Rinkeby
#address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1" # fake
address = "0x2b418C513E70dcb00b29B259641a6559613DC6b3" # Rinkeby
private_key = os.getenv("PRIVATE_KEY") # add 0x at the front

SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode) # contract

# 1. Build contract deploy tx
# 2. sign tx
# 3. send tx

# nonce
nonce = w3.eth.getTransactionCount(address)
print(f"Nonce: {nonce}")

# create tx instance
tx = SimpleStorage.constructor().buildTransaction({
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": address,
        "nonce": nonce,
    }
)

# Sign the transaction
signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
print("Deploying Contract!")

# deploy contract 
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
# Wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")

tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Done! Contract deployed to {tx_receipt.contractAddress}")

# Working with the contract
# We need: 1. contract address and 2. ABI

contract = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

print(contract.functions.retrieve().call()) # calling is just simulations

# 1. create transaction
store_tx = contract.functions.store(15).buildTransaction({
    "chainId": chain_id,
    "gasPrice": w3.eth.gas_price,
    "from": address,
    "nonce": nonce+1,
})
# 2. sign transaction
signed_tx = w3.eth.account.sign_transaction(store_tx, private_key=private_key)
# 3. send transaction
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(contract.functions.retrieve().call())
