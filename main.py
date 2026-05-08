# app.py
#!bin/python
# to run truffle migrate after opening Ganache UI
# to run in development FLASK_APP=main.py FLASK_ENV=development flask run
# to run with ssl -->

from flask import Flask, request, render_template, redirect
from model import AuditRegForm, AuditActions
from model import PatientRegForm, PatientActions
from model import LogForm
from federated.fl_routes import fl_bp
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
import hashlib
import pandas as pd
from cryptography.fernet import Fernet
from dateutil import parser
from urllib.parse import quote
import requests

from web3 import Web3
import json

# install ganache using https://www.trufflesuite.com/ganache

# connect to ganache
ganache_url = "http://127.0.0.1:7545"
# pass in http url
from web3.providers.rpc import HTTPProvider
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Create a session with retry strategy for better connection handling
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=0.3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Use the session with Web3
web3 = Web3(HTTPProvider(ganache_url, session=session))

# Try to connect with retry logic
max_retries = 3
ganache_connected = False
for attempt in range(max_retries):
    try:
        connected = web3.is_connected()
        print(f"Web3 is connected = {connected}")
        if connected:
            ganache_connected = True
            print("Successfully connected to Ganache!")
            break
    except Exception as e:
        print(f"Connection attempt {attempt + 1} failed: {str(e)}")
        if attempt < max_retries - 1:
            import time
            time.sleep(1)

if not ganache_connected:
    print("⚠️  WARNING: Failed to connect to Ganache at http://127.0.0.1:7545")
    print("Please ensure Ganache is running. You can start it with:")
    print("  ganache-cli --host 127.0.0.1 --port 7545")
    print("  or open the Ganache GUI application")

# connect to remix
f = open('abi.json',)
abi = json.load(f)
f = open('bytecode.json',)
bytecode = json.load(f)['object']
contract = web3.eth.contract(abi=abi, bytecode=bytecode)

# default account to send money from default account in each user creation
# account_def = "0xa39c1505c345cc50C19924861659BbB242B9F6d8"
# pk_def = "f1f6e43d6e69d645805581739225db9e256377745fde1041aabf2e3357621386"

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY=b'\xd6\x04\xbdj\xfe\xed$c\x1e@\xad\x0f\x13,@G')
Bootstrap(app)
csrf = CSRFProtect(app)
app.register_blueprint(fl_bp)
csrf.exempt(fl_bp)

account_num = 0

# Helper function to check blockchain connectivity
def check_blockchain_connection():
    """Check if blockchain is connected, return error message if not"""
    try:
        if not web3.is_connected():
            return "Blockchain is not connected. Please ensure Ganache is running on http://127.0.0.1:7545"
        return None
    except Exception as e:
        return f"Error checking blockchain connection: {str(e)}. Please ensure Ganache is running."
# Encryption of authorization data
# Generate once use all time
#enc_key = Fernet.generate_key()
# get key
file = open('data/enc_key.key', 'rb') # rb = read bytes
enc_key  = file.read()
file.close()
fernet = Fernet(enc_key)

# IPFS Configuration
IPFS_API_URL = "http://127.0.0.1:5001/api/v0"
IPFS_GATEWAY_URL = "https://ipfs.io/ipfs/"

def upload_to_ipfs(data):
    """Upload data (text or bytes) to IPFS and return CID"""
    try:
        if isinstance(data, str):
            data = data.encode('utf-8')
        files = {'file': ('record.txt', data, 'text/plain')}
        response = requests.post(f"{IPFS_API_URL}/add", files=files, timeout=10)
        if response.status_code == 200:
            cid = response.json()['Hash']
            print(f"IPFS upload successful. CID: {cid}")
            return cid
        else:
            print(f"IPFS upload failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error connecting to IPFS: {str(e)}")
        return None

def fetch_from_ipfs(cid_input):
    """Fetch data from IPFS, handles hybrid text|CID records"""
    text_notes = ""
    target_cid = cid_input
    
    # Check if this is a hybrid record (Text | IPFS_CID:xxxx)
    if isinstance(cid_input, str) and " | IPFS_CID:" in cid_input:
        parts = cid_input.split(" | IPFS_CID:", 1)
        text_notes = parts[0].strip()
        target_cid = parts[1].strip()
        print(f"DEBUG: Hybrid record detected. Notes: '{text_notes}', CID: '{target_cid}'")

    if not is_ipfs_cid(target_cid):
        return cid_input, 'chain', False

    try:
        response = requests.post(f"{IPFS_API_URL}/cat?arg={target_cid}", timeout=8)
        if response.status_code == 200:
            content = response.content
            binary_signatures = [b'\x89PNG', b'\xff\xd8\xff', b'%PDF', b'IDAT', b'IHDR']
            if any(sig in content for sig in binary_signatures):
                display_text = text_notes if text_notes else "Medical Attachment"
                return display_text, 'local', True, target_cid
            
            try:
                text = content.decode('utf-8')
                if any(ord(c) < 32 and c not in '\n\r\t' for c in text[:500]):
                     display_text = text_notes if text_notes else "Medical Attachment"
                     return display_text, 'local', True, target_cid
                
                combined = f"{text_notes}\n\n{text}" if text_notes else text
                return combined.strip(), 'local', False, target_cid
            except UnicodeDecodeError:
                display_text = text_notes if text_notes else "Medical Attachment"
                return display_text, 'local', True, target_cid
    except Exception:
        pass
    
    return f"Error: Could not fetch from IPFS", 'error', False, target_cid

