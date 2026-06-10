import json
import os
from filters.title_filter import TitleFilter

def clean_json():
    json_path = "frontend/public/jobs.json"
    
    with open(json_path, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
        
    print(f"Original jobs count: {len(jobs)}")
    
    clean_jobs = [job for job in jobs if TitleFilter.passes(job.get("job_title", ""))]
    
    # Re-rank them
    for i, job in enumerate(clean_jobs):
        job["rank"] = i + 1
        
    print(f"Cleaned jobs count: {len(clean_jobs)}")
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(clean_jobs, f, indent=4)
        
if __name__ == "__main__":
    clean_json()
