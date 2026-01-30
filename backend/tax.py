def calculate_tax(financial_summary, bookkeeping_data):
    """
    Estimates tax liability and identifies deductions.
    Assumptions:
    - Flat Corporate Tax Rate: 25% (indicative)
    - Deductible Categories: Operational, Marketing, Software, Travel, COGS, Payroll.
    """
    try:
        net_profit = financial_summary.get('Net Profit', 0)
        
        # 1. Estimate Tax Liability
        estimated_tax = max(0, net_profit * 0.25)
        
        # 2. Identify Deductions
        deductible_cats = ["Operational", "Marketing", "Software", "Travel & Meals", "COGS", "Payroll"]
        total_deduction = 0
        deduction_breakdown = []
        
        if bookkeeping_data and 'breakdown' in bookkeeping_data:
            for item in bookkeeping_data['breakdown']:
                if item['name'] in deductible_cats:
                    total_deduction += item['value']
                    deduction_breakdown.append(item)
        
        # 3. Tax Health Status
        status = "Good"
        msg = "Tax liability is manageable."
        if estimated_tax > (net_profit * 0.4): # Just a heuristic
            status = "High Tax Burden"
            msg = "Consider re-evaluating expenses or consulting a tax pro."
            
        return {
            "estimated_tax": estimated_tax,
            "tax_rate": "25% (Indicative)",
            "total_deductible_expenses": total_deduction,
            "deduction_breakdown": deduction_breakdown,
            "status": status,
            "message": msg
        }

    except Exception as e:
        print(f"Tax Calc Error: {e}")
        return None
