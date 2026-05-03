# EHR Blockchain - Folder Structure Explained

## Complete Project Tree

```
EHRBlockchain/
│
├── 📄 Root Configuration Files
│   ├── main.py                          ← Flask web application (MAIN FILE)
│   ├── model.py                         ← Forms & data models
│   ├── truffle-config.js                ← Truffle configuration
│   ├── package.json                     ← Node.js dependencies
│   ├── package-lock.json                ← Lock file for npm
│   ├── abi.json                         ← Contract interface
│   ├── bytecode.json                    ← Compiled bytecode
│   ├── README.md                        ← Project overview
│   ├── LICENSE                          ← License file
│   └── .gitignore                       ← Git ignore rules
│
├── 📁 contracts/ (SMART CONTRACTS)
│   ├── Patient.sol                      ← Main EHR smart contract
│   └── Migrations.sol                   ← Migration tracking contract
│
├── 📁 migrations/ (DEPLOYMENT SCRIPTS)
│   ├── 1_initial_migration.js           ← Deploy Migrations contract (runs first)
│   └── 2_deploy_contract.js             ← Deploy Patient contract (runs second)
│
├── 📁 build/ (AUTO-GENERATED - Compiled Contracts)
│   └── contracts/
│       ├── Migrations.json              ← Compiled Migrations contract
│       └── Patient.json                 ← Compiled Patient contract
│
├── 📁 templates/ (HTML WEB PAGES)
│   ├── index.html                       ← Home page
│   ├── login.html                       ← Login page
│   ├── patient.html                     ← Patient dashboard
│   ├── patientreg.html                  ← Patient registration
│   ├── audit.html                       ← Auditor dashboard
│   ├── auditreg.html                    ← Auditor registration
│   └── result.html                      ← Result/confirmation page
│
├── 📁 static/ (CSS & IMAGES)
│   ├── css/
│   │   ├── bootstrap.css                ← Bootstrap CSS
│   │   ├── bootstrap.min.css            ← Bootstrap minified
│   │   ├── bootstrap-grid.css           ← Grid system
│   │   └── bootstrap-reboot.css         ← CSS reboot
│   └── img/
│       └── index.png                    ← Project image
│
├── 📁 data/ (ENCRYPTED DATA FILES)
│   ├── enc_key.key                      ← Encryption key (SECRET!)
│   ├── 3f91fb273e0cc...csv              ← Encrypted signin data
│   └── f415ea3131a...csv                ← Encrypted unique ID mappings
│
├── 📁 test/ (TEST FILES)
│   └── (empty - no tests yet)
│
├── 📁 node_modules/ (AUTO-GENERATED - Node packages)
│   ├── truffle/
│   ├── solc/
│   └── (other npm packages)
│
├── 📁 .venv/ or venv/ (AUTO-GENERATED - Python virtual environment)
│   ├── bin/
│   ├── lib/
│   └── pyvenv.cfg
│
└── 📁 images/ (PROJECT IMAGES)
    └── index.png
```

---

## Detailed Folder Explanations

### 1️⃣ **Root Level Files**

#### **main.py** (The Heart of the Application)
```
Purpose: Flask web application
Size: 1000+ lines
Contains:
  ✓ All web routes (@app.route)
  ✓ Login/signup handlers
  ✓ Blockchain connection (Web3.py)
  ✓ Encryption/decryption functions
  ✓ Medical record management
  ✓ CSV data handling
  
When it runs:
  - Flask server starts on http://127.0.0.1:5000
  - Connects to Ganache blockchain
  - Serves HTML templates to users
```

#### **model.py** (Form Validation)
```
Purpose: WTForms form classes
Contains:
  ✓ PatientRegForm - Patient registration form
  ✓ AuditRegForm - Auditor registration form
  ✓ LogForm - Login form
  ✓ Field validators (email, password, etc)
  ✓ Error messages
  
Used by: main.py to validate user input
```

