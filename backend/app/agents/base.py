import os
import re
import time
from pydantic import BaseModel
from google import genai
from google.genai import types
from backend.app.config import GEMINI_API_KEY

class BaseAgent:
    def __init__(self, system_instruction: str = None):
        key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=key)
        self.model_name = "gemini-3.1-flash-lite"
        self.system_instruction = system_instruction

    def generate_text(self, prompt: str) -> str:
        config = types.GenerateContentConfig()
        if self.system_instruction:
            config.system_instruction = self.system_instruction
        
        max_retries = 6
        delay = 3
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                return response.text
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                err_msg = str(e).lower()
                if "429" in err_msg or "resource_exhausted" in err_msg or "quota" in err_msg:
                    match = re.search(r"retry in ([\d\.]+)s", err_msg)
                    sleep_time = float(match.group(1)) + 2.0 if match else 35.0
                    print(f"[Gemini Rate Limit] 429 encountered in {self.__class__.__name__} (attempt {attempt+1}/{max_retries}). Sleeping {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                else:
                    print(f"[Gemini Error] Exception in {self.__class__.__name__} (attempt {attempt+1}/{max_retries}): {e}. Sleeping {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2

    def generate_structured(self, prompt: str, schema) -> BaseModel:
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema
        )
        if self.system_instruction:
            config.system_instruction = self.system_instruction

        max_retries = 6
        delay = 3
        response_text = ""
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                response_text = response.text
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                err_msg = str(e).lower()
                if "429" in err_msg or "resource_exhausted" in err_msg or "quota" in err_msg:
                    match = re.search(r"retry in ([\d\.]+)s", err_msg)
                    sleep_time = float(match.group(1)) + 2.0 if match else 35.0
                    print(f"[Gemini Rate Limit] 429 encountered in {self.__class__.__name__} (attempt {attempt+1}/{max_retries}). Sleeping {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                else:
                    print(f"[Gemini Error] Exception in {self.__class__.__name__} (attempt {attempt+1}/{max_retries}): {e}. Sleeping {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2

        import json
        try:
            return schema.model_validate_json(response_text)
        except Exception as e:
            # Fallback parse or error raising
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            return schema.model_validate_json(cleaned_text.strip())
