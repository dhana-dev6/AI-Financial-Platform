import pandas as pd
import numpy as np
# from sklearn.linear_model import LinearRegression # Removed to save memory on Render Free Tier
from datetime import timedelta

def generate_forecast(df):
    """
    Generates a 6-month forecast for Revenue and Expenses using simple statistical growth.
    """
    try:
        # data preparation
        # Coerce errors to NaT (Not a Time) prevents crash on "Monthly Agg."
        df['date'] = pd.to_datetime(df['date'], errors='coerce') 
        df = df.dropna(subset=['date']) # Drop rows with invalid dates
        
        if df.empty:
             return {"revenue_forecast": [], "expense_forecast": []}

        df = df.sort_values('date')
        
        # Resample to monthly to smooth out daily noise
        monthly_data = df.set_index('date').resample('ME')['amount'].sum().reset_index()
        
        # Separate Revenue and Expenses
        monthly_rev = df[df['amount'] > 0].set_index('date').resample('ME')['amount'].sum().reset_index()
        monthly_exp = df[df['amount'] < 0].set_index('date').resample('ME')['amount'].sum().abs().reset_index() # Use abs for training
        
        # Helper to predict (Simple Version)
        def predict_series(series_df, periods=6):
            if len(series_df) < 2:
                return [] 
            
            # Simple Average Growth
            # If we have 2 months: 100, 110. Growth = 10%.
            # Render Free Tier often crashes with Scikit-Learn.
            
            current_val = series_df['amount'].iloc[-1]
            avg_val = series_df['amount'].mean()
            
            # Simple projection: oscillate around average with slight growth
            growth_factor = 1.02 # Assumed 2% growth
            
            last_date = series_df['date'].max()
            future_dates = [last_date + pd.DateOffset(months=i+1) for i in range(periods)]
            
            predictions = []
            param_val = current_val
            for _ in future_dates:
                param_val = param_val * growth_factor
                predictions.append(param_val)

            return [
                {"date": d.strftime("%b %Y"), "amount": round(max(0, float(pred)), 2)} 
                for d, pred in zip(future_dates, predictions)
            ]

        forecast_rev = predict_series(monthly_rev)
        forecast_exp = predict_series(monthly_exp)
        
        return {
            "revenue_forecast": forecast_rev,
            "expense_forecast": forecast_exp
        }

    except Exception as e:
        print(f"Forecasting Error: {e}")
        return None
