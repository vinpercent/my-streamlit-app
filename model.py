import pandas as pd
from sklearn.linear_model import LinearRegression
from database import engine

def train_lifespan_model():
    try:
        # Pull data arrays from our sqlite tables
        query = "SELECT initial_capital_kes, monthly_operating_cost_kes, average_monthly_patients, competitor_count_radius_5km, historical_survival_months FROM franchise_metrics"
        df = pd.read_sql(query, engine)
        
        # Linear Regression demands data depth. If rows < 3, return None for fallback
        if df.empty or len(df) < 3:
            return None

        X = df[['initial_capital_kes', 'monthly_operating_cost_kes', 'average_monthly_patients', 'competitor_count_radius_5km']]
        y = df['historical_survival_months']
        
        model = LinearRegression()
        model.fit(X, y)
        return model
    except Exception:
        return None

def predict_months(model, features):
    # Safe heuristic processing fallback logic if model is None
    if model is None:
        initial_capital, monthly_cost, patients, competitors = features
        # Calculate financial runway math baseline safely
        net_monthly_income = (patients * 2500) - monthly_cost
        if net_monthly_income >= 0:
            return 60.0  # Sustainable operational projection (5 years)
        else:
            runway = initial_capital / abs(net_monthly_income)
            return min(60.0, round(runway, 1))
    
    try:
        prediction = model.predict([features])
        return max(0.0, round(float(prediction[0]), 1))
    except Exception:
        return 12.0
