from gst_parser import parse_gstr1
import pandas as pd
import json

try:
    with open('../file.json', 'rb') as f:
        content = f.read()

    print("Parsing file.json...")
    df = parse_gstr1(content)
    
    print("\nDataFrame Info:")
    print(df.info())
    print("\nHead:")
    print(df.head())

    # Simulate Main.py Logic
    # Normalize
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Calculate Metrics
    if 'amount' in df.columns:
        total_revenue = float(df[df['amount'] > 0]['amount'].sum())
        total_expenses = float(abs(df[df['amount'] < 0]['amount'].sum()))
        net_profit = float(total_revenue - total_expenses)
        print(f"\nMetrics: Rev={total_revenue}, Exp={total_expenses}, Profit={net_profit}")
    else:
        print("\nERROR: 'amount' column missing!")

except Exception as e:
    print(f"\nCRITICAL ERROR: {e}")
