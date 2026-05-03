# EHR Blockchain - Simple Start-to-End Speaking Guide

## Welcome! Let me walk you through everything step by step.

---

## PART 1: What is This Project?

**Listen carefully:**

This is an **Electronic Health Records system** that runs on **Ethereum Blockchain**. 

**What does that mean?**
- Patients can store their medical records securely
- Doctors or auditors can only see records that patients allow them to see
- Once a record is saved, nobody can change it or delete it - it's permanent
- Everything is encrypted so nobody can read it without permission

**Who uses it?**
- **Patients**: Sign up, add their medical records, give permission to doctors
- **Doctors/Auditors**: Sign up, view only the records patients allow them to see

That's it. Simple.

---

## PART 2: What Do We Need to Install?

**Four main things:**

### 1. Python 3
- Go to: https://www.python.org/downloads/
- Download Python 3.8 or newer
- Install it on your computer
- This runs the website (Flask)

### 2. Node.js & npm
- Go to: https://nodejs.org/
- Download the LTS version
- Install it
- This helps us compile the blockchain smart contracts

### 3. Ganache GUI
- Go to: https://www.trufflesuite.com/ganache
- Download Ganache GUI
- Install it
- This is our local blockchain - where we test everything

### 4. Git (Optional)
- Go to: https://git-scm.com/
- Download and install
- Useful for version control

**That's all we need to install!**

---

## PART 3: Setup Instructions (Copy-Paste Commands)

**Open your Terminal/Command Prompt and follow this exactly:**

### Step 1: Go to the Project Folder

```
cd EHRBlockchain
```

Type that and press Enter.

---

### Step 2: Install Truffle (Blockchain Tool)

```
npm install truffle -g
```

This installs Truffle globally on your computer. Wait for it to finish.

---

### Step 3: Install Project Dependencies

```
npm install
```

This reads `package.json` and installs the Node packages we need (Truffle and Solidity compiler). Wait for it to complete.

---

### Step 4: Create Python Virtual Environment

**On macOS or Linux:**
```
python3 -m venv venv
```

**On Windows:**
```
python -m venv venv
```

This creates an isolated Python environment. Good practice.

---

### Step 5: Activate Python Virtual Environment

**On macOS or Linux:**
```
source venv/bin/activate
```

**On Windows:**
```
venv\Scripts\activate
```

You should see `(venv)` at the start of your terminal line. If yes, it worked!

---

### Step 6: Install Python Libraries

Copy this entire command:

```
pip install flask flask_bootstrap flask_wtf wtforms web3 pandas cryptography pyopenssl requests
```

Wait for all the packages to install. This is the backend stuff - Flask, Web3, encryption, etc.

---

### Step 7: Generate Encryption Key

**Open Python:**
```
python3
```

**Type these lines (one by one):**
```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
```

You'll see a long string of characters. **Copy that entire string.**

**Exit Python:**
```python
exit()
```

---

### Step 8: Save the Encryption Key

**Create a new file:**
```
data/enc_key.key
```

**Put the key you copied inside it. Just the key string, nothing else.**

**Or use this command to create it:**
```
echo "YOUR_KEY_HERE" > data/enc_key.key
```

Replace `YOUR_KEY_HERE` with the actual key you copied.

---

**Setup Complete! Now we run it.**

---

## PART 4: Running the System (Start to Finish)

### Terminal 1: Start Ganache (Blockchain)

1. **Open Ganache GUI application** (the one you downloaded)
2. Click **"New Workspace"** or **"Quick Start"**
3. You'll see accounts with ETH balance
4. Look at the top - it says **RPC Server: http://127.0.0.1:7545**
5. **Keep this window open** - don't close it

This is our fake blockchain running locally. All our transactions will be recorded here.

---

### Terminal 2: Compile & Deploy Smart Contracts

**Open a NEW terminal/command prompt**

**Go to project folder:**
```
cd EHRBlockchain
```

**Compile the smart contracts:**
```
truffle compile
```

Wait for it. You should see:
```
✓ Compiled successfully using:
   - solc: 0.6.6
```

---

**Deploy to Ganache:**
```
truffle migrate
```

Wait. You should see something like:
```
Starting migrations...
✓ Deploying Migrations contract
✓ Deploying Patient contract
```

Great! The smart contracts are now on our fake blockchain.

---

### Terminal 3: Start Flask Website

**Open ANOTHER new terminal/command prompt**

**Go to project folder:**
```
cd EHRBlockchain
```

**Activate Python environment:**

On macOS/Linux:
```
source venv/bin/activate
```

On Windows:
```
venv\Scripts\activate
```

You should see `(venv)` at the start.

---

**Start Flask:**

On macOS/Linux:
```
export FLASK_APP=main.py
export FLASK_ENV=development
flask run
```

On Windows:
```
set FLASK_APP=main.py
set FLASK_ENV=development
flask run
```