#### **truffle-config.js** (Blockchain Configuration)
```
Purpose: Configure Truffle to connect to Ganache
Contains:
  ✓ Network settings (127.0.0.1:7545)
  ✓ Solidity compiler version (0.6.6)
  ✓ Gas settings
  
Used by: Truffle during compile and deploy
```

#### **package.json** (Node.js Dependencies)
```
Purpose: Define Node.js packages to install
Contains:
  ✓ Truffle 5.11.5 (blockchain framework)
  ✓ Solc 0.6.6 (Solidity compiler)
  
When you run: npm install
  → Installs all these packages
```

#### **abi.json** (Contract Interface)
```
Purpose: Describes smart contract functions
Format: JSON
Used by: Web3.py to call smart contract functions
Contains: Function signatures, parameters, return types
```

#### **bytecode.json** (Compiled Contract)
```
Purpose: Machine code for smart contract
Format: JSON with hex bytecode
Used by: Deployment to blockchain
Created by: truffle compile
```

---

### 2️⃣ **contracts/ (Smart Contracts)**

#### **Patient.sol**
```
Purpose: Main Ethereum smart contract
Language: Solidity 0.6.6
Contains:
  ✓ Patient struct (name, email, etc)
  ✓ Medical record struct (date, details, status)
  ✓ Functions to add/update records
  ✓ Access control (who can view records)
  ✓ Audit log functionality
  
Deployed to: Ganache blockchain
```

#### **Migrations.sol**
```
Purpose: Track deployment history
Auto-generated by: Truffle framework
Used for: Ensuring migrations run in correct order
```

---

### 3️⃣ **migrations/ (Deployment Instructions)**

#### **1_initial_migration.js**
```
Purpose: Deploy Migrations contract (first step)
Runs: First during "truffle migrate"
Creates: Migrations contract instance
Auto-generated by: Truffle init
```

#### **2_deploy_contract.js**
```
Purpose: Deploy Patient contract (second step)
Runs: After 1_initial_migration.js completes
Creates: Patient contract instance
Params: Initializes with default values
```

**Deployment Flow:**
```
truffle migrate
    ↓
Runs 1_initial_migration.js
    ↓
Runs 2_deploy_contract.js
    ↓
Contracts now on Ganache blockchain
```

---

### 4️⃣ **build/ (Compiled Output)**

#### **build/contracts/Patient.json**
```
Purpose: Compiled Patient smart contract
Auto-generated by: truffle compile
Contains:
  ✓ Complete ABI (function signatures)
  ✓ Bytecode (machine code)
  ✓ Deployment addresses
  ✓ Compiler settings
  ✓ Network information

Used by: Web3.py (Python code reads this)
```

#### **build/contracts/Migrations.json**
```
Purpose: Compiled Migrations contract
Auto-generated by: truffle compile
Similar to: Patient.json but for Migrations
```

**Important:**
```
⚠️ DO NOT EDIT manually
✓ Auto-generated by: truffle compile
✓ Re-generated each time you compile
✓ Delete with: rm -rf build/
```

---

### 5️⃣ **templates/ (HTML Web Pages)**

#### **index.html** (Home Page)
```
What user sees: Landing page
Contains:
  ✓ Project title
  ✓ Project description
  ✓ Login buttons (Patient & Auditor)
  ✓ Sign up links
  ✓ Bootstrap styling
```

#### **login.html** (Login Page)
```
What user sees: Authentication page
Contains:
  ✓ Email input field
  ✓ Password input field
  ✓ Role selector (Patient or Auditor)
  ✓ Submit button
```

#### **patientreg.html** (Patient Registration)
```
What user sees: Sign-up form
Contains:
  ✓ Account number (0-9)
  ✓ First name, Last name
  ✓ Email, Phone
  ✓ City, Zip code
  ✓ Insurance number
  ✓ Password (with confirmation)
  ✓ Submit button

Form data → main.py → Encryption → CSV → Blockchain
```

