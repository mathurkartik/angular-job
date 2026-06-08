from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.sql import func
from db.database import Base

class DBJobListing(Base):
    __tablename__ = "job_listings"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    company_tier = Column(String)
    category = Column(String, index=True)
    job_title = Column(String)
    location = Column(String)
    description_text = Column(Text)
    application_url = Column(String, unique=True, index=True) # Unique to prevent duplicates
    date_posted = Column(String, nullable=True)
    
    # Filter stats
    passed_gates = Column(JSON)
    
    # Scoring stats
    total_score = Column(Float, index=True)
    pillar_scores = Column(JSON)
    matched_keywords = Column(JSON)
    justification = Column(String)
    
    # Metadata
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ScrapeTask(Base):
    __tablename__ = "scrape_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True)
    category = Column(String)
    status = Column(String, default="PENDING") # PENDING, RUNNING, SUCCESS, FAILED
    jobs_found = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
