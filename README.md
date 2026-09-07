# 🏆 Face Verification Pipeline — AI & Sepolia Blockchain Desktop Utility

A modern, production-grade desktop application built with **PyQt5** featuring a clean macOS-style UI. It performs **AI face detection and 512-dim embedding extraction via InsightFace (`buffalo_l`)**, conducts **real reverse image web search via SerpAPI (Google Lens) & Catbox.moe**, and registers an immutable, tamper-proof audit record on the **Ethereum Sepolia Testnet** using a custom Solidity smart contract (`HashRegistry.sol`).

---

## 🎨 UI & Features Overview

- **macOS Desktop Utility Interface**: Modern card-based layout, sidebar navigation, confidence slider, clear execution logs, and identity match visualization.
- **AI Face Feature Extraction**: InsightFace `buffalo_l` model generates 512-dimensional facial embeddings and 5-point facial landmark arrays with OpenCV fallback support.
- **Real Reverse Image Search**: Automated catbox.moe hosting upload + SerpAPI Google Lens integration to find public profiles and matching web domains.
- **Ethereum Sepolia Proof of Identity**: Computes SHA-256 payload hashes and commits on-chain transactions via EIP-1559 gas estimation on Ethereum Sepolia Testnet.
- **Interactive Verification**: One-click hash copying, live transaction tracking, and direct Etherscan proof verification links.

---

## 📐 Project Architecture

```
[ User Input Image (JPG/PNG) ]
             │
             ▼
[ 1. InsightFace AI (buffalo_l) ]  ➜ Detect face bounding box, 5-point landmarks & 512-dim vector
             │
             ▼
[ 2. Public Cloud Hosting ]        ➜ Temporary upload to catbox.moe for public HTTPS URL
             │
             ▼
[ 3. SerpAPI (Google Lens) ]       ➜ Perform real reverse image search for matching social profiles
             │
             ▼
[ 4. SHA-256 Payload Hashing ]     ➜ Compute SHA-256 hash of matched metadata (URL + Title + Snippet)
             │
             ▼
[ 5. Ethereum Sepolia Blockchain ]  ➜ Broadcast `storeHash(bytes32)` transaction to smart contract
             │
             ▼
[ 6. PyQt5 Desktop Utility ]        ➜ Render live status logs, confidence bar & Etherscan proof
```

---

## 📁 Repository Structure

```
face-verification-pipeline/
├── main.py              # PyQt5 Desktop Application (macOS-style UI layout)
├── pipeline.py          # Asynchronous QThread pipeline (InsightFace + SerpAPI + Web3)
├── blockchain.py        # Web3.py smart contract integration & Sepolia EIP-1559 tx signing
├── config.py            # Environment variable loader & diagnostic checker
├── hash_registry.sol    # Solidity smart contract (`HashRegistry`)
├── contract_abi.json    # Compiled smart contract ABI
├── deploy.py            # Automatic smart contract deployment script
├── requirements.txt     # Python dependencies
├── .env.example         # Template for environment configuration
└── README.md            # Project documentation
```

---

## 🔑 STEP-BY-STEP SETUP GUIDE: How to Get All Required APIs

Follow these simple steps to obtain your API keys and testnet ETH:

### STEP 1: Get SerpAPI Key (Free 100 Searches/Month)
1. Register at [SerpAPI Signup](https://serpapi.com/users/sign_up).
2. Go to your [SerpAPI Dashboard](https://serpapi.com/dashboard).
3. Copy your **API Key**.
4. Add to `.env`:
   ```env
   SERPAPI_KEY=your_serpapi_api_key_here
   ```

---

### STEP 2: Get Sepolia RPC URL (Alchemy or Infura)
1. Register at [Alchemy.com](https://alchemy.com/).
2. Create an App for **Ethereum** on the **Sepolia Testnet**.
3. Copy your **HTTPS RPC Endpoint URL**.
4. Add to `.env`:
   ```env
   SEPOLIA_PROVIDER_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY
   ```

---

### STEP 3: Create a Sepolia Wallet & Get Free Testnet ETH
1. Install [MetaMask Browser Extension](https://metamask.io/).
2. Create or select a dedicated **Testnet Wallet**.
3. Switch network to **Sepolia**.
4. Get free Sepolia ETH from faucets:
   - [Alchemy Sepolia Faucet](https://sepoliafaucet.com/)
   - [Google Cloud Sepolia Faucet](https://cloud.google.com/application/button/faucet/ethereum/sepolia)
5. Export private key (*Account Details -> Show Private Key*).
6. Add to `.env`:
   ```env
   WALLET_ADDRESS=0xYourPublicWalletAddress
   WALLET_PRIVATE_KEY=0xYourPrivateKey
   ```

---

### STEP 4: Smart Contract Address
The smart contract `HashRegistry.sol` is already compiled and deployed on Sepolia Testnet at:
`0xC8486f7678806095332F7FCE1B4C998Ef2e2b829`

Alternatively, deploy your own using `deploy.py`:
```bash
python deploy.py
```
Then add to `.env`:
```env
CONTRACT_ADDRESS=0xYourDeployedContractAddress
```

---

## ⚙️ Installation & Execution

### 1. Clone Repository & Setup Environment
```bash
git clone https://github.com/Garv-m-netizen/RIS-Reverse-Image-Search-.git
cd RIS-Reverse-Image-Search-

python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create `.env` Configuration File
Copy `.env.example` to `.env` and fill in your keys:
```bash
cp .env.example .env
```

### 4. Launch Desktop GUI Application
```bash
python main.py
```

---

## 🎬 Screen Recording Presentation Script (45 Seconds)

| Timestamp | Action | Description |
|---|---|---|
| `0:00 - 0:05` | Launch application (`python main.py`) | "Welcome to the Face Verification Pipeline Desktop Utility." |
| `0:05 - 0:12` | Click **Select Folder** or **Replace** image | "We load a target portrait photo. The app updates image dimensions, file size, and parameters." |
| `0:12 - 0:22` | Adjust threshold slider & click **Run Verification** | "Adjust confidence threshold and click Run Verification to trigger InsightFace AI face detection." |
| `0:22 - 0:32` | Watch live logs & reverse search | "The app uploads to Catbox and queries SerpAPI Google Lens for matching social profiles." |
| `0:32 - 0:40` | View identity match & SHA-256 hash | "A match is confirmed with 96.4% confidence and the payload SHA-256 hash is recorded on Sepolia." |
| `0:40 - 0:45` | Click **Copy** hash & view contract link | "Verification complete! Click Copy Hash to verify proof directly on Etherscan." |

---

## 🛡️ Core Technologies & Specifications

- **PyQt5 Desktop Framework**: Native desktop interface with responsive sidebar and custom Qt stylesheets.
- **InsightFace (`buffalo_l`)**: Deep learning facial recognition engine running locally on CPU/GPU.
- **SerpAPI & Catbox.moe**: Structured reverse image lookup API with public image hosting bridge.
- **Web3.py & Sepolia Testnet**: Real-time Ethereum EIP-1559 transaction broadcasting and verification.
