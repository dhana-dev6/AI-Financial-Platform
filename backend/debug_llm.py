import os
from dotenv import load_dotenv
load_dotenv()

try:
    from main import analyze_with_llm
    
    print(f"API KEY Loaded: {'Yes' if os.getenv('OPENROUTER_API_KEY') else 'No'}")
    
    dummy_summary = {
        "Total Revenue": 100000,
        "Total Expenses": 50000,
        "Net Profit": 50000,
        "Profit Margin": "50.00%",
        "Industry": "Retail",
        "Company": "Test Corp"
    }

    print("Attempting to call LLM...")
    result = analyze_with_llm(dummy_summary)
    print("\nResult:")
    print(result)

except Exception as e:
    print(f"\nCRITICAL FAILURE: {e}")
