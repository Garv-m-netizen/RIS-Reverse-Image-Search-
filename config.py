"""
Configuration module for Face Verification Pipeline.
Loads environment variables from .env file and provides central access to API tokens,
blockchain network RPCs, wallet keys, and smart contract details.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from the current directory or parent
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Bright Data API Config
BRIGHT_DATA_API_TOKEN = os.getenv("BRIGHT_DATA_API_TOKEN", "").strip()
BRIGHT_DATA_ENDPOINT = os.getenv(
    "BRIGHT_DATA_ENDPOINT", "https://api.brightdata.com/dca"
).strip()
BRIGHT_DATA_DATASET_ID = os.getenv("BRIGHT_DATA_DATASET_ID", "").strip()

# SerpAPI Config (Google Lens reverse image search)
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "").strip()

# Ethereum Sepolia Blockchain Config
SEPOLIA_PROVIDER_URL = os.getenv("SEPOLIA_PROVIDER_URL", "").strip()
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "").strip()
WALLET_PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY", "").strip()
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "").strip()
ETHERSCAN_BASE_URL = os.getenv("ETHERSCAN_BASE_URL", "https://sepolia.etherscan.io/tx/").strip()

# Face Detection Config
INSIGHTFACE_MODEL_NAME = os.getenv("INSIGHTFACE_MODEL_NAME", "buffalo_l").strip()
FACE_EMBEDDING_DIM = 512

def validate_config():
    """
    Validates required environment variables and returns a dict with status and missing keys.
    """
    missing = []
    if not BRIGHT_DATA_API_TOKEN:
        missing.append("BRIGHT_DATA_API_TOKEN")
    if not SEPOLIA_PROVIDER_URL:
        missing.append("SEPOLIA_PROVIDER_URL")
    if not CONTRACT_ADDRESS:
        missing.append("CONTRACT_ADDRESS")
    if not WALLET_PRIVATE_KEY:
        missing.append("WALLET_PRIVATE_KEY")
    if not WALLET_ADDRESS:
        missing.append("WALLET_ADDRESS")
        
    return {
        "valid": len(missing) == 0,
        "missing": missing
    }

def print_config_status():
    """Prints configuration diagnostic summary to console."""
    status = validate_config()
    print("--- Configuration Diagnostics ---")
    if status["valid"]:
        print("[OK] All required environment variables are configured!")
    else:
        print(f"[!] Missing environment variables: {', '.join(status['missing'])}")
        print("Please configure them in your .env file for live production execution.")
    print("--------------------------------")

if __name__ == "__main__":
    print_config_status()
