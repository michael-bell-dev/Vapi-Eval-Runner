# Vapi Eval Runner

A simple Python CLI tool for running and monitoring VAPI evaluations in bulk using a CSV configuration file.

This script runs multiple evals simultaneously and supports both assistants and squads. 

## Instalation/Requirements
- Download runEvals.py
- pip install requests python-dotenv
- Create a .env file in the same directory:  
VAPI_API_KEY=your_api_key_here
- CSV file in the following format:  
name,eval_id,agent_id,is_squad,enabled

name     - Friendly name for the eval  
eval_id  - The VAPI eval ID  
agent_id - Assistant ID or Squad ID  
is_squad - true if using squad, false if assistant  
enabled  - true to run, false to skip  

## Usage
python runEvals.py evals.csv

## Example Output
============================================================
Running 2 evals, 3 times each
============================================================

📋 Greeting Test
   Run 1: ✅ PASS (ID: run_abc123)
   Run 2: ❌ FAIL (ID: run_def456)
   Run 3: ✅ PASS (ID: run_xyz789)

📋 Sales Squad Test
   Run 1: ✅ PASS (ID: run_111222)
   Run 2: ✅ PASS (ID: run_333444)
   Run 3: ✅ PASS (ID: run_555666)

============================================================
🎉 All evaluations complete!
============================================================
