import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import timedelta

def generate_forecast(df):
    """
    Generates a 6-month forecast for Revenue and Expenses.
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
        # Revenue is positive, Expenses are negative (usually), but we track magnitude for expenses
        # Actually our dataset might have mixed signs. Let's filter based on sign or type if available?
        # In our main.py we separated by sign. >0 is Revenue, <0 is Expense.
        
        monthly_rev = df[df['amount'] > 0].set_index('date').resample('ME')['amount'].sum().reset_index()
        monthly_exp = df[df['amount'] < 0].set_index('date').resample('ME')['amount'].sum().abs().reset_index() # Use abs for training
        
        # Helper to predict
        def predict_series(series_df, periods=6):
            if len(series_df) < 2:
                return [] # Not enough data
            
            # Prepare X (Ordinal dates) and y (Amounts)
            series_df['date_ordinal'] = series_df['date'].map(pd.Timestamp.toordinal)
            X = series_df[['date_ordinal']]
            y = series_df['amount']
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Future dates
            last_date = series_df['date'].max()
            future_dates = [last_date + pd.DateOffset(months=i+1) for i in range(periods)]
            future_ordinals = [[d.toordinal()] for d in future_dates]
            
            predictions = model.predict(future_ordinals)
            
            return [
                {"date": d.strftime("%b %Y"), "amount": round(max(0, float(pred)), 2)} # Ensure no negative revenue
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
