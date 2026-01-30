def analyze_working_capital(financial_summary, bookkeeping_data):
    """
    Analyzes working capital health, burn rate, and cash runway.
    """
    try:
        total_revenue = financial_summary.get('Total Revenue', 0)
        total_expenses = financial_summary.get('Total Expenses', 0)
        net_profit = financial_summary.get('Net Profit', 0)
        
        # 1. Burn Rate (Avg Monthly Expenses)
        # We assume the dataset spans roughly a month or we take the total expenses as the "burn" for this period
        burn_rate = total_expenses 
        
        # 2. Runway (Hypothetical - usually requires Cash Balance)
        # Since we don't have Bank Balance in CSV, we assume a starting balance or just give general advice
        # Let's assume a hypothetical cash reserve of 2x expenses for calculation or skip
        
        # 3. Efficiency Metrics
        marketing_spend = 0
        operational_spend = 0
        
        if bookkeeping_data and 'breakdown' in bookkeeping_data:
             for item in bookkeeping_data['breakdown']:
                 if item['name'] == 'Marketing':
                     marketing_spend = item['value']
                 if item['name'] == 'Operational':
                     operational_spend = item['value']
        
        marketing_efficiency = (total_revenue / marketing_spend) if marketing_spend > 0 else 0
        
        # Recommendations
        recommendations = []
        status = "Healthy"
        
        if net_profit < 0:
            status = "Critical"
            recommendations.append("Immediate: Reduce non-essential operational costs.")
            recommendations.append("Review payment terms with suppliers (extend days payable).")
        elif (operational_spend / total_expenses) > 0.6:
             recommendations.append("Operational costs are high (>60%). Audit utility and recurring services.")
             
        if marketing_efficiency > 5:
            recommendations.append("Marketing is highly efficient. Consider scaling ad spend.")
        elif marketing_efficiency < 2 and marketing_spend > 0:
            recommendations.append("Marketing ROI is low. Review campaign targeting.")

        return {
            "burn_rate": burn_rate,
            "marketing_efficiency": round(marketing_efficiency, 2),
            "status": status,
            "recommendations": recommendations,
            "operational_spend": operational_spend
        }

    except Exception as e:
        print(f"Working Capital Error: {e}")
        return None
