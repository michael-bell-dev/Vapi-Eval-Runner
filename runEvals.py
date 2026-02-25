import os
import time
import requests
from dotenv import load_dotenv
import json
import csv
import sys

# Load variables from .env
load_dotenv()

# --- Configuration ---
API_KEY = os.getenv("VAPI_API_KEY")

BASE_URL = "https://api.vapi.ai/eval"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def run_single_eval(eval_id, agent_id, is_squad):
    """
    Run a single evaluation and return the run_id and status
    """
    target_type = "squad" if is_squad else "assistant"
    target_key = "squadId" if is_squad else "assistantId"
    
    payload = {
        "type": "eval",
        "evalId": eval_id,
        "target": {
            "type": target_type,
            target_key: agent_id
        }
    }

    response = requests.post(f"{BASE_URL}/run", headers=HEADERS, json=payload)
    
    if response.status_code == 429:
        time.sleep(60)
        return run_single_eval(eval_id, agent_id, is_squad)
    
    if response.status_code not in [200, 201]:
        return None, "error"

    run_data = response.json()
    run_id = run_data.get("evalRunId")
    
    if not run_id:
        return None, "error"
    
    # Poll for results
    max_attempts = 40
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        time.sleep(10)
        
        status_res = requests.get(f"{BASE_URL}/run/{run_id}", headers=HEADERS)
        
        if status_res.status_code == 429:
            time.sleep(60)
            continue
        
        if status_res.status_code != 200:
            break
            
        data = status_res.json()
        status = data.get("status")
        
        if status in ["completed", "ended"]:
            # Check if all eval cases passed
            results = data.get("results", [])
            all_passed = all(result.get("status") == "pass" for result in results)
            return run_id, "pass" if all_passed else "fail"
        elif status == "failed":
            return run_id, "fail"
    
    return run_id, "timeout"

def load_evals_from_csv(filename):
    """
    Load eval configurations from CSV file
    Expected format: name, eval_id, agent_id, is_squad, enabled
    """
    evals = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if len(row) >= 5:
                name = row[0]
                eval_id = row[1]
                agent_id = row[2]
                is_squad = row[3].lower() in ['true', '1', 'yes']
                enabled = row[4].lower() in ['true', '1', 'yes']
                
                # Only add evals that are enabled
                if enabled:
                    evals.append((name, eval_id, agent_id, is_squad))
    return evals

if __name__ == "__main__":
    numTrials = 3

    # Check if CSV file path is provided
    if len(sys.argv) < 2:
        print("Usage: python run_vapi_evals.py <path_to_evals.csv>")
        print("Example: python run_vapi_evals.py evals.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"❌ Error: File '{csv_file}' not found")
        sys.exit(1)
    
    # Load evals from CSV file
    evals = load_evals_from_csv(csv_file)
    
    if not evals:
        print(f"⚠️ No enabled evals found in '{csv_file}'")
        sys.exit(0)
    
    print(f"{'='*60}")
    print(f"Running {len(evals)} evals, {numTrials} times each")
    print(f"{'='*60}\n")
    
    for name, eval_id, agent_id, is_squad in evals:
        print(f"📋 {name}")
        
        for run_num in range(1, numTrials + 1):
            run_id, status = run_single_eval(eval_id, agent_id, is_squad)
            
            status_emoji = "✅" if status == "pass" else "❌"
            if run_id:
                print(f"   Run {run_num}: {status_emoji} {status.upper()} (ID: {run_id})")
            else:
                print(f"   Run {run_num}: {status_emoji} {status.upper()}")
        
        print()  # Blank line between evals
    
    print(f"{'='*60}")
    print("🎉 All evaluations complete!")
    print(f"{'='*60}")