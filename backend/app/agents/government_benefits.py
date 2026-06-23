import json
from pydantic import BaseModel, Field
from typing import List
from sqlalchemy.orm import Session
from backend.app.agents.base import BaseAgent
from backend.app.models import SchemeMock

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
You will receive:
1. The patient's profile details (age, relationship, income, location).
2. A list of government schemes stored in our database registry.
Evaluate eligibility based on age, income limits, and condition context (e.g., pregnant symptoms imply maternal benefit eligibility).
Return a structured eligibility analysis with concrete, simple enrollment steps."""

class GovernmentBenefitsAgent(BaseAgent):
    def __init__(self):
        super().__init__(system_instruction=SYSTEM_INSTRUCTION)

    def assess_benefits(self, db: Session, profile_age: int, profile_income: float, symptoms: str, gender: str, location_zip: str, language: str = "English") -> GovernmentBenefitsResponse:
        # Fetch schemes from DB
        schemes_db = db.query(SchemeMock).all()
        
        schemes_list = []
        for s in schemes_db:
            schemes_list.append({
                "name": s.name,
                "description": s.description,
                "eligibility_rules": s.eligibility_rules,
                "min_age": s.min_age,
                "max_income": s.max_income,
                "benefits_details": s.benefits_details
            })

        prompt = (
            f"Patient Age: {profile_age}\n"
            f"Patient Gender: {gender}\n"
            f"Patient Location (ZIP/PIN Code): {location_zip}\n"
            f"Family Monthly Income: {profile_income} INR\n"
            f"Symptoms reported: {symptoms}\n"
            f"Target Language: {language}\n"
            f"If language is Hindi, write the 'eligibility_reason', 'benefits_summary', 'description', and 'application_steps' in clear Hindi Devnagari script.\n"
            f"Available Government Schemes: {json.dumps(schemes_list)}\n"
            f"Evaluate eligibility."
        )

        return self.generate_structured(prompt, GovernmentBenefitsResponse)