You should see:
```
 * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
```

Perfect!

---

## PART 5: Using the Application

**Now open your web browser and go to:**
```
http://127.0.0.1:5000
```

You should see the **EHR Blockchain** home page.

---

### Test It Out:

**Step 1: Register as Patient**
1. Click "Patient Sign Up"
2. Enter name: "John Doe"
3. Enter email: "john@hospital.com"
4. Enter password: "password123"
5. Enter medical info: "Type O Blood, Allergies: None"
6. Click Register

The system encrypts this data and stores it on the blockchain.

---

**Step 2: Register as Auditor/Doctor**
1. Click "Auditor Sign Up"
2. Enter name: "Dr. Smith"
3. Enter email: "doctor@hospital.com"
4. Enter password: "password456"
5. Click Register

---

**Step 3: Add Medical Record as Patient**
1. Login as John Doe
2. Click "Add Medical Record"
3. Enter: "Annual Checkup - Blood Pressure Normal"
4. Click Add
5. You see the record on blockchain now

---

**Step 4: Grant Access to Doctor**
1. Still logged in as John
2. Click "Grant Access"
3. Enter Dr. Smith's email: "doctor@hospital.com"
4. Click Grant

---

**Step 5: View as Doctor**
1. Logout
2. Login as Dr. Smith
3. You can now see John's medical record
4. Everything is timestamped and immutable

---

**Step 6: Check Blockchain**
1. Go back to Ganache window
2. Click "Transactions" tab
3. You see all the transactions we just made
4. Everything is recorded permanently

---

## PART 6: What Happens Behind the Scenes?

**When patient registers:**
- System hashes password with salt
- Encrypts patient data with Fernet key
- Stores encrypted data in CSV file
- Creates record on blockchain

**When patient adds medical record:**
- Encrypts the record
- Sends transaction to smart contract
- Blockchain records it permanently
- Cannot be changed or deleted

**When doctor views record:**
- System checks if doctor has permission
- Decrypts the record
- Shows it on the webpage
- Blockchain shows timestamp

**Security layers:**
- Password hashing (Hashlib)
- Data encryption (Fernet)
- Blockchain immutability (Ethereum)
- Role-based access (Patient controls permissions)

---

## PART 7: If Something Goes Wrong

### Problem: "Cannot connect to Ganache"
**Solution:**
- Make sure Ganache window is open
- Check it says port 7545
- Restart Ganache

---

### Problem: "Compilation failed"
**Solution:**
```
rm -rf build/
truffle compile
```

---

### Problem: "Flask not found"
**Solution:**
```
source venv/bin/activate
pip install flask web3
```

---

### Problem: "Port 5000 already in use"
**Solution:**
- Close any other Flask processes
- Or use: `flask run --port 5001`

---

## PART 8: Important - Keep These Safe!

⚠️ **NEVER share these:**
- `data/enc_key.key` - The encryption key
- Passwords in Ganache
- Your private keys

**ADD TO .gitignore:**
```
data/enc_key.key
venv/
.env
```

So they don't accidentally go to GitHub.

---

## PART 9: Remember These 3 Terminals

**ALWAYS keep these 3 running at the same time:**

| Terminal | Command | Keep Open? |
|----------|---------|-----------|
| 1 | Ganache GUI | YES |
| 2 | `truffle compile && truffle migrate` | NO (run once) |
| 3 | `flask run` | YES |

Terminal 1 and 3 must stay open while you use the website.
Terminal 2 only runs once when you start.

---

## PART 10: Summary - Speaking Version

**Say this to anyone setting it up:**

"Here's what we do:

1. Install Python, Node.js, and Ganache
2. Go to the project folder
3. Install dependencies with npm and pip
4. Generate encryption key
5. Open Ganache - this is our fake blockchain
6. Run 'truffle compile && truffle migrate' - this deploys our smart contracts
7. Open a new terminal and run 'flask run' - this starts the website
8. Go to http://127.0.0.1:5000 in your browser
9. Register as patient or doctor
10. Test by adding records and granting permissions
11. Check Ganache to see all transactions recorded"

That's it!

---

## Quick Command Cheat Sheet

```bash
# Setup (one time)
cd EHRBlockchain
npm install truffle -g
npm install
python3 -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows
pip install flask flask_bootstrap flask_wtf wtforms web3 pandas cryptography pyopenssl requests

# Generate key
python3
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
exit()
# Save key to: data/enc_key.key

# Running (every time)
# Terminal 1: Open Ganache GUI
# Terminal 2:
truffle compile
truffle migrate

# Terminal 3:
source venv/bin/activate  # or: venv\Scripts\activate on Windows
export FLASK_APP=main.py
export FLASK_ENV=development
flask run

# Open browser: http://127.0.0.1:5000
```

---

**Done! You're ready to run the EHR Blockchain system!** 🎉

Version: 1.0
Date: May 2, 2026
