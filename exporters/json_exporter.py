import json
from typing import List
from pathlib import Path
from schemas.job_listing import ScoredJobListing

class JSONExporter:
    @staticmethod
    def export(jobs: List[ScoredJobListing], filepath: str = "output/jobs.json"):
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        data = [job.model_dump(mode="json") for job in jobs]
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
