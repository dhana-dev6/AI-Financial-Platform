from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import pandas as pd
import io
import io
import os
import json
from dotenv import load_dotenv

load_dotenv()
from openai import OpenAI
from database import SessionLocal, Company, FinancialReport, ComplianceLog
from forecasting import generate_forecast
from bookkeeping import auto_categorize
from tax import calculate_tax
from working_capital import analyze_working_capital
from reports import generate_pdf_report
from fastapi import Response, UploadFile, File, Form, HTTPException
from pdf_parser import parse_pdf
from gst_parser import parse_gstr1
from banking_mock import get_mock_bank_data

app = FastAPI()

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "online", "version": "1.0.1", "message": "Backend is running!"}

# Static Files Mount (Catch-All Moved to Bottom)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize OpenAI (Using OpenRouter for Free Tier)
# Initialize OpenAI (Using OpenRouter for Free Tier)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    default_headers={
        "HTTP-Referer": "http://localhost:5173", # Optional: For OpenRouter rankings
        "X-Title": "SME Financial Health Platform", # Optional: For OpenRouter rankings
    }
)

def analyze_with_llm(financial_summary, language="English"):
    """
    Sends the calculated metrics to OpenAI for detailed, structured analysis.
    """
    prompt = f"""
    You are a high-level Virtual CFO for an SME. 
    Analyze the following financial data:
    {financial_summary}
    
    Output Format: JSON with the following keys (YOU MUST FILL THE VALUES based on the data):
    - "creditworthiness": "High", "Medium", or "Low"
    - "risk_assessment": "A brief paragraph assessing financial risks."
    - "cost_optimization": ["Strategy 1", "Strategy 2"] (List of 2 specific strategies)
    - "executive_summary": "A concise summary of the business health."
    - "recommended_products": ["Product 1", "Product 2"] (e.g., specific bank loans, working capital solutions)

    IMPORTANT: 
    1. Provide the response in the following language: {language}.
    2. Ensure the JSON structure key names remain in English.
    3. generate REAL insights based on the numbers provided. Do not return empty fields or just the keys.
    """
    
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b", # Reliable free model
            messages=[
                {"role": "system", "content": "You are a helpful financial expert assistant that outputs valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        print(f"RAW LLM RESPONSE:\n{content}\n----------------")
        
        # Cleanup
        content = content.replace("```json", "").replace("```", "").strip()
        
        # basic validation
        if 'executive_summary' not in content:
             # Fallback
             data = {
                "creditworthiness": "Unknown",
                "risk_assessment": "Analysis unavailable.",
                "cost_optimization": [],
                "executive_summary": f"Net Profit Margin: {financial_summary.get('Profit Margin', 'N/A')}. Revenue: {financial_summary.get('Total Revenue', '0')}.",
                "recommended_products": []
             }
             content = json.dumps(data)

        return content

    except Exception as e:
        print(f"LLM EXCEPTION: {e}")
        
        error_msg = "Could not generate risk assessment due to AI service disruption."
        summary_msg = f"The business reports a net profit margin of {financial_summary.get('Profit Margin', 'N/A')}. Revenue is {financial_summary.get('Total Revenue', '0')}."
        
        if "429" in str(e) or "Rate limit" in str(e):
             summary_msg += " (Daily Free AI Limit Reached)."
             error_msg = "Daily Free AI Limit Reached. Please try again tomorrow or add credit."
        else:
             summary_msg += " (AI Unavailable)."
        
        # Robust Fallback
        fallback_data = {
            "creditworthiness": "Unknown",
            "risk_assessment": error_msg,
            "cost_optimization": [],
            "executive_summary": summary_msg,
            "recommended_products": []
        }
        return json.dumps(fallback_data)

@app.post("/analyze")
async def analyze_financials(
    file: UploadFile = File(...),
    company_name: str = Form(...),
    industry: str = Form(...),
    language: str = Form("English"),
    db: Session = Depends(get_db)
):
    # 1. Read the File (PDF or CSV)
    try:
        contents = await file.read()
        
        if file.filename.endswith('.pdf'):
            df = parse_pdf(contents)
            if df.empty:
                raise HTTPException(status_code=400, detail="Could not parse PDF. Ensure it contains transaction text.")
        elif file.filename.endswith('.json'):
            # GST Handling
            df = parse_gstr1(contents)
            if df.empty:
                 raise HTTPException(status_code=400, detail="Could not parse JSON. Ensure it is a valid GSTR-1 format.")
        else:
            # CSV Handling
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Normalize column names to lowercase for flexibility
        df.columns = [c.strip().lower() for c in df.columns]
        
        # Map common column names to standard 'amount' and 'date'
        col_map = {
            'amount': 'amount', 'value': 'amount', 'total': 'amount',
            'date': 'date', 'transaction_date': 'date', 'time': 'date',
            'desc': 'description', 'memo': 'description', 'description': 'description'
        }
        
        df = df.rename(columns=col_map)

        if 'amount' not in df.columns:
             raise HTTPException(status_code=400, detail="CSV must contain an 'Amount' or 'Value' column")

        # Clean data
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)

        # Calculate Metrics
        total_revenue = float(df[df['amount'] > 0]['amount'].sum())
        total_expenses = float(abs(df[df['amount'] < 0]['amount'].sum()))
        net_profit = float(total_revenue - total_expenses)
        profit_margin = (net_profit / total_revenue) * 100 if total_revenue > 0 else 0
        health_score = int(min(100, max(0, profit_margin * 2 + 50))) # Simple logic: Base 50 + 2*Margin

        financial_summary = {
            "Total Revenue": total_revenue,
            "Total Expenses": total_expenses,
            "Net Profit": net_profit,
            "Profit Margin": f"{profit_margin:.2f}%",
            "Industry": industry,
            "Company": company_name
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

    # 2. Get AI Analysis
    try:
        print(f"Starting AI Analysis for {company_name} in language: {language}...")
        ai_insight = analyze_with_llm(financial_summary, language)
        print("AI Analysis Result (first 100 chars):", str(ai_insight)[:100])
    except Exception as e:
        print(f"CRITICAL AI ERROR: {e}")
        ai_insight = '{"executive_summary": "AI Analysis Failed due to internal error.", "creditworthiness": "Unknown"}'

    # 3. Save to Database
    try:
        print("Attempting to save to database...")
        # Create Company if not exists (Simplified logic)
        company = Company(name=company_name, industry=industry)
        db.add(company)
        db.commit()
        db.refresh(company)

        from crypto_utils import encrypt_value

        report = FinancialReport(
            company_id=company.id,
            upload_filename=file.filename,
            revenue=encrypt_value(total_revenue),    # Encrypted
            expenses=encrypt_value(total_expenses),  # Encrypted
            net_profit=encrypt_value(net_profit),    # Encrypted
            health_score=health_score,
            ai_analysis_text=str(ai_insight)
        )
        db.add(report)
        db.commit()
        print("Database save successful (Encrypted)!")

        # 4. Save Audit Log (Regulatory Compliance)
        try:
             # Extract simple verdict (e.g., Creditworthiness) or default
             verdict = "Analysis Complete"
             try:
                 parsed_ai = json.loads(ai_insight)
                 # Check common key variations
                 cw = parsed_ai.get('creditworthiness') or parsed_ai.get('Creditworthiness') or parsed_ai.get('credit_worthiness') or 'Unknown'
                 verdict = f"Credit: {cw}"
             except Exception as e:
                 print(f"Verdict Extraction Failed: {e}")
                 verdict = "Credit: Unknown (Parse Error)"

             audit_log = ComplianceLog(
                 company_name=company_name,
                 action_type="AI Risk Assessment",
                 ai_model="GPT-5",
                 decision_summary=verdict
             )
             db.add(audit_log)
             db.commit()
             print("Audit Log Saved.")
        except Exception as e:
             print(f"AUDIT LOG ERROR: {e}")

    except Exception as e:
        print(f"CRITICAL DATABASE ERROR: {e}")
        # Proceed to return result to user even if DB fails

    # Standardize columns for consistency
    if df is not None:
        df.columns = df.columns.str.lower().str.strip()

    # 4. Generate Forecast
    forecast_data = None
    try:
        if df is not None:
             forecast_data = generate_forecast(df)
    except Exception as e:
        print(f"Forecast Module Error: {e}")

    # 5. Automated Bookkeeping
    bookkeeping_data = None
    try:
        if df is not None:
             bookkeeping_data = auto_categorize(df)
    except Exception as e:
        print(f"Bookkeeping Module Error: {e}")

    # 6. Tax Compliance
    tax_data = None
    try:
        tax_data = calculate_tax(financial_summary, bookkeeping_data)
    except Exception as e:
        print(f"Tax Module Error: {e}")

    # 7. Working Capital
    wc_data = None
    try:
        wc_data = analyze_working_capital(financial_summary, bookkeeping_data)
    except Exception as e:
        print(f"Working Capital Module Error: {e}")

    return {
        "metrics": financial_summary,
        "health_score": health_score,
        "ai_analysis": ai_insight,
        "forecast": forecast_data,
        "bookkeeping": bookkeeping_data,
        "tax": tax_data,
        "working_capital": wc_data
    }

@app.get("/compliance_logs")
def get_compliance_logs(db: Session = Depends(get_db)):
    # Return last 5 logs
    logs = db.query(ComplianceLog).order_by(ComplianceLog.timestamp.desc()).limit(5).all()
    return logs

from banking_mock import get_mock_bank_data

@app.get("/connect_bank/{bank_name}")
async def connect_bank(bank_name: str):
    print(f"Connecting to bank: {bank_name}")
    try:
        data = get_mock_bank_data(bank_name)
        print(f"Bank Data: {data}")
        return data
    except Exception as e:
        print(f"BANK ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_report")
async def get_report(data: dict):
    company_name = data.get("company_name", "SME")
    result_data = data.get("result", {})
    
    pdf_bytes = generate_pdf_report(company_name, result_data)
    
    # Return as downloadable file
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=Report_{company_name}.pdf"})

# ==========================================
# CATCH-ALL ROUTE FOR REACT (MUST BE LAST)
# ==========================================
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Ensure static folder exists to prevent crash during dev
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    # API routes match first because this is defined LAST.
    if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi"):
        raise HTTPException(status_code=404, detail="Not Found")
    
    file_path = os.path.join("static", full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
        
    return FileResponse("static/index.html")