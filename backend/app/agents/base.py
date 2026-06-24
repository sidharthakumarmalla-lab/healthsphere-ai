import os
import re
import time
import json
from typing import Any
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

    def _generate_content_with_retry(self, contents: Any, config: Any) -> Any:
        max_retries = 6
        delay = 3
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=config
                )
                return response
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

    def generate_text(self, prompt: str) -> str:
        config = types.GenerateContentConfig()
        if self.system_instruction:
            config.system_instruction = self.system_instruction
        
        response = self._generate_content_with_retry(prompt, config)
        return response.text

    def generate_structured(self, prompt: str, schema) -> BaseModel:
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema
        )
        if self.system_instruction:
            config.system_instruction = self.system_instruction

        response = self._generate_content_with_retry(prompt, config)
        response_text = response.text

        try:
            return schema.model_validate_json(response_text)
        except Exception:
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            return schema.model_validate_json(cleaned_text.strip())

    def generate_with_tools(self, prompt: str, tools: list, schema = None) -> Any:
        """Execute a multi-turn conversation with Gemini binding native tools/skills."""
        config = types.GenerateContentConfig(
            tools=tools
        )
        if self.system_instruction:
            config.system_instruction = self.system_instruction

        max_turns = 6
        contents = [
            types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
        ]

        for turn in range(max_turns):
            response = self._generate_content_with_retry(contents, config)

            if response.function_calls:
                # Add assistant call to history
                contents.append(response.candidates[0].content)

                tool_map = {t.__name__: t for t in tools}
                tool_parts = []
                for fc in response.function_calls:
                    name = fc.name
                    args = fc.args
                    
                    if name in tool_map:
                        try:
                            # Invoke the actual Python skill function
                            res = tool_map[name](**args)
                        except Exception as e:
                            res = json.dumps({"error": str(e)})
                    else:
                        res = json.dumps({"error": f"Tool {name} not found"})

                    tool_parts.append(
                        types.Part.from_function_response(
                            name=name,
                            response={"result": res}
                        )
                    )

                # Add tool answers to history
                contents.append(
                    types.Content(role="tool", parts=tool_parts)
                )
            else:
                # Final turn
                if schema:
                    try:
                        return schema.model_validate_json(response.text)
                    except Exception:
                        refine_prompt = (
                            f"Transform the following response context into structured JSON matching the Pydantic schema:\n\n"
                            f"Response: {response.text}"
                        )
                        return self.generate_structured(refine_prompt, schema)
                return response.text

