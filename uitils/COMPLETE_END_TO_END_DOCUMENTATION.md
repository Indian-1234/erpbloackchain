# EHR BLOCKCHAIN - COMPLETE END-TO-END DOCUMENTATION

## TABLE OF CONTENTS
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Software Requirements & Details](#software-requirements--details)
4. [Complete Installation Steps](#complete-installation-steps)
5. [Configuration Details](#configuration-details)
6. [Running the Application](#running-the-application)
7. [Project Structure](#project-structure)
8. [File Descriptions](#file-descriptions)
9. [User Workflows](#user-workflows)
10. [Testing Guide](#testing-guide)
11. [Troubleshooting](#troubleshooting)
12. [Security](#security)
13. [Production Deployment](#production-deployment)

---

## SYSTEM OVERVIEW

### What is EHR Blockchain?

**EHR Blockchain** is a decentralized Electronic Health Records (EHR) management system built on Ethereum Blockchain. It allows:

- **Patients** to securely store and manage their medical records
- **Doctors/Auditors** to access only authorized patient records
- **Immutable record keeping** - all changes are permanently recorded on blockchain
- **Encrypted data storage** - sensitive information is encrypted before storage
- **Role-based access** - patients control who can view their records

### Key Objectives

1. **Privacy**: Patients maintain control. Unauthorized access is prevented through smart contracts.
2. **Identification & Authorization**: All users authenticate with encrypted credentials and hashed passwords.
3. **Queries**: Authorized entities query patient records with full transaction history.
4. **Immutability**: Once recorded on blockchain, medical records cannot be modified undetected.
5. **Decentralization**: Uses smart contracts and Ethereum blockchain - no single point of control.

### Technology Stack

```
Frontend Layer
    ↓
    HTML/CSS/Bootstrap (Web Pages)
    ├── index.html (Home)
    ├── login.html (Authentication)
    ├── patient.html (Patient Actions)
    └── audit.html (Auditor Actions)
    ↓
Web Framework Layer
    ↓
    Flask (Python Web Framework)
    ├── main.py (Route Handlers)
    ├── model.py (Forms & Data Models)
    └── Web UI Logic
    ↓
Business Logic Layer
    ↓
    Security & Encryption
    ├── Cryptography (Fernet)
    ├── Hashlib (SHA256)
    └── PyOpenSSL (SSL/TLS)
    ↓
Blockchain Connection Layer
    ↓
    Web3.py (Blockchain Interface)
    ├── Connects to Ganache
    ├── Calls Smart Contract Functions
    └── Manages Transactions
    ↓
Blockchain Layer
    ↓
    Ganache (Local Blockchain)
    ├── Port 7545
    ├── 10 Pre-funded Accounts
    └── Transaction Explorer
    ↓
Smart Contract Layer
    ↓
    Solidity Contracts (Compiled by Truffle)
    ├── Migrations.sol
    └── Patient.sol (Main Contract)
    ↓
Truffle Development Environment
    ├── Compiles Solidity Code
    ├── Manages Migrations
    └── Deploys to Ganache
```

---

## ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────┐
│                    PATIENT/AUDITOR                       │
│              (Web Browser - localhost:5000)              │
└────────────────────────┬────────────────────────────────┘
                         │
                         ↓
          ┌──────────────────────────────┐
          │   FLASK WEB APPLICATION      │
          │  (main.py - Port 5000)       │
          │  ┌──────────────────────┐    │
          │  │ Route Handlers       │    │
          │  ├── /                  │    │
          │  ├── /login             │    │
          │  ├── /signup            │    │
          │  ├── /patient           │    │
          │  ├── /audit             │    │
          │  └── /records           │    │
          │  ┌──────────────────────┐    │
          │  │ Security Layer       │    │
          │  ├── Fernet Encryption  │    │
          │  ├── SHA256 Hashing     │    │
          │  └── Password Validation│    │
          │  ┌──────────────────────┐    │
          │  │ Data Storage         │    │
          │  ├── data/signin_data   │    │
          │  └── data/uniqueid_data │    │
          └──────────────┬──────────────┘
                         │
        ┌────────────────┴────────────────┐
        ↓                                 ↓
  ┌──────────────┐              ┌──────────────────┐
  │ WEB3.PY      │              │ PANDAS / JSON    │
  │ Blockchain   │              │ Data Processing  │
  │ Interface    │              └──────────────────┘
  └──────────────┤
                 │
        ┌────────┴──────────┐
        ↓                   ↓
   ┌─────────────┐   ┌─────────────┐
   │ GANACHE GUI │   │ ABI.JSON    │
   │ Port 7545   │   │ BYTECODE    │
   │ (Blockchain)│   │ (Contract   │
   └─────────────┤   │  Metadata)  │
                 │   └─────────────┘
        ┌────────┴──────────┐
        ↓                   ↓
   ┌──────────────────────────────┐
   │  SMART CONTRACTS (Ethereum)  │
   │  ┌────────────────────────┐  │
   │  │ Migrations.sol         │  │
   │  │ - Tracks deployments   │  │
   │  └────────────────────────┘  │
   │  ┌────────────────────────┐  │
   │  │ Patient.sol            │  │
   │  │ - Patient records      │  │
   │  │ - Medical data         │  │
   │  │ - Access control       │  │
   │  │ - Audit logs           │  │
   │  └────────────────────────┘  │
   └──────────────────────────────┘
        ↑
        │ Compiled & Deployed by
        │
   ┌──────────────────────────────┐
   │   TRUFFLE FRAMEWORK          │
   │   ├── truffle-config.js      │
   │   ├── migrations/            │
   │   │   ├── 1_initial_*.js     │
   │   │   └── 2_deploy_*.js      │
   │   └── build/contracts/       │
   │       ├── Migrations.json    │
   │       └── Patient.json       │
   └──────────────────────────────┘
```

---

## SOFTWARE REQUIREMENTS & DETAILS

### 1. OPERATING SYSTEM
- **macOS** (10.12+)
- **Windows** (10 or later)
- **Linux** (Ubuntu 18.04+)

---

### 2. NODEJS & NPM (For Blockchain Tools)

**Purpose**: Manages JavaScript packages for Truffle and Solidity compiler

**Download**: https://nodejs.org/ (LTS version recommended)

**Version**: Node.js 14+ and npm 6+

**Required for**:
- Truffle framework
- Solidity compiler (solc)
- Smart contract compilation and deployment

**Installation Check**:
```bash
node --version    # Should show v14.x.x or higher
npm --version     # Should show 6.x.x or higher
```

---

### 3. PYTHON 3

**Purpose**: Backend application runtime

**Download**: https://www.python.org/downloads/

**Version**: Python 3.8 or higher

**Required for**:
- Flask web server
- Web3.py blockchain connection
- Cryptography and encryption
- Data processing and CSV handling

**Installation Check**:
```bash
python3 --version    # Should show Python 3.8.x or higher
```

---

### 4. GANACHE GUI

**Purpose**: Local Ethereum blockchain simulator

**Download**: https://www.trufflesuite.com/ganache

**What it provides**:
- 10 pre-funded Ethereum accounts with 100 ETH each
- Transaction explorer and block viewer
- Real-time blockchain state
- Port 7545 (RPC Server)

**Key Features**:
- Instant mining of transactions
- Account management
- Transaction history
- Block details and logs

**System Requirements**:
- RAM: 4GB minimum
- Disk Space: 500MB

---

### 5. GIT (Optional but Recommended)

**Purpose**: Version control for code

**Download**: https://git-scm.com/

**Used for**:
- Cloning repository
- Version tracking
- Collaboration

---

## PYTHON DEPENDENCIES

### Core Web Framework
- **flask** (2.0+) - Web framework
- **flask_bootstrap** - Bootstrap CSS integration
- **flask_wtf** - CSRF protection
- **wtforms** - Form validation

### Blockchain Connection
- **web3** (5.0+) - Ethereum blockchain interface
- **requests** - HTTP requests for Ganache connection

### Security & Cryptography
- **cryptography** (3.4+) - Fernet encryption
- **pyopenssl** (20.0+) - SSL/TLS certificates
- **hashlib** (built-in) - Password hashing

### Data Processing
- **pandas** (1.0+) - CSV file handling
- **json** (built-in) - Data serialization

### Utilities
- **clipboard** - Copy to clipboard
- **dateutil** - Date/time conversion
- **datetime** (built-in) - Timestamp handling

---

## NPM DEPENDENCIES

```json
{
  "dependencies": {
    "solc": "^0.6.6"  // Solidity compiler
  },
  "devDependencies": {
    "truffle": "^5.11.5"  // Blockchain framework
  }
}
```

---

## COMPLETE INSTALLATION STEPS

### STEP 1: Install Node.js & npm

**On macOS (using Homebrew)**:
```bash
brew install node
```

**On Windows**:
- Download from https://nodejs.org/
- Run installer and follow steps
- Restart terminal/command prompt

**On Linux (Ubuntu)**:
```bash
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Verify Installation**:
```bash
node --version
npm --version
```

---

### STEP 2: Install Python 3

**On macOS (using Homebrew)**:
```bash
brew install python3
```

**On Windows**:
- Download from https://www.python.org/downloads/
- During installation: ✓ Check "Add Python to PATH"
- Run installer

**On Linux (Ubuntu)**:
```bash
sudo apt-get update
sudo apt-get install python3 python3-venv python3-pip
```

**Verify Installation**:
```bash
python3 --version
pip3 --version
```

---

### STEP 3: Download & Install Ganache GUI

**Download** from: https://www.trufflesuite.com/ganache

**Installation**:
- **macOS**: Drag to Applications folder
- **Windows**: Run .exe installer
- **Linux**: Extract .AppImage and make executable

**Launch Ganache**:
- Open Applications → Ganache (macOS)
- Double-click ganache.exe (Windows)
- Run extracted file (Linux)

**Verify Ganache**:
1. Opens on localhost:7545
2. Shows 10 accounts with 100 ETH
3. Shows "RPC Server" in top bar

---

### STEP 4: Clone/Download Project

```bash
# Option A: Clone from GitHub (if available)
git clone https://github.com/username/EHRBlockchain.git
cd EHRBlockchain

# Option B: Extract from ZIP
unzip EHRBlockchain.zip
cd EHRBlockchain
```

---

### STEP 5: Install Node Dependencies

```bash
# Navigate to project folder
cd EHRBlockchain

# Install Truffle globally
npm install truffle -g

# Install project-specific npm packages
npm install
```

**What this installs**:
- Truffle 5.11.5
- Solidity compiler (solc) 0.6.6

**Verification**:
```bash
truffle --version    # Should show Truffle v5.x.x
```

---

### STEP 6: Create Python Virtual Environment

**Purpose**: Isolate project dependencies from system Python

**On macOS/Linux**:
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) at the start of terminal line
```

**On Windows**:
```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# You should see (venv) at the start of command line
```

---

### STEP 7: Install Python Dependencies

**Make sure virtual environment is activated** (you should see `(venv)`)

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install \
    flask==2.3.0 \
    flask_bootstrap==3.3.7.1 \
    flask_wtf==1.1.1 \
    wtforms==3.0.1 \
    web3==5.31.3 \
    pandas==1.5.3 \
    cryptography==41.0.0 \
    pyopenssl==23.2.0 \
    requests==2.31.0 \
    clipboard==0.0.4 \
    python-dateutil==2.8.2
```

**Or install from requirements file (if available)**:
```bash
pip install -r requirements.txt
```

**Verify Installation**:
```bash
pip list    # Should show all packages installed
```

---

### STEP 8: Generate Encryption Key

**Purpose**: Create the Fernet key for data encryption

```bash
# Open Python interpreter
python3

# Type these commands:
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())

# You'll see output like: b'b_Jd1LkZ...'
# Copy the entire string (without b' and ')

# Exit Python
exit()
```

**Save the Key**:

**On macOS/Linux**:
```bash
echo "your_key_here" > data/enc_key.key
```

**On Windows**:
```bash
echo your_key_here > data\enc_key.key
```

Or manually:
1. Create file: `data/enc_key.key`
2. Paste the key string
3. Save file

**Verify**:
```bash
cat data/enc_key.key    # macOS/Linux
type data\enc_key.key   # Windows
```

---

### STEP 9: Create .gitignore File

**Purpose**: Prevent sensitive files from being committed

Create file: `.gitignore`

```
# Virtual Environment
venv/
env/
ENV/

# Encryption Key
data/enc_key.key

# Environment Variables
.env
.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Flask
instance/
.webassets-cache

# Compiled Contracts
build/

# Node Modules
node_modules/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

---

### STEP 10: Verify All Installations

```bash
# Check Node.js
node --version

# Check npm
npm --version

# Check Python
python3 --version

# Check Truffle
truffle --version

# Check Python virtual environment is activated
which python    # macOS/Linux
where python    # Windows
# Should show path inside venv folder

# Check Flask
python3 -c "import flask; print(flask.__version__)"

# Check Web3.py
python3 -c "import web3; print(web3.__version__)"
```

**All checks should pass ✓**

---

## CONFIGURATION DETAILS

### truffle-config.js

```javascript
module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",      // Ganache host
      port: 7545,             // Ganache port
      network_id: "*"         // Any network ID
    }
  },
  compilers: {
    solc: {
      version: "0.6.6",       // Solidity version
      settings: {
        optimizer: {
          enabled: false,
          runs: 200
        },
        evmVersion: "byzantium"
      }
    }
  }
};
```

**Configuration Explanation**:
- `host: "127.0.0.1"` - Local machine
- `port: 7545` - Ganache default port
- `solc: "0.6.6"` - Solidity compiler version

---

### Ganache Configuration

**When you open Ganache GUI**:

1. Click **"New Workspace"** or **"Quick Start"**
2. Default Settings (leave as-is):
   - **RPC Server**: http://127.0.0.1:7545
   - **Network ID**: 5777
   - **Accounts**: 10 pre-funded
   - **Balance**: 100 ETH each
   - **Mining**: Instamined (instant)

3. Important Settings (if needed):
   - Go to Settings → Server
   - Verify Port: 7545
   - Hostname: 127.0.0.1

---

### main.py Configuration

```python
# Ganache connection
ganache_url = "http://127.0.0.1:7545"

# Flask secret key (change in production)
app.config.from_mapping(
    SECRET_KEY=b'\xd6\x04\xbdj\xfe\xed$c\x1e@\xad\x0f\x13,@G'
)

# Connection retry settings
retry_strategy = Retry(
    total=3,                    # Retry 3 times
    backoff_factor=0.3,        # Wait 0.3, 0.6, 0.9 seconds
    status_forcelist=[429, 500, 502, 503, 504]
)
```

---

### Encryption Configuration

**Fernet Key Location**: `data/enc_key.key`

**How it's Used**:
```python
from cryptography.fernet import Fernet

# Load key from file
with open('data/enc_key.key', 'rb') as key_file:
    key = key_file.read()

# Create cipher
cipher = Fernet(key)

# Encrypt data
encrypted = cipher.encrypt(b"patient data")

# Decrypt data
decrypted = cipher.decrypt(encrypted)
```

---

## RUNNING THE APPLICATION

### COMPLETE STARTUP PROCEDURE

**You need 3 terminals running simultaneously:**

---

### TERMINAL 1: Start Ganache Blockchain

**Step 1**: Open Ganache GUI application
- macOS: Applications → Ganache
- Windows: Double-click ganache.exe
- Linux: Run extracted AppImage

**Step 2**: Click **"New Workspace"** or **"Quick Start"**

**Step 3**: Verify RPC Server shows `http://127.0.0.1:7545`

**Step 4**: Keep this window open (don't close)

**What you should see**:
```
RPC Server: http://127.0.0.1:7545
Network ID: 5777
Gas Limit: 6721975
Gas Price: 2 Gwei
10 Accounts (with 100 ETH each)
```

---

### TERMINAL 2: Compile & Deploy Smart Contracts

**Step 1**: Open new terminal/command prompt

**Step 2**: Navigate to project folder
```bash
cd EHRBlockchain
```

**Step 3**: Make sure you're in the project root (where package.json is)
```bash
ls          # macOS/Linux - should see truffle-config.js
dir         # Windows - should see truffle-config.js
```

**Step 4**: Compile Solidity contracts
```bash
truffle compile
```

**Expected Output**:
```
Compiling your contracts...
✓ Compiled successfully using:
   - solc: 0.6.6
```

**What was created**:
- `build/contracts/Migrations.json`
- `build/contracts/Patient.json`

**Step 5**: Deploy contracts to Ganache
```bash
truffle migrate
```

**Expected Output**:
```
Starting migrations...
> Network name:    'development'
> Network id:      5777
> Block gas limit: 6721975

1_initial_migration.js
=====================
   Deploying 'Migrations'
   > transaction hash:    0x...
   > Blocks: 1            Seconds: 0
   > contract address:    0x...
   > account:             0x...

2_deploy_contract.js
====================
   Deploying 'Patient'
   > transaction hash:    0x...
   > Blocks: 1            Seconds: 1
   > contract address:    0x...
   > account:             0x...

   Deployments summary
   ====================
   > Total deployments:   2
   > Final cost:          0.00... ETH

```

**What Happened**:
- Truffle compiled `.sol` to bytecode
- Deployed Migrations contract
- Deployed Patient contract
- Both are now on Ganache blockchain

**Note**: Keep this terminal open for reference. You only run these commands once (or when updating contracts).

---

### TERMINAL 3: Start Flask Web Application

**Step 1**: Open ANOTHER new terminal/command prompt

**Step 2**: Navigate to project folder
```bash
cd EHRBlockchain
```

**Step 3**: Activate Python virtual environment

**On macOS/Linux**:
```bash
source venv/bin/activate
```

**On Windows**:
```bash
venv\Scripts\activate
```

**Verify**: You should see `(venv)` at the start of your terminal line

**Step 4**: Set Flask environment variables

**On macOS/Linux**:
```bash
export FLASK_APP=main.py
export FLASK_ENV=development
```

**On Windows**:
```bash
set FLASK_APP=main.py
set FLASK_ENV=development
```

**Step 5**: Start Flask server
```bash
flask run
```

**Expected Output**:
```
 * Serving Flask app 'main' (lazy loading)
 * Environment: development
 * Debug mode: on
 * WARNING in use the development server in a production environment.
 * Use a production WSGI server instead.
 * Restarting with reloader
 * Debugger is active!
 * Debugger PIN: 123-456-789
 * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
```

**Step 6**: Keep this terminal running

---

### OPEN APPLICATION IN BROWSER

**Step 1**: Open web browser (Chrome, Firefox, Safari)

**Step 2**: Go to:
```
http://127.0.0.1:5000
```

**Step 3**: You should see the EHR Blockchain home page

**Success Indicators**:
- ✓ Page loads without errors
- ✓ Two buttons: "Patient Login" and "Auditor Login"
- ✓ Bootstrap CSS styling is applied
- ✓ Links to signup pages work

---

### TERMINAL STATUS SUMMARY

| Terminal | Running | Command | Keep Open |
|----------|---------|---------|-----------|
| 1 | Ganache GUI | Application | YES |
| 2 | Truffle | `truffle compile && migrate` | NO* |
| 3 | Flask | `flask run` | YES |

*Terminal 2 only needs to stay open if you're watching for errors. After successful deployment, you can close it.

---

## PROJECT STRUCTURE

```
EHRBlockchain/
│
├── Root Files
│   ├── main.py                    # Flask app & blockchain connection
│   ├── model.py                   # Forms & data models
│   ├── abi.json                   # Contract ABI (interface)
│   ├── bytecode.json              # Contract bytecode
│   ├── package.json               # Node.js dependencies
│   ├── truffle-config.js          # Truffle configuration
│   ├── README.md                  # Project readme
│   └── LICENSE                    # License file
│
├── contracts/                     # Smart Contracts (Solidity)
│   ├── Migrations.sol             # Migration tracking contract
│   └── Patient.sol                # Main EHR contract
│
├── migrations/                    # Truffle migrations
│   ├── 1_initial_migration.js     # Initial migration
│   └── 2_deploy_contract.js       # Deploy Patient contract
│
├── build/                         # Compiled contracts (auto-generated)
│   └── contracts/
│       ├── Migrations.json        # Compiled Migrations
│       └── Patient.json           # Compiled Patient contract
│
├── templates/                     # HTML templates
│   ├── index.html                 # Home page
│   ├── login.html                 # Login page
│   ├── patient.html               # Patient dashboard
│   ├── patientreg.html            # Patient registration
│   ├── audit.html                 # Auditor dashboard
│   ├── auditreg.html              # Auditor registration
│   └── result.html                # Result page
│
├── static/                        # Static assets
│   ├── css/                       # Bootstrap CSS
│   │   ├── bootstrap.css
│   │   ├── bootstrap.min.css
│   │   ├── bootstrap-grid.css
│   │   └── bootstrap-reboot.css
│   └── img/                       # Images
│       └── index.png
│
├── data/                          # Data files
│   ├── enc_key.key                # Encryption key (SECRET!)
│   ├── 3f91fb273e0cc...csv        # Hashed signin_data
│   └── f415ea3131a...csv          # Hashed uniqueid_data
│
├── test/                          # Test files (empty)
│
├── node_modules/                  # Node packages (auto-generated)
│   ├── truffle/
│   └── solc/
│
└── venv/                          # Python virtual environment (auto-generated)
    ├── bin/
    ├── lib/
    └── pyvenv.cfg
```

---

## FILE DESCRIPTIONS

### CORE APPLICATION FILES

#### main.py (Flask Application)
```
Purpose: Main web application and blockchain interface
Size: ~1000+ lines
Contains:
  - Flask route handlers (@app.route)
  - Blockchain connection logic (Web3.py)
  - User authentication (login, signup)
  - Encryption/decryption functions
  - Medical record management
  - CSV data handling
  - Ganache connection with retry logic

Key Functions:
  - check_blockchain_connection() - Verify Ganache is running
  - encrypt_data() - Encrypt sensitive information
  - decrypt_data() - Decrypt stored information
  - hash_password() - Hash passwords with salt
```

#### model.py (Data Models & Forms)
```
Purpose: WTForms form classes for validation
Size: ~200+ lines
Contains:
  - AuditRegForm - Auditor registration form
  - PatientRegForm - Patient registration form
  - LogForm - Login form
  - Form validators (email, password, length)
  - Field definitions with error messages
  - Placeholder text for UI

Validation Rules:
  - Account number: 0-9
  - Name: Required string
  - Email: Valid email format
  - Password: Min 6 characters, must match confirm
  - Phone: Min 10 digits
```

---

### SMART CONTRACT FILES

#### contracts/Patient.sol (Main Smart Contract)
```
Purpose: Ethereum smart contract for patient records
Language: Solidity v0.6.6
Contains:
  - Patient struct with personal info
  - Medical record struct with timestamps
  - Functions for record creation
  - Access control logic
  - Audit trail functionality
  - Patient and doctor interactions

Key Variables:
  - firstName, lastName (encrypted)
  - email, phone, zip, city (encrypted)
  - medical_record[] (array of records)
  - address patient_address (Ethereum address)
  - uint256 record_id (unique record ID)

Key Functions:
  - createPatient() - Register new patient
  - addRecord() - Add medical record
  - grantAccess() - Allow auditor to view records
  - revokeAccess() - Deny auditor access
  - queryRecords() - Retrieve patient records
```

#### contracts/Migrations.sol
```
Purpose: Track which migrations have been deployed
Auto-generated by Truffle framework
Used for: Ensuring migrations run in correct order
```

---

### CONFIGURATION FILES

#### truffle-config.js
```
Purpose: Truffle framework configuration
Contains:
  - Network settings (development)
  - Ganache connection (127.0.0.1:7545)
  - Solidity compiler version (0.6.6)
  - Compilation settings
  - Mocha testing settings

Key Settings:
  - host: "127.0.0.1" (local machine)
  - port: 7545 (Ganache port)
  - network_id: "*" (any network)
  - solc version: "0.6.6"
```

#### package.json
```
Purpose: Node.js project configuration
Contains:
  - Truffle 5.11.5 (devDependency)
  - Solc 0.6.6 (dependency)
  - Project metadata
  - npm script commands

Why these versions:
  - Truffle 5.11.5: Stable, well-tested
  - Solc 0.6.6: Matches contract pragma
```

#### abi.json
```
Purpose: Application Binary Interface (contract interface)
Auto-generated by truffle compile
Contains:
  - Function signatures
  - Input/output types
  - Gas requirements
  - Event definitions

Used by: Web3.py to call smart contract functions
```

#### bytecode.json
```
Purpose: Compiled contract bytecode
Auto-generated by truffle compile
Contains:
  - EVM bytecode (machine code)
  - Compiled contract binary
  - Deployment code

Used by: Deploying contracts to blockchain
```

---

### TEMPLATE FILES (HTML/Jinja2)

#### templates/index.html
```
Purpose: Home page
Contains:
  - Project title and description
  - Login buttons (Patient & Auditor)
  - Signup buttons (Patient & Auditor)
  - Bootstrap responsive layout
```

#### templates/login.html
```
Purpose: Login page for both roles
Contains:
  - Email input field
  - Password input field
  - Role selection dropdown
  - Login button
  - Form validation
```

#### templates/patientreg.html
```
Purpose: Patient registration form
Fields:
  - Account number (0-9)
  - First name
  - Last name
  - Email
  - Phone number
  - City
  - Zip code
  - Insurance number
  - Password (with confirmation)

Data Flow: HTML → main.py → Encrypt → CSV → Blockchain
```

#### templates/patient.html
```
Purpose: Patient dashboard
Features:
  - View personal records
  - Add new medical record
  - Grant access to auditors
  - Revoke auditor access
  - View audit trail
```

#### templates/auditreg.html
```
Purpose: Auditor/Doctor registration
Fields:
  - Account number (0-9)
  - First name, Last name
  - Email
  - Employee ID
  - Password (with confirmation)

Role: Can only view records patients authorized
```

#### templates/audit.html
```
Purpose: Auditor dashboard
Features:
  - View authorized patient records
  - Search for patients
  - View audit timestamps
  - Download records (if enabled)
```

#### templates/result.html
```
Purpose: Result page after login/action
Shows:
  - Success/error messages
  - Action details
  - Redirect links
```

---

### DATA STORAGE FILES

#### data/enc_key.key
```
Purpose: Fernet encryption key
Content: 44-character base64 string
Example: b'2Qr8V_qZ7D...'
Security: NEVER commit to GitHub
Usage: Encrypt/decrypt all sensitive data

Created by: Fernet.generate_key()
Location: data/ directory
Permissions: Read-only
```

#### data/signin_data.csv (Hashed filename)
```
Purpose: Store encrypted user credentials
Actual Filename: 3f91fb273e0cc5729c0e3c6379c3439c1369f987c29705146771707a.csv
Format: CSV with encrypted content
Columns:
  - email (encrypted)
  - password_hash (SHA256 + salt)
  - role (patient/auditor)
  - user_data (encrypted JSON)
```

#### data/uniqueid_data.csv (Hashed filename)
```
Purpose: Map unique IDs to patient records
Actual Filename: f415ea3131a706b7d59e47c93b748932660f10d747cfa34f5868d469.csv
Format: CSV with encrypted content
Columns:
  - unique_id (encrypted)
  - patient_id (encrypted)
  - blockchain_address (encrypted)
  - timestamp
```

---

### BUILD OUTPUTS (Auto-generated)

#### build/contracts/Migrations.json
```
Purpose: Compiled Migrations contract
Auto-generated by: truffle compile
Contains:
  - Contract ABI
  - Bytecode
  - Deployment info
  - Networks deployed to
```

#### build/contracts/Patient.json
```
Purpose: Compiled Patient contract
Auto-generated by: truffle compile
Contains:
  - Full Patient contract ABI
  - Complete bytecode
  - Source maps
  - Compiler settings
  - Networks deployed to

Used by: Web3.py to instantiate contract
```

---

### MIGRATIONS (Deployment Scripts)

#### migrations/1_initial_migration.js
```
Purpose: Deploy Migrations contract
Auto-generated by Truffle
Runs first during migration
```

#### migrations/2_deploy_contract.js
```javascript
var Patient = artifacts.require("Patient");

module.exports = function(deployer) {
    deployer.deploy(
        Patient,
        "a","a","a","a","a","a","a","a","a"  // 9 initial params
    );
};
```

Purpose: Deploy Patient contract to blockchain
Initial Parameters: 9 strings (default values)
Runs second during migration
Creates first Patient contract instance
```

---

## USER WORKFLOWS

### WORKFLOW 1: PATIENT REGISTRATION

```
1. User opens http://127.0.0.1:5000
2. Clicks "Patient Sign Up"
3. Fills form:
   - Account number (picks 0-9)
   - First name
   - Last name
   - Email
   - Phone
   - City
   - Zip code
   - Insurance number
   - Password (min 6 chars)
   - Confirm password
4. Clicks Submit
5. Backend processes:
   - Validates all fields
   - Hashes password with SHA256 + salt
   - Encrypts sensitive data with Fernet
   - Saves to CSV (signin_data)
   - Generates unique patient ID
   - Creates blockchain record via Patient.sol
   - Stores encrypted ID mapping
6. Patient redirected to login page
7. Receives success message

Data Flow:
User Input → Flask Route → Validation
    ↓
Encryption (Fernet) → CSV Storage
    ↓
Smart Contract Call (Web3.py)
    ↓
Ganache Blockchain Records
    ↓
Transaction Hash Generated
```

---

### WORKFLOW 2: PATIENT LOGIN

```
1. User opens login page
2. Selects role: "Patient"
3. Enters email
4. Enters password
5. Clicks Login
6. Backend processes:
   - Reads signin_data CSV
   - Decrypts with Fernet key
   - Finds matching email
   - Hashes entered password
   - Compares with stored hash
   - If match: Load patient records from blockchain
   - If no match: Show error
7. Successful login:
   - Creates session
   - Redirects to patient dashboard
   - Shows patient records
   - Shows audit access buttons

Security:
- Password never stored in plaintext
- Only hash comparison happens
- Session managed by Flask
- CSRF protection via flask_wtf
```

---

### WORKFLOW 3: ADD MEDICAL RECORD

```
1. Patient logged in on dashboard
2. Clicks "Add Medical Record"
3. Fills record form:
   - Record type (checkup, test, etc)
   - Description
   - Date
   - Additional notes
4. Clicks Add Record
5. Backend processes:
   - Validates input
   - Encrypts record data
   - Calls Patient.sol: addRecord()
   - Web3.py sends transaction to Ganache
   - Blockchain records:
     * record_id (unique)
     * patient_address (Ethereum address)
     * record_msg (encrypted)
     * timestamp (seconds since epoch)
     * record_status (0 = Created)
   - Transaction receipt returned
6. Patient sees:
   - "Record added successfully"
   - Transaction hash
   - Record appears in list

Immutability:
- Once on blockchain, cannot be deleted
- Only status changes are recorded
- All changes create new transactions
- Full audit trail maintained
```

---

### WORKFLOW 4: GRANT AUDITOR ACCESS

```
1. Patient logged in on dashboard
2. Clicks "Grant Access"
3. Enters auditor email: "doctor@hospital.com"
4. Clicks Grant
5. Backend processes:
   - Validates auditor exists
   - Calls Patient.sol: grantAccess()
   - Adds auditor's address to allowed list
   - Creates blockchain transaction
   - Records timestamp
   - Stores encrypted reference
6. Auditor can now view patient records
7. Patient sees confirmation
8. Auditor receives notification

Authorization:
- Only patient can grant/revoke
- Patient controls own data access
- All changes recorded on blockchain
- Cannot fake authorization (signed transaction)
```

---

### WORKFLOW 5: AUDITOR VIEW PATIENT RECORDS

```
1. Auditor logs in
2. Searches for patient by email
3. Clicks "View Records"
4. Backend processes:
   - Checks if auditor authorized
   - Calls Patient.sol: queryRecords()
   - Smart contract verifies access
   - If authorized: Returns records
   - If not authorized: Returns error
5. Auditor sees:
   - Patient name
   - Medical history
   - All records with timestamps
   - Who added each record
   - Any modifications made
6. Cannot modify records
   - Only view permission
   - Read-only access

Audit Trail:
- See who accessed records
- When access was granted
- All record modifications
- Immutable history
```

---

## TESTING GUIDE

### PRE-TEST CHECKLIST

- [ ] Ganache GUI is open and running
- [ ] Port 7545 visible in Ganache
- [ ] `truffle compile && truffle migrate` completed
- [ ] Flask server running (`flask run`)
- [ ] Terminal shows "Running on http://127.0.0.1:5000"
- [ ] Can open http://127.0.0.1:5000 in browser

---

### TEST CASE 1: Landing Page

**Test**:
```
1. Open http://127.0.0.1:5000
2. Verify home page loads
3. Verify Bootstrap styling applied
4. Verify two main buttons:
   - Patient Login
   - Auditor Login
5. Verify sign-up links visible
```

**Expected Result**: ✓ Page loads, properly styled, all buttons clickable

---

### TEST CASE 2: Patient Registration

**Test**:
```
1. Click "Patient Sign Up"
2. Fill form:
   Account: 1
   First: John
   Last: Doe
   Email: john@hospital.com
   Phone: 5551234567
   City: Boston
   Zip: 02101
   Insurance: INS123456
   Password: SecurePass123
   Confirm: SecurePass123
3. Click Submit
```

**Expected Result**:
- ✓ Form validates
- ✓ Redirects to login page
- ✓ Success message shown
- ✓ Data saved to CSV (encrypted)
- ✓ Blockchain transaction confirmed

**Verification**:
- Check `data/3f91fb273e0cc...csv` file (should contain encrypted data)
- Check Ganache → Transactions tab (should show new transaction)

---

### TEST CASE 3: Patient Login

**Test**:
```
1. On login page
2. Select role: "Patient"
3. Enter email: john@hospital.com
4. Enter password: SecurePass123
5. Click Login
```

**Expected Result**:
- ✓ Validates credentials
- ✓ Session created
- ✓ Redirects to patient dashboard
- ✓ Shows patient name
- ✓ Shows empty records list

---

### TEST CASE 4: Add Medical Record

**Test**:
```
1. Logged in as patient
2. Click "Add Medical Record"
3. Fill:
   Type: Annual Checkup
   Description: Normal blood pressure, no issues
   Date: 2024-01-15
4. Click Add
```

**Expected Result**:
- ✓ Record added successfully
- ✓ Transaction hash shown
- ✓ Record appears in list
- ✓ Timestamp visible
- ✓ Blockchain transaction in Ganache

**Verify in Ganache**:
1. Open Ganache
2. Click "Transactions"
3. See new transaction with:
   - To: Patient contract address
   - From: Account used for patient
   - Input: Encoded record data

---

### TEST CASE 5: Auditor Registration

**Test**:
```
1. Click "Auditor Sign Up"
2. Fill:
   Account: 2
   First: Dr. Smith
   Last: Smith
   Email: dr.smith@hospital.com
   Employee ID: EMP123
   Password: DocPass456
   Confirm: DocPass456
3. Click Submit
```

**Expected Result**:
- ✓ Form validates
- ✓ Redirects to login
- ✓ Data saved to CSV (encrypted)

---

### TEST CASE 6: Grant Auditor Access

**Test**:
```
1. Login as patient (john@hospital.com)
2. Click "Grant Access"
3. Enter auditor email: dr.smith@hospital.com
4. Click Grant
```

**Expected Result**:
- ✓ Access granted
- ✓ Blockchain transaction created
- ✓ Auditor can now view records
- ✓ Confirmation message shown

---

### TEST CASE 7: Auditor View Records

**Test**:
```
1. Logout (or new browser)
2. Login as auditor
3. Role: "Auditor"
4. Email: dr.smith@hospital.com
5. Password: DocPass456
6. Click "View Records"
7. Search for patient email: john@hospital.com
```

**Expected Result**:
- ✓ Patient's records visible
- ✓ Medical record "Annual Checkup" shown
- ✓ Timestamp visible
- ✓ Read-only (cannot edit)

---

### TEST CASE 8: Revoke Auditor Access

**Test**:
```
1. Login as patient
2. Click "Revoke Access"
3. Select auditor: Dr. Smith
4. Click Revoke
```

**Expected Result**:
- ✓ Access revoked
- ✓ Blockchain transaction created
- ✓ Auditor can no longer view records
- ✓ Error message if auditor tries to access

---

### TEST CASE 9: Blockchain Immutability

**Test**:
```
1. Add patient record
2. Try to modify database CSV directly
3. Access blockchain record again
4. Try to call smart contract to modify record
```

**Expected Result**:
- ✓ Direct CSV edit doesn't affect blockchain
- ✓ Original record still visible
- ✓ Smart contract prevents unauthorized modification
- ✓ Audit shows attempted modification

---

### TEST CASE 10: Encryption Verification

**Test**:
```
1. Open data/3f91fb273e0cc...csv
2. View raw content (should be encrypted)
3. Manually decrypt using Fernet key
4. Verify patient data matches entered info
```

**Expected Result**:
- ✓ CSV contains encrypted data (not readable)
- ✓ With key, can decrypt successfully
- ✓ Decrypted data matches original input
- ✓ No passwords stored in plaintext

---

### PERFORMANCE TEST

```
1. Add 10 patient records
2. Grant access to 5 auditors
3. Have auditors view records
4. Monitor response times
5. Check Ganache gas usage
```

**Expected Result**:
- ✓ Each operation completes in <5 seconds
- ✓ No memory leaks
- ✓ Gas usage stays reasonable (<3M per transaction)

---

## TROUBLESHOOTING

### ISSUE 1: "Cannot connect to Ganache"

**Error Message**:
```
⚠️ WARNING: Failed to connect to Ganache at http://127.0.0.1:7545
```

**Causes & Solutions**:

**Cause 1**: Ganache not running
```bash
# Solution: Open Ganache GUI application
# macOS: Applications → Ganache
# Windows: ganache.exe
# Linux: ./ganache-x64.AppImage
```

**Cause 2**: Wrong port
```bash
# Solution: Check truffle-config.js
# Should show: port: 7545
# Check Ganache window: RPC Server: http://127.0.0.1:7545
```

**Cause 3**: Ganache on different port
```bash
# Solution: Update truffle-config.js
port: 7545,  # Change to match Ganache

# Or in Ganache Settings → Server
# Change port to match truffle-config.js
```

**Cause 4**: Firewall blocking connection
```bash
# Solution: Allow local connections
# macOS: System Preferences → Security
# Windows: Windows Defender Firewall
# Allow 127.0.0.1 traffic
```

---

### ISSUE 2: "truffle compile" fails

**Error Message**:
```
Error: Cannot find module 'solc'
```

**Solution**:
```bash
# Reinstall npm packages
npm install

# Verify installation
truffle --version  # Should work now
```

**Error Message**:
```
SyntaxError in contracts/Patient.sol
```

**Solution**:
```bash
# Check Solidity syntax
# Visit: https://remix.ethereum.org
# Copy contract and check for errors

# Reinstall solc matching version
npm install solc@0.6.6
```

---

### ISSUE 3: "truffle migrate" fails

**Error Message**:
```
Error: Returned values aren't valid, did it run Out of Gas?
```

**Solution**:
```bash
# Increase gas limit in truffle-config.js
networks: {
    development: {
      host: "127.0.0.1",
      port: 7545,
      network_id: "*",
      gas: 8000000,        // Add this
      gasPrice: 2000000000  // Add this
    }
}

# Recompile and migrate
truffle migrate --reset
```

**Error Message**:
```
Error: Network mismatch
```

**Solution**:
```bash
# Reset Ganache and redeploy
# In Ganache: Click trash icon to reset
# Or create new workspace

# Then run:
truffle migrate --reset
```

---

### ISSUE 4: Flask won't start

**Error Message**:
```
ModuleNotFoundError: No module named 'flask'
```

**Solution**:
```bash
# Virtual environment not activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install flask flask_bootstrap flask_wtf wtforms web3 pandas cryptography pyopenssl
```

**Error Message**:
```
Port 5000 already in use
```

**Solution Option 1**: Kill process on port 5000
```bash
# macOS/Linux:
lsof -ti:5000 | xargs kill -9

# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Solution Option 2**: Use different port
```bash
flask run --port 5001
# Then access: http://127.0.0.1:5001
```

---

### ISSUE 5: Encryption key missing

**Error Message**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/enc_key.key'
```

**Solution**:
```bash
# Generate new key
python3

from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())

exit()

# Save to file
echo "your_key_here" > data/enc_key.key  # macOS/Linux
echo your_key_here > data\enc_key.key    # Windows

# Verify
cat data/enc_key.key      # macOS/Linux
type data\enc_key.key     # Windows
```

---

### ISSUE 6: "Module 'web3' not found"

**Error Message**:
```
ImportError: No module named 'web3'
```

**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install web3
pip install web3

# Verify
python3 -c "import web3; print(web3.__version__)"
```

---

### ISSUE 7: "Address already in use" or migrations stuck

**Error Message**:
```
Error: Transaction with nonce X already submitted
```

**Solution**:
```bash
# Reset Ganache workspace
# In Ganache: Click Settings → Reset Workspace
# Or create new workspace

# Clear build artifacts
rm -rf build/

# Recompile and migrate
truffle compile
truffle migrate
```

---

### ISSUE 8: CSV file corrupted

**Error Message**:
```
Error reading CSV file
```

**Solution**:
```bash
# Backup encrypted file
cp data/3f91fb273e0cc...csv data/backup_signin_data.csv

# Delete corrupted file
rm data/3f91fb273e0cc...csv

# Restart application
# New CSV will be created on next registration
```

---

### ISSUE 9: Browser shows blank page or 500 error

**Error Message**:
```
Internal Server Error
```

**Solution**:
```bash
# Check Flask console for error details
# Look for Python traceback

# Common causes:
# 1. Ganache not running
#    → Start Ganache GUI

# 2. Contract not deployed
#    → Run: truffle compile && truffle migrate

# 3. Encryption key missing
#    → Generate and save: data/enc_key.key

# 4. Python dependency missing
#    → pip install -r requirements.txt
```

---

### ISSUE 10: Transaction fails on blockchain

**Error Message**:
```
Error: Returned error: The method eth_sendTransaction does not exist/is not available
```

**Solution**:
```bash
# Ganache not connected to Truffle
# In Ganache: Settings → Server
# Verify Port: 7545, Host: 127.0.0.1

# Update truffle-config.js to match:
networks: {
    development: {
      host: "127.0.0.1",
      port: 7545,
      network_id: "*"
    }
}

# Restart Ganache
# Restart Flask
# Try again
```

---

## SECURITY

### ENCRYPTION METHODS USED

#### 1. Fernet Encryption (Symmetric)
```
Purpose: Encrypt/decrypt sensitive data
Algorithm: AES-128 in CBC mode + HMAC-SHA256
Key Length: 32 bytes (256 bits)
Used For: Patient data, medical records, unique IDs

Example:
from cryptography.fernet import Fernet
key = Fernet.generate_key()
cipher = Fernet(key)
encrypted = cipher.encrypt(b"sensitive data")
decrypted = cipher.decrypt(encrypted)
```

**Pros**:
- Industry standard
- Authenticated encryption
- Built-in integrity check

**Cons**:
- Same key for encrypt/decrypt
- Key must be stored securely

---

#### 2. SHA-256 Password Hashing (with Salt)
```
Purpose: Hash passwords irreversibly
Algorithm: SHA-256 with random salt
Salt Length: Random bytes
Used For: User password storage

Example:
import hashlib
salt = hashlib.sha256(os.urandom(60)).hexdigest()
password_hash = hashlib.pbkdf2_hmac(
    'sha256',
    password.encode('utf-8'),
    salt.encode('utf-8'),
    100000  # iterations
)
```

**Advantages**:
- One-way function (cannot reverse)
- Salt prevents rainbow table attacks
- Multiple iterations slow down brute force

**Disadvantages**:
- Must compare hashes (not actual passwords)
- Takes time to compute

---

#### 3. SSL/TLS (HTTPS)
```
Purpose: Encrypt data in transit
Used by: Flask application
Certificates: Generated with PyOpenSSL
Port: 443 (HTTPS) or 5000 (development)

In production:
- Use proper SSL certificates (Let's Encrypt)
- Enable HTTPS only
- Use secure cookies (HttpOnly, Secure flags)
```

---

#### 4. Ethereum Blockchain Immutability
```
Purpose: Permanent, tamper-proof record keeping
Method: Cryptographic hash linking
Used For: Medical records, access logs, audit trails

How it works:
- Each transaction hashed with SHA-256
- Hash includes previous block hash
- Changing one block invalidates chain
- Network consensus prevents tampering
```

---

### SECURITY BEST PRACTICES

#### File Security

```bash
# 1. NEVER commit encryption key
echo "data/enc_key.key" >> .gitignore

# 2. NEVER commit passwords
echo ".env" >> .gitignore

# 3. Protect file permissions
chmod 600 data/enc_key.key  # Read-only for owner

# 4. Backup encryption key securely
cp data/enc_key.key data/enc_key.backup.key
# Store backup in secure location (not GitHub)
```

---

#### Environment Variables

**Create .env file** (not committed):
```
FLASK_ENV=production
FLASK_SECRET_KEY=your-secret-key-here
GANACHE_URL=http://127.0.0.1:7545
ENCRYPTION_KEY_PATH=data/enc_key.key
```

**Load in main.py**:
```python
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
GANACHE_URL = os.getenv('GANACHE_URL')
```

---

#### Password Requirements

Enforce strong passwords:
```
- Minimum 8 characters
- Mix of uppercase and lowercase
- At least one number
- At least one special character (!@#$%^&*)
- Not commonly used passwords (check against list)
```

**In model.py**:
```python
password = PasswordField('Password', [
    validators.DataRequired(),
    validators.Length(min=8),
    validators.Regexp(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])',
        message='Password must contain lowercase, uppercase, digit, and special char'
    )
])
```

---

#### Access Control

```python
# Only patient can grant/revoke access
@app.route('/grant_access', methods=['POST'])
@login_required
def grant_access():
    if session['role'] != 'patient':
        return "Unauthorized", 403
    # ... rest of code

# Only auditor can query records if authorized
def check_auditor_access(auditor_email, patient_email):
    # Check blockchain for authorization
    # Check Patient.sol allowedAuditors mapping
    pass
```

---

#### Database Security

**Current (CSV files)**:
- Encrypted data only
- No plaintext storage
- Limited to single node

**Production Recommendation**:
```
- Migrate to PostgreSQL + encryption
- Use row-level security
- Encrypt columns at database level
- Implement audit triggers
```

---

### SECURITY AUDIT CHECKLIST

- [ ] Encryption key secured and backed up
- [ ] `data/enc_key.key` NOT in GitHub
- [ ] Passwords hashed with salt
- [ ] HTTPS/TLS enabled in production
- [ ] CSRF protection enabled (flask_wtf)
- [ ] SQL injection prevented (parameterized queries)
- [ ] XSS protection enabled (template escaping)
- [ ] Rate limiting implemented
- [ ] Access logs maintained
- [ ] Regular backups taken
- [ ] Dependencies kept updated
- [ ] Security headers set (CSP, X-Frame-Options)
- [ ] Secrets stored in environment variables
- [ ] No debug mode in production
- [ ] Sessions expire after inactivity

---

## PRODUCTION DEPLOYMENT

### PRE-DEPLOYMENT CHECKLIST

- [ ] Code reviewed and tested
- [ ] All unit tests pass
- [ ] Environment variables configured
- [ ] Database backups available
- [ ] SSL certificates obtained
- [ ] Monitoring set up
- [ ] Logging configured
- [ ] Security audit completed

---

### MIGRATION TO ETHEREUM TESTNET

**Why**: Test on real Ethereum before mainnet

**Steps**:

#### 1. Get Testnet ETH
```bash
# Go to Rinkeby faucet: https://www.rinkeby.io/
# Enter your Ethereum address
# Receive 18.75 ETH (worth ~$0)
```

#### 2. Install Wallet Provider
```bash
npm install @truffle/hdwallet-provider
```

#### 3. Update truffle-config.js
```javascript
const HDWalletProvider = require('@truffle/hdwallet-provider');
const mnemonic = "your 12 word seed phrase";
const infuraKey = "your infura project ID";

module.exports = {
  networks: {
    rinkeby: {
      provider: () => new HDWalletProvider(
        mnemonic,
        `https://rinkeby.infura.io/v3/${infuraKey}`
      ),
      network_id: 4,
      gasPrice: 1000000000, // 1 gwei
      from: '0x...' // your address
    }
  }
};
```

#### 4. Deploy to Testnet
```bash
truffle migrate --network rinkeby
```

#### 5. Verify Deployment
```bash
# Check on Etherscan: https://rinkeby.etherscan.io
# Paste contract address
# Verify contract code
```

---

### MIGRATION TO ETHEREUM MAINNET

**⚠️ WARNING**: Real money involved. Use extreme caution.

#### 1. Prepare Production Build
```bash
# Test thoroughly on testnet first
# Code review by security professionals
# Run gas optimization
```

#### 2. Get Mainnet ETH
```bash
# Purchase ETH from exchange (Coinbase, Kraken)
# Transfer to deployment account
# Minimum: Cost of deployment (depends on gas prices)
# Example: $50-500 USD
```

#### 3. Update Configuration
```javascript
const mainnet = {
  provider: () => new HDWalletProvider(
    mnemonic,
    `https://mainnet.infura.io/v3/${infuraKey}`
  ),
  network_id: 1,
  gasPrice: 20000000000, // 20 gwei (adjust based on network)
  from: '0x...' // your address
};
```

#### 4. Deploy
```bash
truffle migrate --network mainnet
# CAREFUL: This is irreversible!
```

#### 5. Verify on Etherscan
```
# Contract: https://etherscan.io
# Check transactions and balances
```

---

### WEB SERVER DEPLOYMENT

#### Option 1: AWS EC2

```bash
# 1. Create EC2 instance (Ubuntu 20.04)
# 2. SSH into instance
ssh -i key.pem ubuntu@ip-address

# 3. Install dependencies
sudo apt update
sudo apt install python3 python3-venv nodejs npm git

# 4. Clone repository
git clone https://github.com/username/EHRBlockchain.git
cd EHRBlockchain

# 5. Setup as above
npm install
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Install Gunicorn (production WSGI server)
pip install gunicorn

# 7. Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

---

#### Option 2: Heroku

```bash
# 1. Install Heroku CLI
npm install -g heroku

# 2. Create Procfile
echo "web: gunicorn -w 4 -b 0.0.0.0:\$PORT main:app" > Procfile

# 3. Create requirements.txt
pip freeze > requirements.txt

# 4. Push to Heroku
heroku create ehr-blockchain
git push heroku main

# 5. Set environment variables
heroku config:set GANACHE_URL=http://...
```

---

#### Option 3: Docker

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=main.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "main:app"]
```

```bash
# Build image
docker build -t ehr-blockchain .

# Run container
docker run -p 5000:5000 \
  -e GANACHE_URL=http://ganache:7545 \
  ehr-blockchain
```

---

### MONITORING & LOGGING

#### Application Logging
```python
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

logger = logging.getLogger(__name__)
logger.info(f"Patient {email} registered")
```

#### Error Tracking (Sentry)
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()]
)
```

#### Performance Monitoring
```python
# Track response times
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    logger.info(f"Request took {duration}s: {request.path}")
    return response
```

---

### BACKUP STRATEGY

```bash
# Daily backups of encryption key
sudo cp data/enc_key.key /backup/enc_key.$(date +%Y%m%d).backup

# Daily CSV backups
sudo cp data/*.csv /backup/data_$(date +%Y%m%d).backup

# Weekly blockchain snapshots
# Export blockchain data for disaster recovery
```

---

### DISASTER RECOVERY

```
1. Restore encryption key from backup
   - Essential for decrypting any stored data
   - If lost, all encrypted data becomes useless

2. Restore patient CSV files
   - Contains all patient registrations
   - Must be encrypted with same key

3. Verify blockchain integrity
   - Check Ganache/Ethereum for transaction history
   - Redeploy contracts if necessary

4. Test user access
   - Verify login still works
   - Check records are accessible
```

---

## GLOSSARY

| Term | Definition |
|------|-----------|
| **ABI** | Application Binary Interface - describes contract functions |
| **Bytecode** | Compiled EVM code that runs on blockchain |
| **Fernet** | Symmetric encryption algorithm (AES + HMAC) |
| **Ganache** | Local Ethereum blockchain simulator |
| **Gas** | Unit of computation cost on Ethereum |
| **RPC** | Remote Procedure Call - communication protocol |
| **Solidity** | Programming language for Ethereum smart contracts |
| **Smart Contract** | Self-executing code on blockchain |
| **Transaction** | Action recorded on blockchain (costs gas) |
| **Truffle** | Ethereum development framework |
| **Web3.py** | Python library for blockchain interaction |

---

## QUICK REFERENCE - COMMAND SUMMARY

```bash
# SETUP (First Time)
node --version && npm --version
python3 --version
npm install truffle -g
npm install
python3 -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate
pip install flask flask_bootstrap flask_wtf wtforms web3 pandas cryptography pyopenssl requests
python3
  from cryptography.fernet import Fernet
  key = Fernet.generate_key()
  print(key.decode())
  exit()
echo "key_here" > data/enc_key.key

# RUNNING (Every Session)
# Terminal 1: Open Ganache GUI

# Terminal 2:
cd EHRBlockchain
truffle compile
truffle migrate

# Terminal 3:
cd EHRBlockchain
source venv/bin/activate
export FLASK_APP=main.py
export FLASK_ENV=development
flask run

# BROWSER
# http://127.0.0.1:5000

# CLEANUP
deactivate  # Exit virtual environment
rm -rf venv  # Remove virtual environment
rm -rf build/  # Remove compiled contracts
```

---

## SUPPORT & RESOURCES

- **Project Repo**: https://github.com/username/EHRBlockchain
- **Documentation**: [SETUP_AND_RUN_GUIDE.md](SETUP_AND_RUN_GUIDE.md)
- **Quick Start**: [QUICK_START_SPEAKING_GUIDE.md](QUICK_START_SPEAKING_GUIDE.md)

### External Resources

- **Truffle**: https://trufflesuite.com/docs/
- **Web3.py**: https://web3py.readthedocs.io/
- **Flask**: https://flask.palletsprojects.com/
- **Solidity**: https://docs.soliditylang.org/
- **Ethereum**: https://ethereum.org/
- **Cryptography**: https://cryptography.io/

### Support Contacts

- **Issues**: Create GitHub issue
- **Email**: support@eehrblockchain.com
- **Discord**: https://discord.gg/...

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | May 2, 2026 | Initial comprehensive documentation |

---

**Document**: EHR Blockchain - Complete End-to-End Documentation  
**Status**: FINAL  
**Last Updated**: May 2, 2026  
**Author**: Development Team
