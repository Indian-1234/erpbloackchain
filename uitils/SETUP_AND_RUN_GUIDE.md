# EHR Blockchain - Complete Setup & Run Guide

## Project Overview

**EHR Blockchain** is a decentralized Electronic Health Records (EHR) management system built on Ethereum Blockchain. It provides secure, immutable, and encrypted storage of patient medical records with role-based access control for patients and auditors/doctors.

### Key Features
- ✅ **Decentralized**: Built on Ethereum Smart Contracts
- ✅ **Immutable**: All changes recorded on blockchain permanently
- ✅ **Secure**: Encrypted data storage with password hashing
- ✅ **Private**: Patients control who can access their records
- ✅ **Transparent**: All transactions visible on blockchain

---

## Software Tools Used

### 1. **Blockchain Platform**
- **Solidity**: Smart contract programming language for Ethereum
- **Ganache GUI**: Local blockchain simulator and explorer
- **Truffle**: Development environment for compiling and deploying smart contracts

### 2. **Backend**
- **Python 3**: Server-side programming language
- **Flask**: Web framework for building the user interface
- **Web3.py**: Python library to connect with Ethereum blockchain

### 3. **Frontend**
- **HTML/CSS**: Web page markup and styling
- **Bootstrap**: CSS framework for responsive design
- **Jinja**: Template engine for dynamic HTML

### 4. **Security**
- **Cryptography (Fernet)**: Encrypt/decrypt sensitive user data
- **Hashlib**: Hash passwords with salt
- **PyOpenSSL**: SSL/TLS certificates for HTTPS

### 5. **Data Processing**
- **Pandas**: Read/write CSV files
- **JSON**: Configuration and data format

---

## Prerequisites

Before starting, ensure you have installed:

