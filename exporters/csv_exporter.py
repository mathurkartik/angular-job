import csv
from typing import List
from pathlib import Path
from schemas.job_listing import ExportedJobListing

class CSVExporter:
    @staticmethod
    def export(jobs: List[ExportedJobListing], filepath: str = "output/jobs.csv"):
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        if not jobs:
            return
            
        headers = [
            "Rank", "Category", "Tier", "Company", "Job Title", 
            "Location", "Application URL"
        ]
        
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for job in jobs:
                writer.writerow([
                    job.rank,
                    job.category.value,
                    job.company_tier,
                    job.company_name,
                    job.job_title,
                    job.location,
                    job.application_url
                ])
