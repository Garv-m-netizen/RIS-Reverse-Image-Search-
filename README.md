#  Face Verification Pipeline (AI & Ethereum Sepolia Blockchain)

A complete, production-grade desktop application built with **PyQt5** that takes a human face image, performs **AI face detection and 512-dim embedding extraction via InsightFace (`buffalo_l`)**, conducts a **reverse image web search via Bright Data API**, and registers an immutable, tamper-proof record on the **Ethereum Sepolia Testnet** using a custom Solidity smart contract (`HashRegistry.sol`).

---

##  Project Architecture

```
[ User Input Image (JPG/PNG) ]
             │
             ▼
[ 1. InsightFace AI (buffalo_l) ]  ➜ Extract face box & 512-dim embedding vector
             │
             ▼
[ 2. Bright Data Reverse Search ]  ➜ Query web for matching social media post (X, IG, LinkedIn)
             │
             ▼
[ 3. SHA-256 Hashing ]             ➜ Compute SHA-256 hash of (URL + Title + Snippet)
             │
             ▼
[ 4. Ethereum Sepolia Blockchain ]  ➜ Submit `storeHash(bytes32)` transaction to HashRegistry contract
             │
             ▼
[ 5. PyQt5 Desktop GUI ]            ➜ Display status logs, progress bar, & Etherscan proof link
```

---

##  Repository Structure

```
face-verification-pipeline/
├── main.py              # PyQt5 GUI Application entry point
├── pipeline.py          # Asynchronous QThread pipeline (InsightFace + Bright Data + Web3)
├── blockchain.py        # Web3.py smart contract interaction & transaction signing
├── config.py            # Environment configuration management & diagnostics
├── hash_registry.sol    # Solidity smart contract for Sepolia testnet
├── contract_abi.json    # Compiled smart contract ABI
├── requirements.txt     # Python package dependencies
├── .env.example         # Template for required environment variables
└── README.md            # Complete project documentation & setup guide
```

---

##  STEP-BY-STEP GUIDE: How to Get All Required APIs & Credentials for Real Test Execution

To execute live web searches and produce real Ethereum Sepolia transactions visible on Etherscan, follow these 4 straightforward steps:

### STEP 1: Get Bright Data API Token
1. Go to [Bright Data Signup / Control Panel](https://brightdata.com/).
2. Sign in or create a free account (includes free starter credits).
3. Navigate to **Account Settings** -> **API Tokens** (or **Data Collector API**).
4. Click **Generate Token** and copy your API Token.
5. In your `.env` file, set:
   ```env
   BRIGHT_DATA_API_TOKEN=your_copied_bright_data_token
   ```

---

### STEP 2: Get Sepolia RPC URL (Infura or Alchemy)
1. Go to [Infura.io](https://infura.io/) (or [Alchemy.com](https://alchemy.com/)).
2. Create a free account and click **Create New Key** / **Create App**.
3. Select **Ethereum** network and choose **Sepolia Testnet**.
4. Copy the **HTTPS Endpoint URL** (e.g. `https://sepolia.infura.io/v3/YOUR_PROJECT_ID`).
5. In your `.env` file, set:
   ```env
   SEPOLIA_PROVIDER_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
   ```

---

### STEP 3: Create a Sepolia Wallet & Get Free Testnet ETH
1. Install [MetaMask Browser Extension](https://metamask.io/).
2. Create or select a dedicated **Testnet Wallet**.
3. In MetaMask settings, enable **Show test networks** and select **Sepolia**.
4. Copy your Public Wallet Address (e.g., `0x1234...5678`).
5. Get free Sepolia Testnet ETH from any of these faucets:
   - [Google Cloud Sepolia Faucet](https://cloud.google.com/application/button/faucet/ethereum/sepolia)
   - [Alchemy Sepolia Faucet](https://sepoliapowfaucet.com/)
   - [Chainlink Sepolia Faucet](https://faucets.chain.link/sepolia)
6. Export your Private Key from MetaMask (*Account Details -> Show Private Key*).
7. In your `.env` file, set:
   ```env
   WALLET_ADDRESS=0xYourPublicWalletAddress
   WALLET_PRIVATE_KEY=0xYourPrivateKey
   ```

---

### STEP 4: Deploy `hash_registry.sol` to Sepolia Testnet
1. Open [Remix Ethereum IDE](https://remix.ethereum.org/).
2. Create a new file named `HashRegistry.sol` and paste the contents from `hash_registry.sol` in this repository.
3. On the left tab, select **Solidity Compiler**, choose version `0.8.20` or higher, and click **Compile HashRegistry.sol**.
4. On the left tab, select **Deploy & Run Transactions**:
   - Change **Environment** to **Injected Provider - MetaMask**.
   - Ensure MetaMask is connected to the **Sepolia Testnet**.
   - Click **Deploy** and confirm the transaction in MetaMask.
5. Once deployed, copy the **Contract Address** under *Deployed Contracts* (e.g., `0x9876...4321`).
6. In your `.env` file, set:
   ```env
   CONTRACT_ADDRESS=0xYourDeployedContractAddress
   ```

---

##  Installation & Running the Application

### 1. Clone & Setup Virtual Environment
```bash
git clone https://github.com/your-username/face-verification-pipeline.git
cd face-verification-pipeline

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

### 3. Create `.env` File
Copy `.env.example` to `.env` and fill in your keys obtained from the guide above:
```bash
cp .env.example .env
```

### 4. Launch Desktop GUI Application
```bash
python main.py
```

---

##  Screen Recording Presentation Script (45 Seconds)

| Timestamp | Screen Action | Voiceover / Description |
|---|---|---|
| `0:00 - 0:05` | Open `python main.py` | "Welcome to the Face Verification Pipeline desktop application." |
| `0:05 - 0:10` | Drag & drop face photo into upload zone | "We drag and drop a face photo. The app previews the photo and enables the pipeline." |
| `0:10 - 0:18` | Click **START PIPELINE** | "Clicking Start Pipeline runs InsightFace AI to detect and generate a 512-dim embedding." |
| `0:18 - 0:28` | Live log shows Bright Data search | "Bright Data API triggers reverse image search and locates the matching social media post." |
| `0:28 - 0:38` | Live log shows Sepolia transaction | "The post metadata is SHA-256 hashed and broadcasted to our HashRegistry smart contract on Sepolia." |
| `0:38 - 0:45` | Click **View on Etherscan** | "Verification is complete! Clicking 'View on Etherscan' verifies the immutable record on-chain." |

---

## 🛡️ Technical Rationale & Specifications

- **InsightFace (`buffalo_l`)**: Industry standard 512-dimensional facial feature extraction running offline.
- **Bright Data Reverse Image API**: Reliable reverse search endpoint avoiding CAPTCHAs with fast JSON responses.
- **Web3.py & Sepolia Testnet**: Real smart contract storage on an Ethereum testnet with public Etherscan links.
- **PyQt5 GUI**: Threaded execution prevents UI freezes, featuring Catppuccin dark theme styling (#1e1e2e).
