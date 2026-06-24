import json
from pydantic import BaseModel, Field
from typing import List
from backend.app.agents.base import BaseAgent
from backend.app.agents.skills import lookup_local_hospitals

class RecommendedHospital(BaseModel):
    name: str
    specialties: List[str]
    address: str
    contact_number: str
    distance_miles: float = Field(description="Mock distance in miles (e.g., 2.5).")
    routing_reason: str = Field(description="Why this specific clinic/hospital is suited for the patient's current severity and symptoms.")

class HospitalDiscoveryResponse(BaseModel):
    recommended_hospitals: List[RecommendedHospital]
    general_guidance: str = Field(description="Advice on traveling to the facility, what documents to carry (like ID card, card schemes).")

SYSTEM_INSTRUCTION = """You are the Hospital Discovery Agent for HealthSphere AI.
Your role is to recommend the best local clinics, primary health centers (PHCs), or community health centers (CHCs) for a patient.
You must use the `lookup_local_hospitals` tool to retrieve available clinics for the patient's ZIP code.
Review the hospitals returned by the tool, select the most relevant ones, assign a mock distance (e.g. between 1 and 15 miles), and provide a 'routing_reason' explaining why that facility is appropriate (e.g., 'This clinic is 2 miles away and handles basic fever checkups, suitable for low severity symptoms' or 'As a District Hospital with an ICU, they can handle your severe respiratory distress.')."""

class HospitalDiscoveryAgent(BaseAgent):
    def __init__(self):
        super().__init__(system_instruction=SYSTEM_INSTRUCTION)

    def discover(self, location_zip: str, symptoms: str, severity: str, language: str = "English") -> HospitalDiscoveryResponse:
        prompt = (
            f"Patient Location ZIP/PIN: {location_zip}\n"
            f"Patient Symptoms: {symptoms}\n"
            f"Assessed Severity: {severity}\n"
            f"Target Language: {language}\n"
            f"If language is not English, write the 'routing_reason' and 'general_guidance' in the native script of the target language.\n"
            f"Use the `lookup_local_hospitals` tool with the ZIP code to discover clinics, then select and rank them."
        )
        
        return self.generate_with_tools(prompt, tools=[lookup_local_hospitals], schema=HospitalDiscoveryResponse)

