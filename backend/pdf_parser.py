import pandas as pd
from pypdf import PdfReader
import io
import re

def parse_pdf(file_bytes):
    """
    Parses a PDF bank statement and returns a DataFrame.
    """
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
            
        print("DEBUG: Extracted PDF Text Sample:", text[:200]) # For debugging
        
        # Robust Parsing Strategy using Regex
        # Look for lines that look like transactions:
        # Date (YYYY-MM-DD or DD/MM/YYYY) ... Description ... Amount (Positive/Negative)
        
        # Regex for Date: \d{2,4}[-/]\d{1,2}[-/]\d{2,4}
        # Regex for Amount: [-+]?[\d,]+\.\d{2}
        
        transactions = []
        lines = text.split('\n')
        
        date_pattern = re.compile(r'(\d{2,4}[-/]\d{1,2}[-/]\d{2,4})')
        # Amount pattern: looks for numbers with optional commas and a decimal point, possibly negative
        amount_pattern = re.compile(r'([-+]?[\d,]+\.\d{2})') 
        
        for line in lines:
            date_match = date_pattern.search(line)
            amount_matches = amount_pattern.findall(line)
            
            if date_match and amount_matches:
                date_str = date_match.group(1)
                # Take the last match as amount (often balance is last, checking this heuristic)
                # Actually, typically: Date | Desc | Debit | Credit | Balance
                # We need the transaction amount.
                # Let's assume the largest absolute value implies the transaction if multiple numbers exist?
                # Or simplistic: If 1 number -> Amount. If 2 -> Debit/Credit?
                # Let's just grab the last amount found on the line for now, but handle commas
                
                amount_str = amount_matches[-1].replace(',', '')
                try:
                    amount = float(amount_str)
                    
                    # Description: Everything else?
                    # Remove date and amount from line to get description
                    desc = line.replace(date_str, '').replace(amount_matches[-1], '').strip()
                    # Clean up random chars
                    desc = re.sub(r'\s+', ' ', desc)
                    
                    transactions.append({
                        "date": date_str,
                        "description": desc,
                        "amount": amount
                    })
                except:
                    continue

        if not transactions:
            # Fallback for empty parse
            print("PDF Parsing warning: No transactions found with regex.")
            return pd.DataFrame(columns=["date", "description", "amount"])

        df = pd.DataFrame(transactions)
        
        # Standardize Date
        try:
             df['date'] = pd.to_datetime(df['date'])
        except:
             pass # Keep as string if parsing fails
             
        # Standardize Amount (Ensure correct sign logic if possible, or assume user provides signed PDF)
        # Bank statements often have columns for Debit/Credit.
        # This regex parser is naive and assumes signed amounts or single column. 
        # For a hackathon, this is often sufficient or we advise the user on format.
        
        return df

    except Exception as e:
        print(f"PDF Parse Error: {e}")
        return pd.DataFrame()
