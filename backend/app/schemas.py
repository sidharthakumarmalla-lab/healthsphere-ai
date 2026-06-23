from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- PROFILE SCHEMAS ---
class ProfileBase(BaseModel):
    name: str
    age: int
    gender: str
    relationship: str
    medical_history: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    location_zip: str
    monthly_income: Optional[float] = 0.0

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    relationship: Optional[str] = None
    medical_history: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    location_zip: Optional[str] = None
    monthly_income: Optional[float] = None

class ProfileResponse(ProfileBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- REMINDER SCHEMAS ---
class ReminderBase(BaseModel):
    medication_name: str
    dosage: str
    frequency: str
    time_of_day: str # e.g. "08:00"

class ReminderCreate(ReminderBase):
    profile_id: int

class ReminderUpdate(BaseModel):
    medication_name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    time_of_day: Optional[str] = None
    is_active: Optional[bool] = None

class ReminderResponse(ReminderBase):
    id: int
    profile_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- CONSULTATION SCHEMAS ---
class ConsultRequest(BaseModel):
    profile_id: int
    raw_symptoms: str
    duration: Optional[str] = "Unknown"
    language: Optional[str] = "English"

class HospitalInfo(BaseModel):
    name: str
    specialties: List[str]
    address: str
    contact_number: str
    distance_miles: Optional[float] = None
    routing_reason: Optional[str] = None

class SchemeInfo(BaseModel):
    name: str
    description: str
    eligibility_rules: Optional[str] = None
    benefits_details: str

class ConsultResponse(BaseModel):
    encounter_id: int
    profile_id: int
    raw_symptoms: str
    duration: str
    severity_level: str # LOW, MEDIUM, HIGH, EMERGENCY
    risk_score: float
    symptom_summary: str
    clinical_notes: str
    hospitals_recommended: List[HospitalInfo]
    benefits_identified: List[SchemeInfo]
    home_care_guidance: str
    created_at: datetime
    medications_suggested: Optional[List[Dict[str, Any]]] = []

    class Config:
        from_attributes = True

# --- DASHBOARD SCHEMAS ---
class DashboardStats(BaseModel):
    total_profiles: int
    total_encounters: int
    emergency_alerts_count: int
    active_reminders_count: int
    recent_encounters: List[Dict[str, Any]]
    risk_trends: List[Dict[str, Any]] # history of risk scores