1. **Python 3.8+** - [Download](https://www.python.org/downloads/)
2. **Node.js & npm** - [Download](https://nodejs.org/)
3. **Ganache GUI** - [Download](https://www.trufflesuite.com/ganache)
4. **Git** (optional) - For version control

---

## Step-by-Step Setup

### Step 1: Install Node.js Dependencies

```bash
# Navigate to project folder
cd EHRBlockchain

# Install Truffle globally
npm install truffle -g

# Install project dependencies
npm install
```

### Step 2: Install Python Dependencies

```bash
# Create a Python virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install Python libraries
pip install flask flask_bootstrap flask_wtf wtforms web3 pandas cryptography pyopenssl requests
```

### Step 3: Generate Encryption Key

```bash
# Open Python shell
python3

# Run these commands:
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())

# Copy the generated key and save it to: data/enc_key.key
```

Then create the file:
```bash
echo "your_generated_key_here" > data/enc_key.key
```

---

## How to Run

### Step 1: Start Ganache Local Blockchain

1. Open **Ganache GUI** application
2. Click **"New Workspace"** or **"Quick Start"**
3. Look for the **RPC Server** address (default: `http://127.0.0.1:7545`)
4. Keep Ganache running in the background

### Step 2: Compile & Deploy Smart Contracts

```bash
# From the project folder
cd EHRBlockchain

# Compile Solidity contracts
truffle compile

# Deploy contracts to Ganache
truffle migrate
```

**Expected Output:**
```
Compiling your contracts...
✓ Compiled successfully using:
   - solc: 0.6.6

Starting migrations...
✓ Deploying Migrations contract
✓ Deploying Patient contract
```

### Step 3: Start Flask Application

Open a **new terminal** and run:

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Set Flask environment variables
export FLASK_APP=main.py
export FLASK_ENV=development

# Run the Flask server
flask run
```

**Expected Output:**
```
 * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
```

### Step 4: Access the Application

Open your browser and go to:
```
http://127.0.0.1:5000
```

You should see the **EHR Blockchain** homepage.

---

## User Workflow

### Patient Registration & Login
1. Click **"Patient Sign Up"**
2. Enter: Name, Email, Password, Medical Details
3. System encrypts data and stores on blockchain
4. Login with email and password

### Managing Medical Records
1. Login as patient
2. **Add Record**: Enter health information
3. **View Records**: All records stored immutably on blockchain
4. **Grant Access**: Add auditor/doctor emails to view your records

### Auditor/Doctor Actions
1. Click **"Auditor Sign Up"**
2. Enter: Name, Email, Password
3. Login as auditor
4. **View Records**: Only see records patient has authorized
5. **Audit Trail**: See timestamp of all modifications

---

## Project Structure

```
EHRBlockchain/
├── main.py                 # Flask app & blockchain connection
├── model.py                # Database models & forms
├── contracts/
│   ├── Patient.sol         # Smart contract for patient records
│   └── Migrations.sol      # Truffle migrations contract
├── migrations/
│   ├── 1_initial_migration.js
│   └── 2_deploy_contract.js
├── templates/              # HTML web pages
│   ├── index.html
│   ├── login.html
│   ├── patient.html
│   └── audit.html
├── static/                 # CSS & images
├── data/                   # Encrypted data files
│   └── enc_key.key         # Encryption key (keep secret!)
└── build/contracts/        # Compiled contracts (auto-generated)
```

---

## Troubleshooting

### Issue: "Cannot connect to Ganache"
**Solution**: 
- Check Ganache is running
- Verify port is 7545 in `truffle-config.js`
- Restart Ganache application

### Issue: "Compilation failed"
**Solution**:
```bash
# Clean and recompile
rm -rf build/
truffle compile
```

### Issue: "Flask not found"
**Solution**:
```bash
# Activate virtual environment and reinstall
source venv/bin/activate
pip install flask web3 pandas cryptography
```

### Issue: "Encryption key missing"
**Solution**:
```bash
# Regenerate encryption key
python3
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
# Save to data/enc_key.key
```

---

## Security Notes

⚠️ **Important Security Considerations**:

1. **Never commit `data/enc_key.key` to GitHub** - Add to `.gitignore`
2. **Change default Ganache accounts** before production
3. **Use environment variables** for sensitive data
4. **Enable HTTPS** in production using SSL certificates
5. **Keep passwords hashed** - Never store plain text passwords

---

## Testing the Application

### Test Patient Flow
1. Register as patient "John Doe"
2. Add medical record: "Annual Checkup - Normal"
3. Login as auditor "Dr. Smith"
4. Patient grants auditor access
5. Dr. Smith views the record

### Verify Blockchain
1. Open Ganache
2. Go to **"Transactions"** tab
3. See all smart contract calls recorded

---

## Next Steps / Production Deployment

1. **Migrate to Ethereum Testnet** (Rinkeby, Goerli)
   - Update `truffle-config.js` with testnet RPC URL
   - Use Infura for remote nodes

2. **Deploy to Production Ethereum**
   - Deploy Patient smart contract mainnet
   - Use proper wallet management

3. **Database Migration**
   - Replace CSV files with PostgreSQL/MongoDB
   - Keep encryption key in secure vault

4. **Use Web3 Wallet**
   - Integrate MetaMask for user authentication
   - Allow users to manage their own wallets

---

## Support & Documentation

- **Truffle Docs**: https://trufflesuite.com/docs/
- **Web3.py Docs**: https://web3py.readthedocs.io/
- **Flask Docs**: https://flask.palletsprojects.com/
- **Solidity Docs**: https://docs.soliditylang.org/

---

## Summary Commands

**Quick Reference - All Commands to Run**

```bash
# Terminal 1: Start Ganache GUI
# (Download from https://www.trufflesuite.com/ganache)

# Terminal 2: Compile & Deploy
truffle compile
truffle migrate

# Terminal 3: Start Flask
source venv/bin/activate
export FLASK_APP=main.py
export FLASK_ENV=development
flask run

# Open browser: http://127.0.0.1:5000
```

---

**Version**: 1.0  
**Last Updated**: 2026-05-02  
**Project**: EHR Blockchain System
