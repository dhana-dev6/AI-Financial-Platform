from banking_mock import get_mock_bank_data
import json

try:
    data = get_mock_bank_data("HDFC")
    print("KEYS:", data.keys())
    print("TRANSACTIONS TYPE:", type(data.get("transactions")))
    print("FIRST TRANSACTION:", data.get("transactions")[0] if data.get("transactions") else "NONE")
    # print(json.dumps(data, indent=2))
except Exception as e:
    print(f"ERROR: {e}")