#### **patient.html** (Patient Dashboard)
```
What user sees: After patient login
Contains:
  ✓ Patient name & details
  ✓ Add medical record button
  ✓ View records list
  ✓ Grant/revoke auditor access
  ✓ View access history
```

#### **auditreg.html** (Auditor Registration)
```
What user sees: Auditor sign-up form
Contains:
  ✓ Account number
  ✓ Name, Email
  ✓ Employee ID
  ✓ Password
```

#### **audit.html** (Auditor Dashboard)
```
What user sees: After auditor login
Contains:
  ✓ Search for patients
  ✓ View authorized records
  ✓ See timestamps
  ✓ Download records (if enabled)
```

#### **result.html** (Confirmation Page)
```
What user sees: After action completion
Contains:
  ✓ Success/error message
  ✓ Transaction details
  ✓ Links to next action
```

---

### 6️⃣ **static/ (CSS & Images)**

#### **static/css/ (Styling)**
```
bootstrap.css              - Full Bootstrap framework
bootstrap.min.css          - Minified version (smaller size)
bootstrap-grid.css         - Grid layout system
bootstrap-reboot.css       - CSS resets
```

**Purpose:** Make web pages look professional and responsive

#### **static/img/ (Images)**
```
index.png                  - Project screenshot/logo
Used in: Templates for visual appeal
```

---

### 7️⃣ **data/ (Encrypted Data Storage)**

#### **enc_key.key** (Encryption Master Key)
```
Purpose: Fernet encryption key
Size: ~44 characters
Example: KJ8_-vZ3qL9...

🔒 SECURITY:
  ⚠️ NEVER commit to GitHub
  ⚠️ KEEP SAFE - if lost, all data unrecoverable
  ✓ Add to .gitignore
  ✓ Backup securely

How created:
  from cryptography.fernet import Fernet
  key = Fernet.generate_key()
  print(key.decode())  # Save this
```

#### **3f91fb273e0cc...csv** (Hashed Filename)
```
Purpose: Store encrypted user credentials
Actual name: Hashed version of "signin_data"
Contents:
  ✓ Email (encrypted)
  ✓ Password hash (SHA256 + salt)
  ✓ User role (patient/auditor)
  ✓ User metadata (encrypted)

Format:
  - CSV file (comma-separated values)
  - All data encrypted
  - Cannot read without encryption key

Created when: User registers
Read when: User logs in
```

#### **f415ea3131a...csv** (Unique ID Mapping)
```
Purpose: Map unique IDs to blockchain records
Actual name: Hashed version of "uniqueid_data"
Contents:
  ✓ Unique record ID (encrypted)
  ✓ Patient ID (encrypted)
  ✓ Blockchain address (encrypted)
  ✓ Timestamp

Stores: Links between local IDs and blockchain addresses
```

---

### 8️⃣ **test/ (Test Files)**

```
Currently: Empty folder
Purpose: For unit tests and integration tests
Future use: 
  ✓ Test smart contracts
  ✓ Test Flask routes
  ✓ Test encryption functions
```

---

### 9️⃣ **node_modules/ (Node Packages)**

```
AUTO-GENERATED when you run: npm install
Contains: All JavaScript packages
  ✓ Truffle framework
  ✓ Solc compiler
  ✓ Dependencies of dependencies

🗑️ Can be deleted - will be reinstalled with: npm install
⚠️ Should NOT be committed to GitHub (add to .gitignore)
Size: ~500MB
```

---

### 🔟 **.venv/ or venv/ (Python Environment)**

```
AUTO-GENERATED when you run: python3 -m venv venv
Contains:
  ✓ Python interpreter
  ✓ All installed Python packages
  ✓ pip package manager

🗑️ Can be deleted - will be recreated with: python3 -m venv venv
⚠️ Should NOT be committed to GitHub
Location: /bin/  contains Python executable
```

---

### 1️⃣1️⃣ **images/ (Project Images)**

