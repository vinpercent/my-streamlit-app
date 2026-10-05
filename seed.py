import pandas as pd
from database import engine
mock_data = pd.DataFrame({
    "clinic_name": ["Equity Afya - Thika", "Equity Afya - Eldoret", "Equity Afya - Kawangware", "Equity Afya - Kisumu CBD"],
    "county": ["Kiambu", "Uasin Gishu", "Nairobi", "Kisumu"],
    "initial_capital_kes": [6000000.0, 5500000.0, 4000000.0, 7000000.0],
    "monthly_operating_cost_kes": [700000.0, 600000.0, 450000.0, 850000.0],
    "average_monthly_patients": [500, 400, 650, 550],
    "competitor_count_radius_5km": [3, 5, 12, 6],
    "historical_survival_months": [48, 36, 18, 42]
})
try:
    mock_data.to_sql("franchise_metrics", con=engine, if_exists="append", index=False)
    print("? Database records successfully generated.")
except Exception as e:
    print(f"? Seed error: {e}")
