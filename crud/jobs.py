from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert
from db.models import DBJobListing
from schemas.job_listing import ScoredJobListing

async def get_job_by_url(db: AsyncSession, application_url: str) -> Optional[DBJobListing]:
    result = await db.execute(select(DBJobListing).filter(DBJobListing.application_url == application_url))
    return result.scalars().first()

async def get_jobs(db: AsyncSession, skip: int = 0, limit: int = 100, min_score: float = 0.0) -> List[DBJobListing]:
    result = await db.execute(
        select(DBJobListing)
        .filter(DBJobListing.total_score >= min_score)
        .order_by(DBJobListing.total_score.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def upsert_job(db: AsyncSession, job: ScoredJobListing) -> DBJobListing:
    """Inserts a new job or updates an existing one if the URL matches."""
    job_data = {
        "company_name": job.company_name,
        "company_tier": job.company_tier,
        "category": job.category.value,
        "job_title": job.job_title,
        "location": job.location,
        "description_text": job.description_text,
        "application_url": str(job.application_url),
        "date_posted": job.date_posted,
        "passed_gates": job.passed_gates,
        "total_score": job.total_score,
        "pillar_scores": job.pillar_scores,
        "matched_keywords": job.matched_keywords,
        "justification": job.justification,
        "scraped_at": job.scraped_at
    }
    
    # PostgreSQL specific upsert (ON CONFLICT)
    stmt = insert(DBJobListing).values(**job_data)
    stmt = stmt.on_conflict_do_update(
        index_elements=['application_url'],
        set_=job_data
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    # Return the updated object
    return await get_job_by_url(db, str(job.application_url))
