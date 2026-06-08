from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from workers.tasks import scrape_category_task

router = APIRouter()

class ScrapeRequest(BaseModel):
    category: str  # "main", "indian_product", "service"
    headless: bool = True

class ScrapeResponse(BaseModel):
    message: str
    task_id: str

@router.post("/", response_model=ScrapeResponse, status_code=202)
async def trigger_scrape(request: ScrapeRequest):
    """
    Triggers a background Celery task to scrape the requested category.
    Returns immediately with a task ID.
    """
    valid_categories = ["main", "indian_product", "service"]
    if request.category not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of {valid_categories}")

    # Dispatch to Celery
    task = scrape_category_task.delay(request.category, request.headless)
    
    return ScrapeResponse(
        message=f"Scraping task for '{request.category}' started in the background.",
        task_id=task.id
    )

@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Checks the status of a Celery scraping task.
    """
    task_result = scrape_category_task.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }
