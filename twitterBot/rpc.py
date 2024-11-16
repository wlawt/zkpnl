import subprocess
from web3 import Web3
from pathlib import Path
from os.path import join as path_join
import json
import hashlib

rpc_url = "https://zircuit1-testnet.p2pify.com"
w3 = Web3(Web3.HTTPProvider(rpc_url))

def create_contract(w3, addr):
    root = str(Path(__file__).parent.parent.absolute())
    j = path_join(root, "contracts/out", "ProofVerifier.sol", "ProofVerifier.json")
    with open(j) as f:
        abi = json.load(f)["abi"]
    return w3.eth.contract(address=addr, abi=abi)

def invoke_contract(w3, contract, method, args, sender_pk, chain_id=48899, gas=2e6):
    sender_addr = w3.eth.account.from_key(sender_pk).address
    txn = contract.functions[method](*args).build_transaction({
        'from': sender_addr,
        # 'gas': int(gas),
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(sender_addr),
        'chainId': chain_id
    })
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=sender_pk)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash, tx_receipt

def get_method(contract, method, args):
    return contract.functions[method](*args).call()

def post_to_sc(proof_hash):
    contract_address = "0xCC497f66EBE70Fd4f8757287E800DD5DDc467848"
    contract = create_contract(w3, contract_address)
    tx_hash, tx_receipt = invoke_contract(
        w3,
        contract, "addProofHash", [hashlib.sha256(proof_hash.encode()).digest()],
        "0xd0e14fb3701cf1440a3ab7982148ab6ac24628ca6b203714c7fa7c68b6422bf2",
    )
    return f"https://explorer.testnet.zircuit.com/tx/0x{tx_receipt['transactionHash'].hex()}"

def run_rust_exe(exe_path, *args):
    try:
        # Run the Rust executable and pass command-line arguments
        result = subprocess.run(
            [exe_path, *map(str, args)],  # Convert all args to strings
            stdout=subprocess.PIPE,      # Capture standard output
            stderr=subprocess.PIPE,      # Capture standard error
            text=True,                   # Return output as string
            check=True                   # Raise an exception on non-zero exit
        )
        return result.stdout.strip()  # Return the output
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.strip()}")
        return None

def call_zk(entry, current, pnl, lev):
    exe_path = "./host"  # Replace with the path to your Rust executable
    args = [entry, current, pnl, lev]          # Arguments to pass to the Rust executable

    output = run_rust_exe(exe_path, *args)
    if "proof hash:" in output:
        return output.split("proof hash:")[1].strip()

    return None
    


if __name__ == "__main__":
    proof_hash_to_post = call_zk(100.0, 120.0, 20.0, 1)
    if proof_hash_to_post:
        print(post_to_sc(proof_hash_to_post))
    else:
        print("Error: Could not generate proof hash")