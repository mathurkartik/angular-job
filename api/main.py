from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.routes import jobs, scrape
from db.database import engine, Base
import asyncio

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for the Automated Job Acquisition Engine",
    version="1.0.0"
)

# CORS configuration for potential frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs.router, prefix=f"{settings.API_V1_STR}/jobs", tags=["jobs"])
app.include_router(scrape.router, prefix=f"{settings.API_V1_STR}/scrape", tags=["scrape"])

@app.on_event("startup")
async def startup_event():
    """Create DB tables on startup if they don't exist."""
    async with engine.begin() as conn:
        # Warning: For production, use Alembic for migrations instead of create_all
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Job Engine API is running"}
