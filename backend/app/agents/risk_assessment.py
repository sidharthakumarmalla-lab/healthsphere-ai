from pydantic import BaseModel, Field
from typing import List
from backend.app.agents.base import BaseAgent

class RiskAssessment(BaseModel):
    risk_score: float = Field(
        description="A risk score from 0.0 (no risk, healthy) to 10.0 (critical, severe emergency)."
    )
    severity_level: str = Field(
        description="The classified severity level. Must be one of: 'LOW', 'MEDIUM', 'HIGH'."
    )
    risk_factors: List[str] = Field(
        description="List of medical risk factors present (e.g. elderly age, pre-existing diabetes, long duration, compounding symptoms)."
    )
    rationalization: str = Field(
        description="A concise clinical rationale explaining how the score was determined."
    )

SYSTEM_INSTRUCTION = """You are the Risk Assessment Agent for HealthSphere AI.
Your role is to assess the clinical severity of the symptoms and assign a risk score from 0.0 to 10.0 and a category (LOW, MEDIUM, HIGH).
Factor in:
1. The symptoms themselves (e.g., chest pain is higher risk than a runny nose).
2. Pre-existing medical conditions and age from the profile context.
3. Compound symptoms.
Ensure your classification is clear and medically logical."""

class RiskAssessmentAgent(BaseAgent):
    def __init__(self):
        super().__init__(system_instruction=SYSTEM_INSTRUCTION)

    def assess(self, symptom_analysis_summary: str, profile_context: str = "") -> RiskAssessment:
        prompt = (
            f"Symptom Summary: {symptom_analysis_summary}\n"
            f"Patient Context (Age, History): {profile_context}\n"
            f"Perform risk calculation."
        )
        return self.generate_structured(prompt, RiskAssessment)
