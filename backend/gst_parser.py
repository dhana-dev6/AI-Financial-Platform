import json
import pandas as pd

def parse_gstr1(file_bytes):
    """
    Parses a GSTR-1 JSON file and returns a DataFrame of B2B invoices.
    Also calculates total turnover from the payload.
    """
    try:
        data = json.loads(file_bytes.decode('utf-8'))
        
        # Helper to extract invoices
        # GSTR-1 Structure roughly: data['b2b'] -> list of invoices
        
        invoices = []
        
        # 1. B2B Invoices (Business to Business)
        if 'b2b' in data:
            for entry in data['b2b']:
                for inv in entry.get('inv', []):
                    # inv['idt'] = Invoice Date
                    # inv['val'] = Total Invoice Value
                    invoices.append({
                        'date': inv.get('idt', 'Unknown'),
                        'description': f"GST Inv#{inv.get('inum', 'NA')} (B2B)",
                        'amount': float(inv.get('val', 0)),
                        'category': 'Revenue' # Verified Revenue
                    })
                    
        # 2. B2CS (Business to Consumer Small) - usually aggregated
        if 'b2cs' in data:
             for entry in data['b2cs']:
                 # entry['txval'] = Taxable Value
                 invoices.append({
                     'date': 'Monthly Agg.',
                     'description': "GST B2CS Aggregated Sales",
                     'amount': float(entry.get('txval', 0)),
                     'category': 'Revenue'
                 })

        if not invoices:
            # Fallback for mock data if structure is different
            print("GST Parser: No standard invoice keys found. Returning empty.")
            return pd.DataFrame()

        df = pd.DataFrame(invoices)
        df['amount'] = pd.to_numeric(df['amount'])
        
        # Sort by date if possible (dd-mm-yyyy format usually in GST)
        try:
            # Normalize to datetime first to ensure validity
            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce').fillna(pd.Timestamp.now())
            # Convert back to string for JSON serialization
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        except:
            df['date'] = df['date'].astype(str)
            
        return df

    except Exception as e:
        print(f"GST Parsing Error: {e}")
        return pd.DataFrame()
