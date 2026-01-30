import urllib.request
import urllib.parse
import json

url = "http://127.0.0.1:8000/analyze"

# Manually construct multipart form data (simplified)
# Actually, urllib is hard for multipart. Let's just use curl and print to stdout then parse manually in python?
# Or just use the existing curl command and LOOK at the output in the terminal manually?
# No, I want to script it.
# Let's try to install requests quickly. It's standard.
# Or better: check if `httpx` is installed (FastAPI often uses it).
# Let's just try to install requests.

import sys
import subprocess
try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

# Mock CSV content
csv_content = """Date,Description,Amount
2023-01-01,Sales,5000
2023-01-02,Rent,-1000
"""

files = {
    'file': ('test.csv', csv_content, 'text/csv')
}
data = {
    'company_name': 'Test Corp',
    'industry': 'Retail',
    'language': 'Hindi'
}

print("Sending request to backend...")
try:
    response = requests.post(url, files=files, data=data)
    print(f"Status Code: {response.status_code}")
    print("Response Text Preview:", response.text[:200])
    
    if response.status_code == 200:
        json_resp = response.json()
        raw_ai = json_resp.get('ai_analysis')
        print("\nAI Analysis Raw:")
        print(raw_ai)
        
        try:
             parsed = json.loads(raw_ai)
             print("\nExecutive Summary:")
             print(parsed.get('executive_summary'))
        except:
             print("Could not parse AI JSON")
except Exception as e:
    print(f"Request Error: {e}")
