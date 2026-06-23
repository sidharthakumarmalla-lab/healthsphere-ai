import json
from pydantic import BaseModel, Field
from typing import List
from sqlalchemy.orm import Session
from backend.app.agents.base import BaseAgent
from backend.app.models import HospitalMock

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
You will receive:
1. A list of local hospitals queried from the database.
2. The patient's symptom summary and severity.
Review the hospitals, select the most relevant ones, assign a mock distance (e.g. between 1 and 15 miles), and provide a 'routing_reason' explaining why that facility is appropriate (e.g., 'This clinic is 2 miles away and handles basic fever checkups, suitable for low severity symptoms' or 'As a District Hospital with an ICU, they can handle your severe respiratory distress.')."""

class HospitalDiscoveryAgent(BaseAgent):
    def __init__(self):
        super().__init__(system_instruction=SYSTEM_INSTRUCTION)

    def discover(self, db: Session, location_zip: str, symptoms: str, severity: str, language: str = "English") -> HospitalDiscoveryResponse:
        # Query local database for hospitals matching ZIP
        hospitals_db = db.query(HospitalMock).filter(HospitalMock.location_zip == location_zip).all()
        if not hospitals_db:
            # Fallback to default clinics
            hospitals_db = db.query(HospitalMock).filter(HospitalMock.location_zip == "default").all()

        # Format hospitals into a clean string for the LLM
        hospital_list = []
        for h in hospitals_db:
            hospital_list.append({
                "name": h.name,
                "specialties": json.loads(h.specialties),
                "address": h.address,
                "contact_number": h.contact_number
            })

        prompt = (
            f"Patient Location ZIP/PIN: {location_zip}\n"
            f"Patient Symptoms: {symptoms}\n"
            f"Assessed Severity: {severity}\n"
            f"Target Language: {language}\n"
            f"If language is Hindi, write the 'routing_reason' and 'general_guidance' in clear Hindi Devnagari script.\n"
            f"Available Local Hospitals: {json.dumps(hospital_list)}\n"
            f"Recommend and rank these clinics."
        )
        
        return self.generate_structured(prompt, HospitalDiscoveryResponse)
