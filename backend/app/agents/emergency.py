from pydantic import BaseModel, Field
from typing import List
from backend.app.agents.base import BaseAgent

class EmergencyAssessment(BaseModel):
    is_emergency: bool = Field(
        description="True if the symptoms describe a life-threatening medical emergency requiring immediate hospitalization or ambulance call (e.g. chest pain, difficulty breathing, severe bleeding, sudden numbness/paralysis, anaphylaxis, unconsciousness)."
    )
    reason: str = Field(description="Clinical reason why this constitutes or does not constitute a critical emergency.")
    immediate_actions: List[str] = Field(
        description="List of immediate first aid or safety actions the user should take (e.g., 'Take 325mg aspirin', 'Sit upright', 'Apply pressure to the wound'). Empty list if not an emergency."
    )

SYSTEM_INSTRUCTION = """You are the Emergency Triage Agent for HealthSphere AI.
Your primary role is to examine the user's symptoms and determine if they require immediate emergency medical care.
Be conservative: if there is a reasonable risk of a life-threatening condition (e.g., cardiac arrest, stroke, severe sepsis, anaphylaxis, heavy arterial bleeding), classify it as an emergency.
Provide clear, actionable first-aid steps that can be done instantly."""

class EmergencyAgent(BaseAgent):
    def __init__(self):
        super().__init__(system_instruction=SYSTEM_INSTRUCTION)

    def assess(self, symptoms: str, duration: str = "unknown", language: str = "English") -> EmergencyAssessment:
        prompt = (
            f"Symptoms reported: '{symptoms}' (Duration: {duration}).\n"
            f"Target Language: {language}.\n"
            f"If language is Hindi, write the 'reason' and 'immediate_actions' in clear Hindi Devnagari script.\n"
            f"Ensure recommendations refer to Indian helpline numbers like 112 (National Emergency) and 108 (Ambulance).\n"
            f"Analyze if this is an immediate emergency."
        )
        return self.generate_structured(prompt, EmergencyAssessment)
