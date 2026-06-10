import os
import json
from typing import List, Dict, Any, Optional
from groq import Groq
from utils.logger import get_logger

logger = get_logger("groq_client")

class GroqClient:
    def __init__(self):
        # Support either a comma-separated list of keys or a single key
        keys_env = os.getenv("GROQ_API_KEYS") or os.getenv("GROQ_API_KEY")
        
        self.api_keys = []
        if keys_env:
            self.api_keys = [k.strip() for k in keys_env.split(",") if k.strip()]
            
        if not self.api_keys:
            logger.warning("No GROQ_API_KEY found in environment. Groq integrations will fail.")
        
        # We use a fast, cheap model for high-volume text parsing
        self.model = "llama-3.1-8b-instant" 
        self.current_key_idx = 0
        self.client = Groq(api_key=self.api_keys[self.current_key_idx]) if self.api_keys else None

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
        attempts = 0
        max_attempts = len(self.api_keys) if self.api_keys else 1
        
        while attempts < max_attempts:
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
                
                response_content = chat_completion.choices[0].message.content
                return json.loads(response_content)
                
            except Exception as e:
                error_str = str(e).lower()
                # Check for rate limit / 429 error or invalid API key / 401 error
                if "rate limit" in error_str or "429" in error_str or "401" in error_str or "invalid" in error_str:
                    attempts += 1
                    logger.warning(f"Groq Error (Rate limit/Invalid key) hit on key {self.current_key_idx + 1}/{len(self.api_keys)}.")
                    
                    if attempts < max_attempts:
                        self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
                        logger.info(f"Switching to Groq API Key {self.current_key_idx + 1}...")
                        self.client = Groq(api_key=self.api_keys[self.current_key_idx])
                    else:
                        logger.error("All Groq API keys have hit their rate limits or are invalid.")
                        return []
                else:
                    logger.error(f"Groq Extraction Failed: {str(e)}")
                    return []
        
        return []



groq_client = GroqClient()
