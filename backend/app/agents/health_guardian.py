import json
from backend.app.agents.base import BaseAgent

SYSTEM_INSTRUCTION = """You are the Health Guardian Memory Agent for HealthSphere AI.
Your role is to manage the long-term electronic health record and clinical memory of the patient.
You perform two key tasks:
1. Summarize a new clinical encounter into a dense, descriptive summary text optimized for semantic vector searching.
2. Read a patient's medical history (past symptom summaries and risks) and write a cohesive, clinical summary of their longitudinal health history. Highlight repeating symptoms, increasing risk trends, or chronic complaints."""

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

    def synthesize_history_context(self, past_encounters: list, profile_details: dict) -> str:
        if not past_encounters:
            return f"Patient is a {profile_details.get('age')}-year-old {profile_details.get('gender')}. No prior HealthSphere encounter history."

        encounters_summary = []
        for e in past_encounters:
            # past_encounters can be a list of dicts (from vector store or database)
            encounters_summary.append({
                "date": str(e.get("created_at", "unknown")),
                "symptoms": e.get("summary", e.get("raw_symptoms", "")),
                "severity": e.get("severity_level", "")
            })

        prompt = (
            f"Patient Demographics: Age {profile_details.get('age')}, Gender {profile_details.get('gender')}, Chronic Conditions: {profile_details.get('medical_history')}, Allergies: {profile_details.get('allergies')}.\n"
            f"Past Encounters History:\n{json.dumps(encounters_summary)}\n"
            f"Write a concise clinical history summary of this patient, highlighting any patterns or concerns for the orchestrator."
        )
        return self.generate_text(prompt)
