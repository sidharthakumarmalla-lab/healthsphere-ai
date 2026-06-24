import json
from pydantic import BaseModel, Field
from typing import List
from backend.app.agents.base import BaseAgent
from backend.app.agents.skills import lookup_welfare_benefits

class EligibleScheme(BaseModel):
    name: str
    description: str
    eligibility_reason: str = Field(description="Why this specific family profile (based on age, income, state) qualifies for this scheme.")
    benefits_summary: str = Field(description="What financial or medical benefits are covered (e.g., Free delivery, Rs. 5 Lakh coverage).")
    application_steps: List[str] = Field(description="Step-by-step guidance on how to register or claim (e.g., Go to nearest PHC with Aadhaar card).")

class GovernmentBenefitsResponse(BaseModel):
    eligible_schemes: List[EligibleScheme]
    general_counseling: str = Field(description="General counseling for the family on utilizing government health services.")

SYSTEM_INSTRUCTION = """You are the Government Benefits Agent for HealthSphere AI.
Your role is to identify and recommend government healthcare schemes (e.g., Ayushman Bharat PM-JAY, maternal health aids, senior insurance) that a family member is eligible for.
You must use the `lookup_welfare_benefits` tool to evaluate and query available welfare health schemes matching the patient profile.
Evaluate eligibility based on the rules, age, income limits, and condition context (e.g., pregnant symptoms imply maternal benefit eligibility).
Return a structured eligibility analysis in the target language with concrete, simple enrollment steps."""

class GovernmentBenefitsAgent(BaseAgent):
    def __init__(self):
        super().__init__(system_instruction=SYSTEM_INSTRUCTION)

    def assess_benefits(self, profile_age: int, profile_income: float, symptoms: str, gender: str, location_zip: str, language: str = "English") -> GovernmentBenefitsResponse:
        prompt = (
            f"Patient Age: {profile_age}\n"
            f"Patient Gender: {gender}\n"
            f"Patient Location (ZIP/PIN Code): {location_zip}\n"
            f"Family Monthly Income: {profile_income} INR\n"
            f"Symptoms reported: {symptoms}\n"
            f"Target Language: {language}\n"
            f"If language is not English, write the 'eligibility_reason', 'benefits_summary', 'description', and 'application_steps' in the native script of the selected target language.\n"
            f"Use the `lookup_welfare_benefits` tool to fetch schemes, then evaluate the patient's eligibility."
        )

        return self.generate_with_tools(
            prompt, 
            tools=[lookup_welfare_benefits], 
            schema=GovernmentBenefitsResponse
        )

