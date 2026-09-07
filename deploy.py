"""
Deployment script for HashRegistry.sol to Ethereum Sepolia Testnet.
Compiles HashRegistry.sol using py-solc-x and deploys using Web3.py.
Automatically updates CONTRACT_ADDRESS in .env file upon successful deployment.
"""

import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv
from web3 import Web3

import solcx

def main():
    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(dotenv_path=env_path)

    provider_url = os.getenv("SEPOLIA_PROVIDER_URL", "").strip()
    private_key = os.getenv("WALLET_PRIVATE_KEY", "").strip()
    wallet_address = os.getenv("WALLET_ADDRESS", "").strip()

    if not provider_url:
        print("[!] ERROR: SEPOLIA_PROVIDER_URL is missing in .env")
        sys.exit(1)

    if not private_key or private_key.startswith("0x000000000000"):
        print("[!] ERROR: Please set your actual WALLET_PRIVATE_KEY in .env before deploying.")
        sys.exit(1)

    print("[1/5] Connecting to Sepolia Testnet RPC...")
    w3 = Web3(Web3.HTTPProvider(provider_url))
    if not w3.is_connected():
        print(f"[!] Unable to connect to Sepolia provider URL: {provider_url}")
        sys.exit(1)

    chain_id = w3.eth.chain_id
    print(f"    Connected to chain ID: {chain_id}")

    # Derive wallet address if not provided
    account = w3.eth.account.from_key(private_key)
    sender_address = account.address
    print(f"    Deployer Wallet Address: {sender_address}")

    balance_wei = w3.eth.get_balance(sender_address)
    balance_eth = w3.from_wei(balance_wei, 'ether')
    print(f"    Wallet Balance: {balance_eth:.6f} SepoliaETH")

    if balance_wei == 0:
        print("[!] WARNING: Wallet balance is 0 SepoliaETH. Please fund wallet using a Sepolia Faucet.")
        print("    Google Sepolia Faucet: https://cloud.google.com/application/button/faucet/ethereum/sepolia")
        sys.exit(1)

    print("\n[2/5] Compiling HashRegistry.sol...")
    solcx.install_solc('0.8.20')
    solcx.set_solc_version('0.8.20')

    sol_path = Path(__file__).resolve().parent / "hash_registry.sol"
    compiled_sol = solcx.compile_files(
        [str(sol_path)],
        output_values=['abi', 'bin'],
        solc_version='0.8.20'
    )

    contract_id = list(compiled_sol.keys())[0]
    abi = compiled_sol[contract_id]['abi']
    bytecode = compiled_sol[contract_id]['bin']
    print("    Contract compiled successfully!")

    print("\n[3/5] Building Deployment Transaction...")
    HashRegistry = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(sender_address)

    gas_price = w3.eth.gas_price
    transaction = HashRegistry.constructor().build_transaction({
        'chainId': chain_id,
        'gasPrice': gas_price,
        'from': sender_address,
        'nonce': nonce
    })

    # Estimate gas
    try:
        estimated_gas = w3.eth.estimate_gas(transaction)
        transaction['gas'] = int(estimated_gas * 1.2)
    except Exception as e:
        print(f"    Gas estimation note: {e}, setting fallback gas limit 1,500,000")
        transaction['gas'] = 1500000

    print("\n[4/5] Signing & Broadcasting Transaction...")
    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"    Transaction Hash: 0x{tx_hash.hex()}")
    print("    Waiting for block confirmation...")

    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    contract_address = tx_receipt.contractAddress

    print(f"\n[5/5] CONTRACT SUCCESSFULLY DEPLOYED!")
    print(f"    Contract Address: {contract_address}")
    print(f"    View on Etherscan: https://sepolia.etherscan.io/address/{contract_address}")

    # Update .env file
    env_text = env_path.read_text(encoding='utf-8')
    new_env_text = re.sub(
        r'CONTRACT_ADDRESS=.*',
        f'CONTRACT_ADDRESS={contract_address}',
        env_text
    )
    new_env_text = re.sub(
        r'WALLET_ADDRESS=.*',
        f'WALLET_ADDRESS={sender_address}',
        new_env_text
    )
    env_path.write_text(new_env_text, encoding='utf-8')
    print("    Updated CONTRACT_ADDRESS and WALLET_ADDRESS in .env automatically!")

if __name__ == '__main__':
    main()
