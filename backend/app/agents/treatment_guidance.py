from pydantic import BaseModel, Field
from typing import List
from backend.app.agents.base import BaseAgent

class TreatmentGuidanceResponse(BaseModel):
    home_care_measures: List[str] = Field(description="Actionable home care steps (e.g., oral rehydration, warm compresses, physical rest) suitable for low/medium risk.")
    warning_signs: List[str] = Field(description="Red flag warning signs that, if developed, require immediate trip to an emergency room.")
    recommended_next_steps: List[str] = Field(description="Step-by-step next actions (e.g., visit local PHC, book eye test).")
    educational_notes: str = Field(description="A brief explanation of how to manage these symptoms and stay healthy.")
    clinical_disclaimer: str = Field(
        description="A mandatory medical disclaimer stating that this AI output is for guidance only, not a professional medical diagnosis or treatment plan."
    )

SYSTEM_INSTRUCTION = """You are the Treatment Guidance Agent for HealthSphere AI.
Your role is to compile recommendations, home-care guidance, and crucial safety warnings for patients based on diagnostic outputs from analysis, research, and risk assessment agents.
Rules:
1. Always prioritize patient safety.
2. If risk is high, direct them to professional care immediately.
3. Write in extremely clear, supportive, and accessible language suitable for rural and underserved users.
4. Include a prominent disclaimer."""

class TreatmentGuidanceAgent(BaseAgent):
    def __init__(self):
        super().__init__(system_instruction=SYSTEM_INSTRUCTION)

    def formulate_guidance(self, symptom_summary: str, risk_level: str, research_summary: str, language: str = "English") -> TreatmentGuidanceResponse:
        prompt = (
            f"Symptom Summary: {symptom_summary}\n"
            f"Risk Level Assessed: {risk_level}\n"
            f"Medical Research Findings: {research_summary}\n"
            f"Target Language: {language}\n"
            f"If language is Hindi, write the 'home_care_measures', 'warning_signs', 'recommended_next_steps', 'educational_notes', and 'clinical_disclaimer' in clear Hindi Devnagari script.\n"
            f"Formulate safe treatment guidance."
        )
        return self.generate_structured(prompt, TreatmentGuidanceResponse)
