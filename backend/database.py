from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os

# REPLACE WITH YOUR DATABASE URL
# Format: postgresql://user:password@localhost:5432/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/finhealth")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    industry = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class FinancialReport(Base):
    __tablename__ = "financial_reports"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    upload_filename = Column(String)
    # Storing encrypted strings instead of raw floats
    revenue = Column(String) 
    expenses = Column(String)
    net_profit = Column(String)
    health_score = Column(Integer)
    ai_analysis_text = Column(Text)
    report_date = Column(DateTime, default=datetime.datetime.utcnow)

class ComplianceLog(Base):
    """
    Audit trail for AI decisions to ensure regulatory compliance and explainability.
    """
    __tablename__ = "compliance_logs"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String)
    action_type = Column(String) # e.g., "Risk Assessment", "Credit Check"
    ai_model = Column(String)
    decision_summary = Column(String) # Short verdict e.g. "High Risk"
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)