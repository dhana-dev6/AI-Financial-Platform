import random
from datetime import datetime, timedelta

def get_mock_bank_data(bank_name):
    """
    Simulates fetching data from a banking API.
    Returns balance and recent transactions.
    """
    # Simulate realistic balance for an SME
    main_balance = random.randint(50000, 500000) 
    
    # Generate random transactions for the last 30 days
    transactions = []
    today = datetime.now()
    
    descriptions = [
        ("Client Payment - inv#2023", "Revenue"),
        ("AWS Service Charge", "Software"), 
        ("Office Rent", "Operational"),
        ("Staff Payroll", "Payroll"),
        ("Vendor Payment - Supplies", "COGS"),
        ("Interest Credit", "Other"),
        ("Utility Bill", "Operational")
    ]
    
    for i in range(10):
        days_ago = random.randint(0, 30)
        date = (today - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        desc, cat = random.choice(descriptions)
        
        # Decide amount based on category (rough logic)
        if cat == "Revenue":
            amount = random.randint(1000, 20000)
        elif cat == "Payroll":
             amount = -random.randint(5000, 15000)
        else:
             amount = -random.randint(100, 5000)
             
        transactions.append({
            "date": date,
            "description": desc,
            "amount": amount,
            "category": cat
        })
        
    # Sort by date desc
    transactions.sort(key=lambda x: x['date'], reverse=True)
    
    return {
        "bank_name": bank_name,
        "account_id": f"XX-{random.randint(1000,9999)}",
        "current_balance": main_balance,
        "currency": "USD",
        "transactions": transactions
    }
