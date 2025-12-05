import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
RPC_URL = os.getenv("RPC_URL", "https://zetachain-athens-evm.blockpi.network/v1/rpc/public")

if not PRIVATE_KEY:
    # Handle missing private key gracefully for demo purposes or raise error
    pass

w3 = Web3(Web3.HTTPProvider(RPC_URL))

def get_address():
    if not PRIVATE_KEY:
        return None
    account = w3.eth.account.from_key(PRIVATE_KEY)
    return account.address

def send_zeta(to_address: str, amount: float):
    if not PRIVATE_KEY:
        raise ValueError("Private key not found in .env")

    account = w3.eth.account.from_key(PRIVATE_KEY)
    from_address = account.address
    
    # Convert amount to Wei
    value_wei = w3.to_wei(amount, 'ether')
    
    # Get nonce
    nonce = w3.eth.get_transaction_count(from_address)
    
    # Build transaction
    tx = {
        'nonce': nonce,
        'to': w3.to_checksum_address(to_address),
        'value': value_wei,
        'gas': 2000000, 
        'gasPrice': w3.eth.gas_price,
        'chainId': w3.eth.chain_id
    }
    
    # Sign transaction
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    
    # Send transaction
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    return w3.to_hex(tx_hash)
