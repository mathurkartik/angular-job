from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
from db.database import get_db
from crud.jobs import get_jobs
import json

router = APIRouter()

class JobResponse(BaseModel):
    company_name: str
    company_tier: str
    category: str
    job_title: str
    location: str
    total_score: float
    justification: str
    application_url: HttpUrl
    passed_gates: List[str]
    matched_keywords: dict

    class Config:
        from_attributes = True

@router.get("/", response_model=List[JobResponse])
async def read_jobs(
    skip: int = 0, 
    limit: int = 100, 
    min_score: float = Query(0.35, description="Minimum score threshold"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve scored and ranked jobs from the database.
    """
    jobs = await get_jobs(db, skip=skip, limit=limit, min_score=min_score)
    return jobs
