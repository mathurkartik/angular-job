import os
import json
from typing import List, Dict, Any, Optional
from groq import Groq
from utils.logger import get_logger

logger = get_logger("groq_client")

class GroqClient:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found in environment. Groq integrations will fail.")
        
        # We use a fast, cheap model for high-volume text parsing
        self.model = "llama-3.1-8b-instant" 
        self.client = Groq(api_key=self.api_key) if self.api_key else None

    def extract_jobs_from_text(self, text: str, base_url: str) -> List[Dict[str, Any]]:
        """
        Passes a massive wall of text to Groq and asks it to extract job listings as JSON.
        """
        if not self.client:
            return []

        prompt = f"""
You are an expert technical recruiter. I am going to give you the raw text scraped from a company's career page.
Your goal is to extract all the Software Engineering, Frontend, and UI job listings. Ignore marketing, sales, and irrelevant roles.

Base URL for relative links: {base_url}

Return ONLY a valid JSON object. Do not include markdown formatting or explanations.
The object must contain a single key called "jobs", which is an array of objects.
Each object in the array must have exactly these keys:
- "job_title": The title of the job.
- "location": The location of the job.
- "application_url": The direct URL to apply. If the text only has relative paths, prepend the Base URL.
- "description_text": A short snippet or description of the role if available.

Raw Page Text:
{text[:6000]}  # Truncating to avoid context limits if text is absolutely massive
"""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
                response_format={"type": "json_object"},
            )
            
            # Since Groq json_object requires an object (not an array), we should prompt it to return an object with a "jobs" array.
            # Let's adjust the prompt handling.
            response_content = chat_completion.choices[0].message.content
            return json.loads(response_content)
            
        except Exception as e:
            logger.error(f"Groq Extraction Failed: {str(e)}")
            return []



groq_client = GroqClient()
