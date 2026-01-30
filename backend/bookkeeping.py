import pandas as pd

# Standard SME Categories
CATEGORIES = {
    "Operational": ["rent", "utility", "electricity", "water", "internet", "phone", "office", "repair", "maintenance", "cleaning"],
    "Payroll": ["salary", "wages", "contractor", "consultant", "payroll", "bonus", "hiring"],
    "Marketing": ["ads", "advertising", "facebook", "google", "marketing", "promo", "campaign", "social media", "seo"],
    "Software": ["aws", "azure", "google cloud", "software", "subscription", "zoom", "slack", "microsoft", "adobe", "saas"],
    "Travel & Meals": ["uber", "lyft", "taxi", "flight", "hotel", "airbnb", "travel", "meal", "food", "restaurant", "dinner", "lunch"],
    "COGS": ["inventory", "raw material", "freight", "shipping", "goods", "supplier", "purchase order"],
    "Taxes": ["tax", "gst", "vat", "irs", "gov", "audit"],
    "Financial": ["bank", "fee", "interest", "insurance", "loan", "credit card"]
}

def auto_categorize(df):
    """
    Categorizes transactions based on description keywords.
    Handles 'Description' vs 'description' column case sensitivity.
    """
    try:
        # 0. Standardize Columns to lowercase
        df.columns = df.columns.str.lower().str.strip()
        
        # Check required columns
        if 'description' not in df.columns or 'amount' not in df.columns:
            print("Bookkeeping Error: Missing 'description' or 'amount' columns.")
            return None

        # Helper function
        def classify(desc, amount):
            if amount > 0:
                return "Revenue"
            desc = str(desc).lower()
            for cat, keywords in CATEGORIES.items():
                for kw in keywords:
                    if kw in desc:
                        return cat
            return "Miscellaneous"

        # Apply classification
        df['category'] = df.apply(lambda x: classify(x.get('description', ''), x.get('amount', 0)), axis=1)
        
        # 1. Expense Breakdown (amount < 0)
        expense_df = df[df['amount'] < 0].copy()
        if not expense_df.empty:
            expense_df['abs_amount'] = expense_df['amount'].abs()
            breakdown = expense_df.groupby('category')['abs_amount'].sum().reset_index()
            breakdown_list = breakdown.rename(columns={'abs_amount': 'value', 'category': 'name'}).to_dict('records')
        else:
            breakdown_list = []
        
        # 2. Recent Transactions (Top 20)
        # Ensure 'date' exists
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            recent_df = df.dropna(subset=['date']).sort_values('date', ascending=False).head(20).copy()
            recent_df['date'] = recent_df['date'].dt.strftime('%Y-%m-%d')
            recent_transactions = recent_df[['date', 'description', 'amount', 'category']].to_dict('records')
        else:
             # Fallback if no date column
             recent_transactions = df.head(20)[['description', 'amount', 'category']].to_dict('records')
             for t in recent_transactions: t['date'] = 'N/A'

        return {
            "breakdown": breakdown_list,
            "recent_transactions": recent_transactions
        }

    except Exception as e:
        print(f"Bookkeeping Error: {e}")
        return None