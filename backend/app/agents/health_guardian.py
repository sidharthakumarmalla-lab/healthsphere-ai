import json
from backend.app.agents.base import BaseAgent
from backend.app.agents.skills import lookup_historical_memory

SYSTEM_INSTRUCTION = """You are the Health Guardian Memory Agent for HealthSphere AI.
Your role is to manage the long-term electronic health record and clinical memory of the patient.
You perform two key tasks:
1. Summarize a new clinical encounter into a dense, descriptive summary text optimized for semantic vector searching.
2. Retrieve a patient's historical encounters using the `lookup_historical_memory` tool and write a cohesive, clinical summary of their longitudinal health history. Highlight repeating symptoms, increasing risk trends, or chronic complaints."""

class HealthGuardianAgent(BaseAgent):
    def __init__(self):
        super().__init__(system_instruction=SYSTEM_INSTRUCTION)

    def summarize_for_memory(self, symptoms: str, severity: str, risk_score: float, clinical_notes: str) -> str:
        prompt = (
            f"Generate a dense vector-store-optimized search text for the following consultation:\n"
            f"- Symptoms: {symptoms}\n"
            f"- Severity: {severity}\n"
            f"- Risk Score: {risk_score}\n"
            f"- Notes: {clinical_notes}\n"
            f"Format it as a single coherent paragraph summarizing the clinical picture."
        )
        return self.generate_text(prompt)

    def synthesize_history_context(self, profile_id: int, symptoms_query: str, profile_details: dict) -> str:
        prompt = (
            f"Patient ID: {profile_id}\n"
            f"Symptom Query: {symptoms_query}\n"
            f"Patient Demographics: Age {profile_details.get('age')}, Gender {profile_details.get('gender')}, Chronic Conditions: {profile_details.get('medical_history')}, Allergies: {profile_details.get('allergies')}.\n"
            f"Use the `lookup_historical_memory` tool to retrieve past clinical consultations for this patient ID. "
            f"Then write a concise clinical history summary of this patient, highlighting any patterns or concerns for the orchestrator. "
            f"If no prior encounters are returned by the tool, simply state that the patient has no prior HealthSphere history."
        )
        return self.generate_with_tools(prompt, tools=[lookup_historical_memory])

