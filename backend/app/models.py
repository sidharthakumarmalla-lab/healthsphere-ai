from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, TypeDecorator
from sqlalchemy.orm import relationship as sqlalchemy_relationship
import datetime
from backend.app.database import Base
from backend.app.utils.security import encrypt_data, decrypt_data

class EncryptedText(TypeDecorator):
    """Custom SQLAlchemy type for transparent Fernet encryption of text fields."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return encrypt_data(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return decrypt_data(value)

class EncryptedFloat(TypeDecorator):
    """Custom SQLAlchemy type for transparent Fernet encryption of float fields."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return encrypt_data(str(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        val_str = decrypt_data(value)
        try:
            return float(val_str)
        except (ValueError, TypeError):
            return 0.0

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    relationship = Column(String, nullable=False) # Self, Spouse, Child, Parent, etc.
    medical_history = Column(EncryptedText, default="[]") # Encrypted JSON string list
    allergies = Column(EncryptedText, default="[]") # Encrypted JSON string list
    location_zip = Column(String, nullable=False)
    monthly_income = Column(EncryptedFloat, default="0.0") # Encrypted float
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    encounters = sqlalchemy_relationship("Encounter", back_populates="profile", cascade="all, delete-orphan")
    reminders = sqlalchemy_relationship("MedicationReminder", back_populates="profile", cascade="all, delete-orphan")


class Encounter(Base):
    __tablename__ = "encounters"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    raw_symptoms = Column(Text, nullable=False)
    duration = Column(String, nullable=True)
    severity_level = Column(String, nullable=False) # LOW, MEDIUM, HIGH, EMERGENCY
    risk_score = Column(Float, nullable=False) # 0.0 to 10.0
    symptom_summary = Column(Text, nullable=True)
    clinical_notes = Column(Text, nullable=True)
    hospitals_recommended = Column(Text, default="[]") # JSON list of hospital dicts
    benefits_identified = Column(Text, default="[]") # JSON list of benefits dicts
    home_care_guidance = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    profile = sqlalchemy_relationship("Profile", back_populates="encounters")

class MedicationReminder(Base):
    __tablename__ = "medication_reminders"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    medication_name = Column(String, nullable=False)
    dosage = Column(String, nullable=False) # e.g., "500mg" or "1 tablet"
    frequency = Column(String, nullable=False) # e.g., "Daily", "Twice Daily"
    time_of_day = Column(String, nullable=False) # e.g., "08:00", "20:00" (comma-separated or single)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    profile = sqlalchemy_relationship("Profile", back_populates="reminders")

class HospitalMock(Base):
    __tablename__ = "hospital_mocks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    specialties = Column(Text, default="[]") # JSON list
    location_zip = Column(String, nullable=False)
    address = Column(String, nullable=False)
    contact_number = Column(String, nullable=False)

class SchemeMock(Base):
    __tablename__ = "scheme_mocks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    eligibility_rules = Column(Text, nullable=True) # Text description
    min_age = Column(Integer, nullable=True)
    max_income = Column(Float, nullable=True)
    benefits_details = Column(Text, nullable=False)
