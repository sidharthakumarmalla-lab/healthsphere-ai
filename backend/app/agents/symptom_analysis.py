from pydantic import BaseModel, Field
from typing import List
from backend.app.agents.base import BaseAgent

class SymptomAnalysis(BaseModel):
    parsed_symptoms: List[str] = Field(description="Clean, standard list of identified symptoms.")
    affected_body_parts: List[str] = Field(description="List of body parts or systems affected (e.g. Chest, Digestive, Respiratory, Head).")
    severity_signals: List[str] = Field(description="Any specific alarming details mentioned (e.g., high fever, coughing blood, pain spreading to arm).")
    structured_summary: str = Field(description="A concise clinical summary of the patient's symptoms, onset, and description.")

SYSTEM_INSTRUCTION = """You are the Symptom Analysis Agent for HealthSphere AI.
Your job is to parse unstructured, raw symptoms entered by the patient and extract a clean, structured clinical summary.
Ignore irrelevant chit-chat and focus on clinical symptoms, duration, qualifiers, and affected body regions."""

class SymptomAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(system_instruction=SYSTEM_INSTRUCTION)

    def analyze(self, symptoms: str, profile_context: str = "", language: str = "English") -> SymptomAnalysis:
        prompt = (
            f"Symptoms: '{symptoms}'.\n"
            f"Patient Profile Context: {profile_context}\n"
            f"Target Language: {language}.\n"
            f"If language is not English, generate the 'structured_summary' in the clear native script of the target language (e.g., Devanagari for Hindi/Marathi, Tamil script for Tamil, Telugu script for Telugu, Bengali script for Bengali, Kannada script for Kannada, Malayalam script for Malayalam, Gujarati script for Gujarati, Gurmukhi for Punjabi, Odia script for Odia).\n"
            f"Note: keep the list keys 'parsed_symptoms' and 'affected_body_parts' in English for standard backend processing, but write the 'structured_summary' in the target language."
        )
        return self.generate_structured(prompt, SymptomAnalysis)
