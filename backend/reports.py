from fpdf import FPDF
import io

class PDFReport(FPDF):
    def header(self):
        try:
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, 'SME Financial Health Report', 0, 1, 'C')
            self.ln(5)
        except:
            pass

    def footer(self):
        try:
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        except:
            pass

def clean(text):
    """
    Aggressively cleans text to ensure FPDF compatibility (Latin-1/ASCII).
    """
    if not text:
        return ""
    text = str(text)
    # Replace common problem characters
    replacements = {
        '\u201c': '"', '\u201d': '"', '\u2018': "'", '\u2019': "'",
        '\u2013': '-', '\u2014': '-', '\u2022': '*', '\u2026': '...'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
        
    # Final safety: encode to ascii, ignoring errors to prevent '?' clutter
    # Ideally we'd use a utf-8 font, but for MVP standard font:
    return text.encode('latin-1', 'ignore').decode('latin-1')

def generate_pdf_report(company_name, result):
    try:
        pdf = PDFReport()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # 1. Executive Summary
        try:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, clean(f"Executive Summary for {company_name}"), 0, 1)
            pdf.set_font("Arial", size=10)
            
            score = result.get('health_score', 'N/A')
            pdf.multi_cell(0, 10, clean(f"Health Score: {score}/100"))
            
            ai_data = result.get('ai_analysis')
            ai_summary = "Analysis details available in dashboard."
            
            if isinstance(ai_data, str):
                try: 
                    import json
                    parsed = json.loads(ai_data)
                    ai_summary = parsed.get('executive_summary', ai_summary)
                except:
                    ai_summary = clean(ai_data)
            elif isinstance(ai_data, dict):
                ai_summary = ai_data.get('executive_summary', ai_summary)
                
            pdf.multi_cell(0, 7, clean(ai_summary))
            pdf.ln(5)
        except Exception as e:
            print(f"Error in Exec Summary: {e}")
            pdf.multi_cell(0, 10, "Summary generation failed.")

        # 2. Key Metrics
        try:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, clean("Key Financial Metrics"), 0, 1)
            pdf.set_font("Arial", size=10)
            metrics = result.get('metrics', {})
            for k, v in metrics.items():
                pdf.cell(100, 8, clean(f"{k}: ${v:,.2f}"), 0, 1)
            pdf.ln(5)
        except Exception as e:
            print(f"Error in Metrics: {e}")

        # 3. Tax & Working Capital
        try:
            if 'tax' in result:
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, clean("Tax & Compliance"), 0, 1)
                pdf.set_font("Arial", size=10)
                pdf.cell(100, 8, clean(f"Est. Liability: ${result['tax'].get('estimated_tax', 0):,.2f}"), 0, 1)
                pdf.cell(100, 8, clean(f"Status: {result['tax'].get('message', 'N/A')}"), 0, 1)
                pdf.ln(5)
        except Exception as e:
             print(f"Error in Tax: {e}")

        # Output
        return pdf.output(dest='S').encode('latin-1', 'replace')
        
    except Exception as e:
        print(f"CRITICAL PDF ERROR: {e}")
        # Return a valid PDF saying error
        err_pdf = FPDF()
        err_pdf.add_page()
        err_pdf.set_font("Arial", size=12)
        err_pdf.cell(0, 10, "Error generating report. Please check server logs.", 0, 1)
        return err_pdf.output(dest='S').encode('latin-1', 'replace')
