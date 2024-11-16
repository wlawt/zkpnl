from typing import List, Dict
from rpc import call_zk


def verify_data(trade_data_array: List[Dict]) -> str:
    """
    Verifies trade data using ZK proofs and returns a hash if all trades are valid.
    
    Args:
        trade_data_array: List of dictionaries containing trade data
        
    Returns:
        str: Hash from a verified trade if all trades are valid, empty string if any verification fails
    """
    verification_results = []
    
    for trade_data in trade_data_array:
        try:
            # Extract values from trade data
            entry = float(trade_data['entry'])
            exit_price = float(trade_data['exit'])
            percentage = float(trade_data['percentage'])
            leverage = int(trade_data['leverage'])
            
            # Call ZK proof generation
            proof_hash = call_zk(entry, exit_price, percentage, leverage)
            
            if proof_hash:
                print(f"Trade verified with hash: {proof_hash}")
                verification_results.append({
                    'verified': True,
                    'hash': proof_hash
                })
            else:
                print(f"Failed to verify trade: {trade_data}")
                verification_results.append({
                    'verified': False,
                    'hash': None
                })
                
        except Exception as e:
            print(f"Error processing trade data: {e}")
            print(f"Problematic trade data: {trade_data}")
            verification_results.append({
                'verified': False,
                'hash': None
            })
    
    # Check if all trades were verified
    all_verified = all(result['verified'] for result in verification_results)
    
    if all_verified and verification_results:
        # Return hash from first verified trade
        # We could return any hash since all are verified
        return verification_results[0]['hash']
    else:
        print("Verification failed: Not all trades could be verified")
        # Print which trades failed
        for i, result in enumerate(verification_results):
            if not result['verified']:
                print(f"Trade {i + 1} failed verification")
        return ""

# Example usage:

trade_data = [
    {"entry": 211.15, "exit": 220.37, "percentage": 334.68, "leverage": 80},
    {"entry": 100.0, "exit": 120.0, "percentage": 20.0, "leverage": 1}
]

final_hash = verify_data(trade_data)
if final_hash:
    print(f"All trades verified successfully. Final hash: {final_hash}")
else:
    print("Verification failed for one or more trades")
