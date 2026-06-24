from pydantic import BaseModel, Field
from typing import List
from backend.app.agents.base import BaseAgent

class ConditionMatch(BaseModel):
    condition_name: str = Field(description="Name of the possible medical condition.")
    likelihood: str = Field(description="Likelihood of matching symptoms: 'Low', 'Moderate', or 'High'.")
    common_symptoms: List[str] = Field(description="List of common symptoms for this condition.")
    matching_indicators: List[str] = Field(description="Specific indicators from this patient matching this condition.")

class MedicalResearchResult(BaseModel):
    potential_conditions: List[ConditionMatch] = Field(description="List of potential conditions matching the symptoms.")
    relevant_guidelines: List[str] = Field(description="Standard clinical guidelines or recommendations for these symptoms (e.g. CDC/WHO guidelines).")
    clinical_evidence: str = Field(description="A concise summary of clinical knowledge backing these findings.")

SYSTEM_INSTRUCTION = """You are the Medical Research Agent for HealthSphere AI.
Your role is to retrieve general medical guidance, standard guidelines, and possible matching conditions for the patient's symptoms.
IMPORTANT: You do not diagnose. You only identify potential medical concepts and conditions that the patient can discuss with their healthcare provider.
Use clear, easy-to-understand language suitable for rural and underserved populations, avoiding overly dense medical jargon."""

class MedicalResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(system_instruction=SYSTEM_INSTRUCTION)

    def research(self, symptoms: str, severity: str, language: str = "English") -> MedicalResearchResult:
        prompt = (
            f"Symptoms: '{symptoms}' (Severity: {severity}).\n"
            f"Target Language: {language}.\n"
            f"If language is not English, generate 'relevant_guidelines' and 'clinical_evidence' in the clear native script of the target language (e.g., Devanagari for Hindi/Marathi, Tamil script for Tamil, Telugu script for Telugu, Bengali script for Bengali, Kannada script for Kannada, Malayalam script for Malayalam, Gujarati script for Gujarati, Gurmukhi for Punjabi, Odia script for Odia).\n"
            f"Ensure condition details and indicators reflect the target language context.\n"
            f"Research potential conditions and standard care guidelines."
        )
        return self.generate_structured(prompt, MedicalResearchResult)
