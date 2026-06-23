from pydantic import BaseModel, Field
from typing import List
from backend.app.agents.base import BaseAgent

class ProposedReminder(BaseModel):
    medication_name: str = Field(description="Name of the medicine (e.g. Paracetamol, ORS, Cough Syrup).")
    dosage: str = Field(description="Dosage (e.g. '1 tablet', '500mg', '10ml').")
    frequency: str = Field(description="How often to take (e.g., 'Daily', 'Twice Daily', 'Three times daily').")
    time_of_day: str = Field(description="Recommended hour of day in HH:MM (e.g. '08:00', or comma-separated '08:00, 20:00'). Use 24-hour format.")

class MedicineReminderResponse(BaseModel):
    proposed_reminders: List[ProposedReminder]
    general_guidelines: str = Field(description="General warnings on taking medication, checking expiry, and advice on consulting a doctor first.")

SYSTEM_INSTRUCTION = """You are the Medicine Reminder Agent for HealthSphere AI.
Your role is to identify any standard Over-The-Counter (OTC) remedies or common medications mentioned in the treatment guidance (e.g. ORS for dehydration, Paracetamol for fever, Cetirizine for allergies) and propose a structured medication reminder schedule.
Ensure that you emphasize safety: advise taking prescription drugs only under a doctor's care, and note whether medications should be taken before or after meals."""

class MedicineReminderAgent(BaseAgent):
    def __init__(self):
        super().__init__(system_instruction=SYSTEM_INSTRUCTION)

    def generate_reminders(self, treatment_guidance: str, language: str = "English") -> MedicineReminderResponse:
        prompt = (
            f"Review the treatment guidance text and extract proposed medication schedules:\n"
            f"Guidance: '{treatment_guidance}'\n"
            f"Target Language: {language}\n"
            f"Map medicines to standard Indian equivalents (e.g., Paracetamol -> Dolo-650 or Crocin, ORS -> Electral, Cetirizine -> Okacet, Pantoprazole -> Pan-20/40).\n"
            f"If language is Hindi, write the 'medication_name', 'dosage', 'frequency', and 'general_guidelines' in clear Hindi Devnagari script.\n"
            f"Generate structured reminders."
        )
        return self.generate_structured(prompt, MedicineReminderResponse)
