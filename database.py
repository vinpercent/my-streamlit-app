import os
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

# Using version 4 to bypass any cached database structures completely
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///equity_afya_v4.db")
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class FranchiseMetrics(Base):
    __tablename__ = 'franchise_metrics'
    id = Column(Integer, primary_key=True)
    clinic_name = Column(String, nullable=False)
    county = Column(String, nullable=False)
    initial_capital_kes = Column(Float, nullable=False)
    monthly_operating_cost_kes = Column(Float, nullable=False)
    average_monthly_patients = Column(Integer, nullable=False)
    competitor_count_radius_5km = Column(Integer, nullable=False)
    historical_survival_months = Column(Integer, nullable=False)

def init_db():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
    print("✅ New database tables initialized successfully.")
