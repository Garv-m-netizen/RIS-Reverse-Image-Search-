"""
Blockchain verification module using Web3.py.
Interacts with HashRegistry smart contract on Ethereum Sepolia Testnet.
"""

import json
import hashlib
import time
from pathlib import Path
from web3 import Web3
import config

class BlockchainVerifier:
    def __init__(self):
        self.provider_url = config.SEPOLIA_PROVIDER_URL
        self.contract_address = config.CONTRACT_ADDRESS
        self.private_key = config.WALLET_PRIVATE_KEY
        self.wallet_address = config.WALLET_ADDRESS
        self.w3 = None
        self.contract = None
        
        # Load ABI
        abi_path = Path(__file__).resolve().parent / "contract_abi.json"
        if abi_path.exists():
            with open(abi_path, "r", encoding="utf-8") as f:
                self.abi = json.load(f)
        else:
            self.abi = []

        self._init_web3()

    def _init_web3(self):
        """Initializes Web3 provider and contract instance if credentials are valid."""
        if self.provider_url:
            try:
                self.w3 = Web3(Web3.HTTPProvider(self.provider_url))
                if self.w3.is_connected() and self.contract_address and self.abi:
                    checksum_address = Web3.to_checksum_address(self.contract_address)
                    self.contract = self.w3.eth.contract(address=checksum_address, abi=self.abi)
            except Exception as e:
                print(f"⚠️ Web3 initialization warning: {e}")

    def is_configured(self) -> bool:
        """Returns True if real Web3 connection is established and wallet configured."""
        return (
            self.w3 is not None 
            and self.w3.is_connected() 
            and self.contract is not None 
            and bool(self.private_key) 
            and bool(self.wallet_address)
        )

    @staticmethod
    def create_post_hash(url: str, title: str, description: str = "") -> str:
        """
        Creates a SHA-256 hash of post data (URL + title + description).
        Returns a 0x-prefixed 64-character hex string (32 bytes).
        """
        combined = f"{url.strip()}|{title.strip()}|{description.strip()}"
        sha256_hex = hashlib.sha256(combined.encode("utf-8")).hexdigest()
        return f"0x{sha256_hex}"

    def store_hash_on_chain(self, hash_hex: str) -> dict:
        """
        Stores SHA-256 hash on Ethereum Sepolia testnet.
        
        Returns:
            dict with tx_hash, block_number, gas_used, timestamp, verifier, verified
        """
        if not hash_hex.startswith("0x"):
            hash_hex = "0x" + hash_hex

        hash_bytes32 = bytes.fromhex(hash_hex[2:])

        if self.is_configured():
            try:
                account = Web3.to_checksum_address(self.wallet_address)
                nonce = self.w3.eth.get_transaction_count(account)
                
                gas_price = self.w3.eth.gas_price
                priority_fee = self.w3.to_wei('1.5', 'gwei')
                max_fee = max(gas_price * 2, priority_fee + self.w3.to_wei('1', 'gwei'))
                if priority_fee > max_fee:
                    priority_fee = max_fee

                # Build transaction
                tx_build = self.contract.functions.storeHash(hash_bytes32).build_transaction({
                    'from': account,
                    'nonce': nonce,
                    'gas': 150000,
                    'maxFeePerGas': max_fee,
                    'maxPriorityFeePerGas': priority_fee,
                    'chainId': self.w3.eth.chain_id
                })

                # Sign transaction
                signed_tx = self.w3.eth.account.sign_transaction(tx_build, private_key=self.private_key)

                # Send transaction
                tx_hash_bytes = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_hash_hex = self.w3.to_hex(tx_hash_bytes)

                # Wait for transaction receipt
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash_bytes, timeout=120)

                block = self.w3.eth.get_block(receipt['blockNumber'])
                
                return {
                    "success": True,
                    "tx_hash": tx_hash_hex,
                    "block_number": receipt['blockNumber'],
                    "gas_used": receipt['gasUsed'],
                    "timestamp": block['timestamp'],
                    "verifier": account,
                    "etherscan_url": f"{config.ETHERSCAN_BASE_URL}{tx_hash_hex}",
                    "simulated": False
                }

            except Exception as e:
                err_msg = str(e)
                # Check if already registered on-chain
                if "already registered" in err_msg.lower():
                    return self.verify_hash_on_chain(hash_hex)
                raise RuntimeError(f"Blockchain Transaction Failed: {err_msg}")
        else:
            # Demonstration Fallback Mode when credentials are not yet configured in .env
            time.sleep(2.0)  # Simulate network latency
            sim_tx = "0x" + hashlib.sha256(f"sim_tx_{time.time()}".encode()).hexdigest()
            return {
                "success": True,
                "tx_hash": sim_tx,
                "block_number": 6482104,
                "gas_used": 48210,
                "timestamp": int(time.time()),
                "verifier": self.wallet_address or "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
                "etherscan_url": f"{config.ETHERSCAN_BASE_URL}{sim_tx}",
                "simulated": True
            }

    def verify_hash_on_chain(self, hash_hex: str) -> dict:
        """
        Queries the smart contract to verify if a hash exists on-chain.
        """
        if not hash_hex.startswith("0x"):
            hash_hex = "0x" + hash_hex

        hash_bytes32 = bytes.fromhex(hash_hex[2:])

        if self.is_configured():
            try:
                exists = self.contract.functions.verifyHash(hash_bytes32).call()
                if exists:
                    verifier = self.contract.functions.getVerifier(hash_bytes32).call()
                    ts = self.contract.functions.getTimestamp(hash_bytes32).call()
                    return {
                        "verified": True,
                        "verifier": verifier,
                        "timestamp": ts,
                        "simulated": False
                    }
                else:
                    return {"verified": False, "simulated": False}
            except Exception as e:
                return {"verified": False, "error": str(e), "simulated": False}
        else:
            return {
                "verified": True,
                "verifier": self.wallet_address or "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
                "timestamp": int(time.time()),
                "simulated": True
            }

if __name__ == "__main__":
    bv = BlockchainVerifier()
    test_hash = bv.create_post_hash("https://twitter.com/test/status/1", "Test Title")
    print(f"Generated Test Hash: {test_hash}")
    print(f"Is Blockchain Configured: {bv.is_configured()}")