```
Purpose: Store project screenshots, logos, diagrams
Contains: index.png and other graphics
Used in: README.md, documentation
```

---

## File Type Guide

| Extension | Purpose | Example |
|-----------|---------|---------|
| `.py` | Python files | main.py, model.py |
| `.sol` | Smart contracts (Solidity) | Patient.sol |
| `.js` | JavaScript files | truffle-config.js |
| `.json` | Data format | abi.json, package.json |
| `.html` | Web pages | index.html |
| `.css` | Styling | bootstrap.css |
| `.csv` | Data storage | signin_data.csv |
| `.key` | Encryption key | enc_key.key |
| `.md` | Documentation | README.md |

---

## Data Flow Through Folders

```
USER REGISTRATION:
  ↓
  templates/patientreg.html (Fill form)
  ↓
  main.py (Validate & encrypt)
  ↓
  data/signin_data.csv (Store encrypted)
  ↓
  Web3.py calls contracts/Patient.sol
  ↓
  Ganache stores record
  ↓
  build/contracts/Patient.json updated


USER LOGIN:
  ↓
  templates/login.html (Enter credentials)
  ↓
  main.py (Read from CSV, compare)
  ↓
  data/signin_data.csv (Decrypt & verify)
  ↓
  Create session
  ↓
  templates/patient.html (Show dashboard)


ADD MEDICAL RECORD:
  ↓
  templates/patient.html (Fill form)
  ↓
  main.py (Encrypt record)
  ↓
  Web3.py sends to contracts/Patient.sol
  ↓
  Ganache records transaction
  ↓
  data/uniqueid_data.csv (Map record ID)
```

---

## Ignore These Folders (In .gitignore)

```
⚠️ Should NOT be in GitHub:

build/              ← Auto-generated by Truffle
node_modules/       ← Auto-generated by npm
.venv/ or venv/     ← Auto-generated by Python
__pycache__/        ← Auto-generated by Python
data/enc_key.key    ← SENSITIVE encryption key
.env                ← Environment variables
.DS_Store           ← macOS system file
```

---

## Quick Reference

| Folder | Created By | Auto-generated? | Can Delete? |
|--------|-----------|-----------------|------------|
| contracts/ | Developer | No | No (need code) |
| migrations/ | Developer | No | No (need code) |
| templates/ | Developer | No | No (need code) |
| static/ | Developer | No | No (need styles) |
| build/ | Truffle | YES | Yes (rebuild with truffle compile) |
| node_modules/ | npm | YES | Yes (rebuild with npm install) |
| .venv/ | Python | YES | Yes (rebuild with python3 -m venv venv) |
| data/ | Application | Partially | Mostly No (contains user data) |

---

## Summary

```
📦 EHRBlockchain Project Structure
│
├── 🎯 MAIN APPLICATION
│   └── main.py ← Start here (Flask server)
│
├── 🔐 BLOCKCHAIN
│   ├── contracts/ ← Smart contracts (Solidity)
│   ├── migrations/ ← Deployment scripts
│   └── truffle-config.js ← Blockchain config
│
├── 🌐 WEB INTERFACE
│   ├── templates/ ← HTML pages
│   └── static/ ← CSS & images
│
├── 📊 DATA
│   └── data/ ← Encrypted user data
│
├── ⚙️ CONFIGURATION
│   ├── package.json ← Node packages
│   ├── model.py ← Forms
│   ├── abi.json ← Contract interface
│   └── bytecode.json ← Compiled code
│
└── 🛠️ AUTO-GENERATED (Don't edit)
    ├── build/ ← Compiled contracts
    ├── node_modules/ ← npm packages
    └── .venv/ ← Python packages
```

---

**This structure separates:**
- ✅ **Blockchain logic** (contracts/)
- ✅ **Web interface** (templates/, static/)
- ✅ **Backend logic** (main.py, model.py)
- ✅ **Data storage** (data/)
- ✅ **Configuration** (root level)

All working together to create a complete decentralized EHR system!