def is_ipfs_cid(value):
    """Check if a string looks like an IPFS CID"""
    return isinstance(value, str) and value.startswith(('Qm', 'bafy', '1220'))

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/patientreg', methods=['GET', 'POST'])
def patient_registration():
    form = PatientRegForm(request.form)
    if request.method == 'POST':
        if not form.validate_on_submit():
            # Show validation errors
            error_msg = "Please fix the errors below:\n" + "\n".join(
                [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
            )
            print(f"Form validation failed: {error_msg}")
            return render_template('patientreg.html', form=form, error=error_msg)
        
        # Check blockchain connection first
        blockchain_error = check_blockchain_connection()
        if blockchain_error:
            print(blockchain_error)
            return render_template('patientreg.html', form=form, error=blockchain_error)
        
        try:
            account_num = web3.eth.accounts[form.account_number.data]
            print(f"Patient registration: Using account {form.account_number.data} -> {account_num}")
        except (ValueError, IndexError) as e:
            error_msg = f"Invalid account number: {form.account_number.data}. Please use a valid account number between 0 and {len(web3.eth.accounts)-1}"
            print(error_msg)
            return render_template('patientreg.html', form=form, error=error_msg)
        except Exception as e:
            error_msg = f"Error connecting to blockchain: {str(e)}. Please ensure Ganache is running on http://127.0.0.1:7545"
            print(error_msg)
            return render_template('patientreg.html', form=form, error=error_msg)
            
        ###################### RECORD ACCOUNT DETAILS TO A FILE ##############################
        try:
            fname = hashlib.sha224(b"signin_data").hexdigest()
            f = open("data/"+fname+".csv", "a")
            pass_hash = hashlib.sha224(("loremipsum"+form.password.data).encode('utf-8')).hexdigest()
            encrypted_data = "patient" + ", " + str(fernet.encrypt("patient".encode('utf-8'))) + ", " +\
                    str(fernet.encrypt(form.name_first.data.encode('utf-8'))) + ", " +\
                    str(fernet.encrypt(form.name_last.data.encode('utf-8'))) + ", " +\
                    str(fernet.encrypt(form.email.data.encode('utf-8')))  + ", " +\
                    str(fernet.encrypt(form.phone.data.encode('utf-8')))  + ", " +\
                    str(fernet.encrypt(form.city.data.encode('utf-8')))  + ", " +\
                    str(fernet.encrypt(form.zip_code.data.encode('utf-8')))  + ", " +\
                    str(fernet.encrypt(form.insurance.data.encode('utf-8')))  + ", " +\
                    str(fernet.encrypt(pass_hash.encode('utf-8'))) + "\n"
            f.write(encrypted_data)
            f.close()
            print(f"Patient data encrypted and saved for {form.name_first.data} {form.name_last.data}")
        except Exception as e:
            error_msg = f"Error saving patient data: {str(e)}"
            print(error_msg)
            return render_template('patientreg.html', form=form, error=error_msg)

        ################## CONSTRUCTOR OF SMART CONTRACT -- DEPLOY #############################
        try:
            web3.eth.default_account = account_num
            print(f"Setting default account to {account_num}")
            
            # Deploy smart contract
            print("Deploying smart contract...")
            tx_hash = contract.constructor(
                str(form.name_first.data),
                str(form.name_last.data),
                str(form.insurance.data),
                "bdate", 
                str(form.email.data),
                str(form.phone.data),
                str(form.zip_code.data),
                str(form.city.data),
                "ekey"
            ).transact()
            print(f"Transaction hash: {tx_hash.hex()}")
            
            print("Waiting for transaction receipt...")
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Contract deployed at: {tx_receipt.contractAddress}")

            username = form.name_first.data + " " + form.name_last.data
            address = account_num
            pk = "no need for demo but will be sent in actual app as email"
            result = "We have emailed you a key pair and contract address! "+"\nNormally it will be emailed using emailing API:"
            patient_qr = "https://api.qrserver.com/v1/create-qr-code/?data="+ quote(str(account_num)) +"&size=150x150"
            print(f"Patient registration successful for {username}")
            return render_template('result.html', result=result, username = username, address = address, pk=pk, tx_hash = tx_hash.hex(), tx_receipt = tx_receipt, audit_qr=patient_qr)
        
        except Exception as e:
            error_msg = f"Error deploying smart contract: {str(e)}"
            print(f"Smart contract deployment error: {error_msg}")
            import traceback
            traceback.print_exc()
            return render_template('patientreg.html', form=form, error=error_msg)
    
    return render_template('patientreg.html', form=form)

@app.route('/auditreg', methods=['GET', 'POST'])
def audit_registration():
    form = AuditRegForm(request.form)
    global account_num
    account_num = 0
    if request.method == 'POST':
        if not form.validate_on_submit():
            # Show validation errors
            error_msg = "Please fix the errors below:\n" + "\n".join(
                [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
            )
            print(f"Form validation failed: {error_msg}")
            return render_template('auditreg.html', form=form, error=error_msg)
        
        # Check blockchain connection first
        blockchain_error = check_blockchain_connection()
        if blockchain_error:
            print(blockchain_error)
            return render_template('auditreg.html', form=form, error=blockchain_error)
        
        try:
            account_num = web3.eth.accounts[form.account_number.data]
            print(f"Audit registration: Using account {form.account_number.data} -> {account_num}")
        except (ValueError, IndexError) as e:
            error_msg = f"Invalid account number: {form.account_number.data}. Please use a valid account number between 0 and {len(web3.eth.accounts)-1}"
            print(error_msg)
            return render_template('auditreg.html', form=form, error=error_msg)
        except Exception as e:
            error_msg = f"Error connecting to blockchain: {str(e)}. Please ensure Ganache is running on http://127.0.0.1:7545"
            print(error_msg)
            return render_template('auditreg.html', form=form, error=error_msg)
        
        try:
            fname = hashlib.sha224(b"signin_data").hexdigest()
            f = open("data/"+fname+".csv", "a")
            pass_hash = hashlib.sha224(("loremipsum"+form.password.data).encode('utf-8')).hexdigest()
            encrypted_data = "audit" + ", " +str(fernet.encrypt("audit".encode('utf-8'))) + ", " +\
                    str(fernet.encrypt(form.name_first.data.encode('utf-8'))) + ", " +\
                    str(fernet.encrypt(form.name_last.data.encode('utf-8'))) + ", " +\
                    str(fernet.encrypt(form.email.data.encode('utf-8')))  + ", " +\
                    str(fernet.encrypt(form.employee_id.data.encode('utf-8')))  + ", " +\
                    str(fernet.encrypt("n/a".encode('utf-8')))  + ", " +\
                    str(fernet.encrypt("00008".encode('utf-8')))  + ", " +\
                    str(fernet.encrypt("0000000000".encode('utf-8')))  + ", " +\
                    str(fernet.encrypt(pass_hash.encode('utf-8'))) + "\n"
            f.write(encrypted_data)
            f.close()
            print(f"Audit data encrypted and saved for {form.name_first.data} {form.name_last.data}")
        except Exception as e:
            error_msg = f"Error saving audit data: {str(e)}"
            print(error_msg)
            return render_template('auditreg.html', form=form, error=error_msg)
        
        username = form.name_first.data + " " + form.name_last.data
        address = account_num
        pk = "no need for demo but will be sent in actual app as email"
        result = "We have emailed you a key pair! "+"\nNormally it will be emailed using emailing API:"
        audit_qr = "https://api.qrserver.com/v1/create-qr-code/?data="+ quote(str(account_num)) +"&size=150x150"
        print(f"Audit registration successful for {username}")
        return render_template('result.html', result=result, username = username, address = address, pk=pk, tx_hash =0, tx_receipt=0, audit_qr=audit_qr)
    
    return render_template('auditreg.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    fname = hashlib.sha224(b"signin_data").hexdigest()
    form = LogForm(request.form)
    form2 = PatientActions(request.form)
    form3 = AuditActions(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        address = form.user_name.data
        hashed_pass = hashlib.sha224(("loremipsum"+form.password.data).encode('utf-8')).hexdigest()
        
        valid_login = False
        try:
            df = pd.read_csv("data/"+fname+".csv", header=None)
            for index, row in df.iterrows():
                # The last column is the encrypted hashed password
                encrypted_pass = str(row.iloc[-1]).strip()
                try:
                    if encrypted_pass.startswith("b'") and encrypted_pass.endswith("'"):
                        encrypted_pass = encrypted_pass[2:-1]
                    decrypted_pass = fernet.decrypt(encrypted_pass.encode('utf-8')).decode('utf-8')
                    if decrypted_pass == hashed_pass:
                        valid_login = True
                        break
                except Exception:
                    continue
        except Exception:
            pass

        if not valid_login:
            error = 'Invalid Credentials. Please try again.'
        else:
            if str(form.contract_address.data) != "0":
                return redirect('patient?'+"address=" + str(form.user_name.data) + "&contract=" + str(form.contract_address.data) )
            else:
                return redirect('audit?'+ "address=" + form.user_name.data + "&contract=0")
    return render_template('login.html', form=form, error=error)

@app.route('/patient', methods=['GET', 'POST'])
def patientdash():
    form = PatientActions(request.form)
    account_address  = request.args.get("address")
    contract_address = request.args.get("contract")
    isCard = False
    if request.method == 'POST':
        if request.form.get('action1') == 'VALUE1':
            isCard  = True
            appointment_date = form.start_visit.data
            result = "Patient initiated visit."


            ################## Solidity Transaction ###################
            #find deployed contract
            contract = web3.eth.contract(address = contract_address, abi = abi)
            # assign default address
            web3.eth.default_account = account_address
            date_obj = parser.parse(form.start_visit.data)
            date_epoch = date_obj.timestamp()
            tx_hash  = contract.functions.start_visit(int(date_epoch)).transact()
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            event_logs = contract.events.event_start_visit.get_logs()
            qr_code = "https://api.qrserver.com/v1/create-qr-code/?data="+quote(str(event_logs[0]['args']['record_unique_id']))+"&size=150x150"
#             changes = filter.get_new_entries()
            print("--------------------changes-------------")
            print(event_logs)
            print("--------------------end changes-------------")
#             print(tx_receipt)
#             contract.functions.record_mapping()
            ################## End Solidity TRansaction ###############
            ###################### ENCRYPT & RECORD ACCOUNT DETAILS TO A FILE ##############################
            fname = hashlib.sha224(b"uniqueid_data").hexdigest()
            f = open("data/"+fname+".csv", "a")
            encrypted_data = str(fernet.encrypt(contract_address.encode('utf-8')))\
            +","+str(fernet.encrypt(str(event_logs[0]['args']['record_unique_id']).encode('utf-8')))+"\n"
            f.write(encrypted_data)
            f.close()
            ###################### END RECORD ACCOUNT DETAILS TO A FILE ########################

            return render_template("patient.html", form=form, isStart = True, isCard  = isCard, username=account_address,contract_address=contract_address, date = appointment_date, result=result, tx_receipt = tx_receipt, tx_hash=tx_hash.hex(), event_logs = event_logs, qr_code=qr_code)
        elif  request.form.get('action2') == 'VALUE2':
            isCard  = True
            dr_id = form.add_doctors.data
            result = "Patient added a doctor to audit their medical records."

            ################## Solidity Transaction ###################
            #find deployed contract
            contract = web3.eth.contract(address = contract_address, abi = abi)
            # assign default address
            web3.eth.default_account = account_address
            tx_hash  = contract.functions.addDoctors(dr_id).transact()
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            event_logs = contract.events.event_add_doctor.get_logs()
#             changes = filter.get_new_entries()
            print("--------------------changes-------------")
            print(event_logs[0]['args']['return_msg'])
            print("--------------------end changes-------------")
#             print(tx_receipt)
#             contract.functions.record_mapping()
            ################## End Solidity TRansaction ###############
            return render_template("patient.html", form=form, isCard  = isCard, username=account_address,contract_address=contract_address, result=result, tx_receipt = tx_receipt, tx_hash=tx_hash.hex(), event_logs = event_logs)
        elif  request.form.get('action3') == 'VALUE3':
            isCard  = True
            dr_id = form.remove_doctors.data
            result = "Patient removed a doctor to audit their medical records."

            ################## Solidity Transaction ###################
            #find deployed contract
            contract = web3.eth.contract(address = contract_address, abi = abi)
            # assign default address
            web3.eth.default_account = account_address
            tx_hash  = contract.functions.removeDoctors(dr_id).transact()
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            event_logs = contract.events.event_remove_doctor.get_logs()
#             changes = filter.get_new_entries()
            print("--------------------changes-------------")
            print(event_logs)
            print("--------------------end changes-------------")
#             print(tx_receipt)
#             contract.functions.record_mapping()
            ################## End Solidity TRansaction ###############
            return render_template("patient.html", form=form, isCard  = isCard, username=account_address,contract_address=contract_address, result=result, tx_receipt = tx_receipt, tx_hash=tx_hash.hex(), event_logs = event_logs)
        elif  request.form.get('action4') == 'VALUE4':
            isCard  = True
            audit_id = form.add_audits.data
            result = "Patient added an audit to view/change their medical records."

            ################## Solidity Transaction ###################
            #find deployed contract
            contract = web3.eth.contract(address = contract_address, abi = abi)
            # assign default address
            web3.eth.default_account = account_address
            tx_hash  = contract.functions.addAudit(audit_id).transact()
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            event_logs = contract.events.event_add_audit.get_logs()

            print("--------------------changes-------------")
            print(event_logs)
            print("--------------------end changes-------------")

            ################## End Solidity TRansaction ###############
            return render_template("patient.html", form=form, isCard  = isCard, username=account_address,contract_address=contract_address, result=result, tx_receipt = tx_receipt, tx_hash=tx_hash.hex(), event_logs = event_logs)

        elif  request.form.get('action5') == 'VALUE5':
            isCard  = True
            audit_id = form.remove_audits.data
            result = "Patient removed an audit to prohibit view/change their medical records."

            ################## Solidity Transaction ###################
            #find deployed contract
            contract = web3.eth.contract(address = contract_address, abi = abi)
            # assign default address
            web3.eth.default_account = account_address
            tx_hash  = contract.functions.removeAudit(audit_id).transact()
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            event_logs = contract.events.event_remove_audit.get_logs()

            print("--------------------changes-------------")
            print(event_logs)
            print("--------------------end changes-------------")

            ################## End Solidity TRansaction ###############
            return render_template("patient.html", form=form, isCard  = isCard, username=account_address,contract_address=contract_address, result=result, tx_receipt = tx_receipt, tx_hash=tx_hash.hex(), event_logs = event_logs)


        elif  request.form.get('action6') == 'VALUE6':
            isCard  = True
            unique_id = form.print_record.data
            unique_id = unique_id.strip().lower()
            if not Web3.is_address(unique_id):
                return render_template("patient.html", form=form, isCard=True, username=account_address, contract_address=contract_address, result="Error: Invalid Record ID format. Please enter a valid Ethereum address.", tx_hash="")
            unique_id = Web3.to_checksum_address(unique_id)
            result = "Patient printed their medical records."

            ################## Solidity Transaction ###################
            #find deployed contract
            contract = web3.eth.contract(address = contract_address, abi = abi)
            # assign default address
            web3.eth.default_account = account_address
            tx_hash  = contract.functions.print_record(unique_id).transact()
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            event_logs = contract.events.event_patient_print.get_logs()
            print("--------------------changes-------------")
            print(event_logs)
            print("--------------------end changes-------------")

            # get medical record details
            try:
                raw_record = contract.functions.get_record_details(unique_id).call()
                record_details, ipfs_source, is_binary, ipfs_cid = fetch_from_ipfs(raw_record)
            except Exception as e:
                print(f"Contract call failed: {e}")
                record_details = "Error: Could not retrieve record. It may not exist or you may not have permission."
                ipfs_cid = None
                ipfs_source = None
                is_binary = False
            
            return render_template("patient.html", form=form, isCard=isCard, username=account_address, contract_address=contract_address, result=result, tx_receipt=tx_receipt, tx_hash=tx_hash.hex(), event_logs=event_logs, record_details=record_details, ipfs_cid=ipfs_cid, ipfs_source=ipfs_source, ipfs_gateway_url=IPFS_GATEWAY_URL, is_binary=is_binary)

        elif  request.form.get('action7') == 'VALUE7':
            isCard  = True
            unique_id = form.delete_record.data
            unique_id = unique_id.strip().lower()
            if not Web3.is_address(unique_id):
                return render_template("patient.html", form=form, isCard=True, username=account_address, contract_address=contract_address, result="Error: Invalid Record ID format. Please enter a valid Ethereum address.", tx_hash="")
            unique_id = Web3.to_checksum_address(unique_id)
            result = "Patient deleted their medical record."

            ################## Solidity Transaction ###################
            #find deployed contract
            contract = web3.eth.contract(address = contract_address, abi = abi)
            # assign default address
            web3.eth.default_account = account_address
            tx_hash  = contract.functions.delete_record(unique_id).transact()
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            event_logs = contract.events.event_patient_delete.get_logs()
            print("--------------------changes-------------")
            print(event_logs)
            print("--------------------end changes-------------")

            ################## End Solidity TRansaction ###############
            return render_template("patient.html", form=form, isCard  = isCard, username=account_address,contract_address=contract_address, result=result, tx_receipt = tx_receipt, tx_hash=tx_hash.hex(), event_logs = event_logs)
        else:
            pass # unknown
    return render_template('patient.html', form=form, isCard  = isCard, username=account_address,contract_address=contract_address )

@app.route('/audit', methods=['GET', 'POST'])
def auditdash():
    account_address  = request.args.get("address")
    contract_address = request.args.get("contract")
    form = AuditActions(request.form)
    if request.method == 'POST':
        print("====== AUDIT DASH POST ======")
        print("request.form:", request.form)
        print("action10:", request.form.get('action10'))
        print("form.contract_address.data:", form.contract_address.data)
        if request.form.get('action10') == 'VALUE10':
            contract_address  = form.contract_address.data
            return redirect('audit?'+"address=" + str(account_address) + "&contract=" + str(form.contract_address.data) )
        if request.form.get('action1') == 'VALUE1':
            print("-------------contract address  = " +contract_address)
            isCard  = True
            unique_id = form.print_record.data
            unique_id = unique_id.strip().lower()
            if not Web3.is_address(unique_id):
                return render_template("audit.html", form=form, isCard=True, username=account_address, contract_address=contract_address, result="Error: Invalid Record ID format. Please enter a valid Ethereum address.", tx_hash="")
            unique_id = Web3.to_checksum_address(unique_id)
            result = "Audit printed patient medical records."

            ################## Solidity Transaction ###################
            #find deployed contract
            contract = web3.eth.contract(address = contract_address, abi = abi)
            # assign default address
            web3.eth.default_account = account_address
            try:
                tx_hash  = contract.functions.doctor_print_record(unique_id).transact()
                tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            except Exception as e:
                print(f"Transaction failed: {e}")
                return render_template("audit.html", form=form, isCard=True, username=account_address, contract_address=contract_address, result=f"Error: Transaction failed. {e}")
            
            event_logs = contract.events.event_doctor_print.get_logs()
            print("--------------------changes-------------")
            print(event_logs)
            print("--------------------end changes-------------")

            # get medical record details
            try:
                raw_record = contract.functions.get_record_details(unique_id).call()
                record_details, ipfs_source, is_binary, ipfs_cid = fetch_from_ipfs(raw_record)
            except Exception as e:
                print(f"Contract call failed: {e}")
                record_details = "Error: Could not retrieve record. It may not exist or you may not have permission."
                ipfs_cid = None
                ipfs_source = None
                is_binary = False
            
            return render_template("audit.html", form=form, isCard=isCard, username=account_address, contract_address=contract_address, result=result, tx_receipt=tx_receipt, tx_hash=tx_hash.hex(), event_logs=event_logs, record_details=record_details, ipfs_cid=ipfs_cid, ipfs_source=ipfs_source, ipfs_gateway_url=IPFS_GATEWAY_URL, is_binary=is_binary)

        elif  request.form.get('action2') == 'VALUE2':
            isCard  = True
            unique_id = form.update_record_id.data
            unique_id = unique_id.strip().lower()
            if not Web3.is_address(unique_id):
                return render_template("audit.html", form=form, isCard=True, username=account_address, contract_address=contract_address, result="Error: Invalid Record ID format. Please enter a valid Ethereum address.")
            unique_id = Web3.to_checksum_address(unique_id)
            result = "Audit updated patient medical records."
            new_record = form.update_record_rec.data
            ################## Solidity Transaction ###################
            #find deployed contract
            contract = web3.eth.contract(address = contract_address, abi = abi)
            web3.eth.default_account = account_address
            # Check if file was also uploaded via IPFS file upload
            uploaded_file = request.files.get('ipfs_file')
            if uploaded_file and uploaded_file.filename:
                file_bytes = uploaded_file.read()
                ipfs_cid = upload_to_ipfs(file_bytes)
                if ipfs_cid:
                    # Store both: Text + CID in a formatted string
                    record_to_store = f"{new_record} | IPFS_CID:{ipfs_cid}"
                else:
                    record_to_store = new_record
            else:
                # No file, just check if text should go to IPFS or chain
                ipfs_cid = upload_to_ipfs(new_record)
                record_to_store = ipfs_cid if ipfs_cid else new_record

            record_to_store = record_to_store.strip()
            print(f"DEBUG: Saving to Blockchain: '{record_to_store}'")

            try:
                tx_hash  = contract.functions.doctor_update_record(unique_id, record_to_store).transact()
                tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            except Exception as e:
                print(f"Transaction failed: {e}")
                return render_template("audit.html", form=form, isCard=True, username=account_address, contract_address=contract_address, result=f"Error: Transaction failed. {e}", tx_hash="")
            
            event_logs = contract.events.event_doctor_update.get_logs()
            print("--------------------changes-------------")
            print(event_logs)
            print("--------------------end changes-------------")

            ipfs_upload_success = bool(ipfs_cid)
            try:
                raw_record = contract.functions.get_record_details(unique_id).call()
                # fetch_from_ipfs now returns (display_text, source, is_binary, actual_cid)
                record_details, ipfs_source, is_binary, ipfs_cid = fetch_from_ipfs(raw_record)
            except Exception as e:
                print(f"Contract call failed: {e}")
                record_details = "Error: Record updated on blockchain, but could not be verified/retrieved. Check authorization."
                ipfs_cid = None
                ipfs_source = None
                is_binary = False

            # Auto-trigger FL local training for the hospital that updated this record
            fl_hospital = request.form.get("fl_hospital", "Hospital_A")
            try:
                from federated.fl_routes import HOSPITALS, load_state, save_state, save_model_file
                from federated.local_trainer import generate_hospital_data, train_local_model
                from sklearn.model_selection import train_test_split
                fl_state = load_state()
                if fl_hospital in HOSPITALS and fl_hospital not in fl_state["trained"]:
                    seed = HOSPITALS.index(fl_hospital) * 100
                    X, y = generate_hospital_data(fl_hospital, seed=seed)
                    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.25, random_state=42)
                    model, scaler = train_local_model(X_train, y_train)
                    save_model_file(fl_hospital, model, scaler)
                    fl_state["trained"].append(fl_hospital)
                    save_state(fl_state)
                    print(f"[FL] Auto-trained {fl_hospital} after record update. Trained so far: {fl_state['trained']}")
            except Exception as fl_err:
                print(f"[FL] Auto-train skipped: {fl_err}")

            return render_template("audit.html", form=form, isCard=isCard, username=account_address, contract_address=contract_address, result=result, tx_receipt=tx_receipt, tx_hash=tx_hash.hex(), event_logs=event_logs, record_details=record_details, ipfs_cid=ipfs_cid, ipfs_upload_success=ipfs_upload_success, ipfs_source=ipfs_source, ipfs_gateway_url=IPFS_GATEWAY_URL, is_binary=is_binary)

        elif  request.form.get('action3') == 'VALUE3':
            isCard  = True
            unique_id = form.query.data
            unique_id = unique_id.strip().lower()
            if not Web3.is_address(unique_id):
                return render_template("audit.html", form=form, isCard=True, username=account_address, contract_address=contract_address, result="Error: Invalid Record ID format. Please enter a valid Ethereum address.", tx_hash="")
            unique_id = Web3.to_checksum_address(unique_id)
            result = "Audit queried one of the patient medical records."

            ################## Solidity Transaction ###################
            #find deployed contract
            contract = web3.eth.contract(address = contract_address, abi = abi)
            # assign default address
            web3.eth.default_account = account_address
            try:
                tx_hash  = contract.functions.doctor_query_record(unique_id).transact()
                tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            except Exception as e:
                print(f"Transaction failed: {e}")
                return render_template("audit.html", form=form, isCard=True, username=account_address, contract_address=contract_address, result=f"Error: Transaction failed. {e}", tx_hash="")
            
            event_logs = contract.events.event_doctor_query.get_logs()
            print("--------------------changes-------------")
            print(event_logs)
            print("--------------------end changes-------------")

            # get medical record details
            try:
                raw_record = contract.functions.get_record_details(unique_id).call()
                record_details, ipfs_source, is_binary, ipfs_cid = fetch_from_ipfs(raw_record)
            except Exception as e:
                print(f"Contract call failed: {e}")
                record_details = "Error: Could not retrieve record. It may not exist or you may not have permission."
                ipfs_cid = None
                ipfs_source = None
                is_binary = False
            
            ################## End Solidity TRansaction ###############
            return render_template("audit.html", form=form, isCard=isCard, username=account_address, contract_address=contract_address, result=result, tx_receipt=tx_receipt, tx_hash=tx_hash.hex(), event_logs=event_logs, record_details=record_details, ipfs_cid=ipfs_cid, ipfs_source=ipfs_source, ipfs_gateway_url=IPFS_GATEWAY_URL, is_binary=is_binary)

        elif  request.form.get('action30') == 'VALUE30':
            fname = hashlib.sha224(b"uniqueid_data").hexdigest()
            df = pd.read_csv('data/'+fname+'.csv')
            print(df)
            token3 = df.applymap(lambda x: bytes(x[2:-1],'utf-8'))
            token4 = token3.applymap(lambda x: fernet.decrypt(x))
            decrypted_df = token4.applymap(lambda x: x.decode('utf-8'))
            print(decrypted_df)
            filtered_df = decrypted_df[decrypted_df['contract_address']==contract_address]
            filtered_dict = filtered_df.to_dict()
            print(filtered_dict)
            return render_template("audit.html", form=form, username=account_address,contract_address=contract_address,isDF = True, filtered_df=filtered_df)
        elif  request.form.get('action4') == 'VALUE4':
            isCard  = True
            unique_id = form.copy_record.data
            unique_id = unique_id.strip().lower()
            if not Web3.is_address(unique_id):
                return render_template("audit.html", form=form, isCard=True, username=account_address, contract_address=contract_address, result="Error: Invalid Record ID format. Please enter a valid Ethereum address.", tx_hash="")
            unique_id = Web3.to_checksum_address(unique_id)
            result = "Audit copied patient medical records."

            ################## Solidity Transaction ###################
            #find deployed contract
            contract = web3.eth.contract(address = contract_address, abi = abi)
            # assign default address
            web3.eth.default_account = account_address
            try:
                tx_hash  = contract.functions.doctor_copy_record(unique_id).transact()
                tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            except Exception as e:
                print(f"Transaction failed: {e}")
                return render_template("audit.html", form=form, isCard=True, username=account_address, contract_address=contract_address, result=f"Error: Transaction failed. {e}", tx_hash="")
            
            event_logs = contract.events.event_doctor_copy.get_logs()
            print("--------------------changes-------------")
            print(event_logs)
            print("--------------------end changes-------------")

            # get medical record details
            try:
                raw_record = contract.functions.get_record_details(unique_id).call()
                record_details, ipfs_source, is_binary, ipfs_cid = fetch_from_ipfs(raw_record)
            except Exception as e:
                print(f"Contract call failed: {e}")
                record_details = "Error: Could not retrieve record. It may not exist or you may not have permission."
                ipfs_cid = None
                ipfs_source = None
                is_binary = False
            
            ################## End Solidity TRansaction ###############
            return render_template("audit.html", form=form, isCard=isCard, username=account_address, contract_address=contract_address, result=result, tx_receipt=tx_receipt, tx_hash=tx_hash.hex(), event_logs=event_logs, record_details=record_details, ipfs_cid=ipfs_cid, ipfs_source=ipfs_source, ipfs_gateway_url=IPFS_GATEWAY_URL, is_binary=is_binary)
        elif  request.form.get('action5') == 'VALUE5':
            isCard  = True
            unique_id = form.delete_record.data
            unique_id = unique_id.strip().lower()
            if not Web3.is_address(unique_id):
                return render_template("audit.html", form=form, isCard=True, username=account_address, contract_address=contract_address, result="Error: Invalid Record ID format. Please enter a valid Ethereum address.", tx_hash="")
            unique_id = Web3.to_checksum_address(unique_id)
            result = "Audit deleted patient medical records."

            ################## Solidity Transaction ###################
            #find deployed contract
            contract = web3.eth.contract(address = contract_address, abi = abi)
            # assign default address
            web3.eth.default_account = account_address
            tx_hash  = contract.functions.doctor_delete_record(unique_id).transact()
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            event_logs = contract.events.event_doctor_delete.get_logs()
            print("--------------------changes-------------")
            print(event_logs)
            print("--------------------end changes-------------")

            ################## End Solidity TRansaction ###############
            return render_template("audit.html", form=form, isCard  = isCard, username=account_address,contract_address=contract_address, result=result, tx_receipt = tx_receipt, tx_hash=tx_hash.hex(), event_logs = event_logs)

        else:
            pass # unknown
    return render_template('audit.html', form=form, username=account_address, contract_address=contract_address)


if __name__ == '__main__':
    # add ssl certificate
    app.run(ssl_context='adhoc')
