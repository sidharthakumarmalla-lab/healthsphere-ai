import json
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import datetime

from backend.app.database import engine, Base, get_db
from backend.app import models, schemas
from backend.app.seed_data import seed_database
from backend.app.agents.orchestrator import orchestrator

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HealthSphere AI Backend", version="1.0.0")

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed database on startup
@app.on_event("startup")
def startup_event():
    db = next(get_db())
    try:
        seed_database(db)
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "healthy", "platform": "HealthSphere AI Multi-Agent Platform"}

@app.get("/api")
@app.get("/api/")
def read_api_root():
    return {"status": "healthy"}

# --- PROFILE ENDPOINTS ---

def map_profile_to_response(db_profile: models.Profile) -> schemas.ProfileResponse:
    profile_dict = {
        "id": db_profile.id,
        "name": db_profile.name,
        "age": db_profile.age,
        "gender": db_profile.gender,
        "relationship": db_profile.relationship,
        "medical_history": json.loads(db_profile.medical_history) if db_profile.medical_history else [],
        "allergies": json.loads(db_profile.allergies) if db_profile.allergies else [],
        "location_zip": db_profile.location_zip,
        "monthly_income": db_profile.monthly_income,
        "created_at": db_profile.created_at
    }
    return schemas.ProfileResponse.model_validate(profile_dict)

@app.post("/api/profiles", response_model=schemas.ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(profile: schemas.ProfileCreate, db: Session = Depends(get_db)):
    db_profile = models.Profile(
        name=profile.name,
        age=profile.age,
        gender=profile.gender,
        relationship=profile.relationship,
        medical_history=json.dumps(profile.medical_history),
        allergies=json.dumps(profile.allergies),
        location_zip=profile.location_zip,
        monthly_income=profile.monthly_income
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return map_profile_to_response(db_profile)

@app.get("/api/profiles", response_model=List[schemas.ProfileResponse])
def get_profiles(db: Session = Depends(get_db)):
    profiles = db.query(models.Profile).all()
    return [map_profile_to_response(p) for p in profiles]

@app.get("/api/profiles/{profile_id}", response_model=schemas.ProfileResponse)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return map_profile_to_response(profile)

@app.delete("/api/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    db.delete(profile)
    db.commit()
    return None

# --- CONSULTATION / ORCHESTRATION ---

@app.post("/api/consult", response_model=schemas.ConsultResponse)
def consult_agents(request: schemas.ConsultRequest, db: Session = Depends(get_db)):
    try:
        results = orchestrator.process_consultation(
            db=db,
            profile_id=request.profile_id,
            raw_symptoms=request.raw_symptoms,
            duration=request.duration,
            language=request.language
        )
        return results
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-Agent Execution Error: {str(e)}")

@app.get("/api/encounters/profile/{profile_id}", response_model=List[schemas.ConsultResponse])
def get_encounters_by_profile(profile_id: int, db: Session = Depends(get_db)):
    encounters = db.query(models.Encounter).filter(models.Encounter.profile_id == profile_id).order_by(models.Encounter.created_at.desc()).all()
    res_list = []
    for e in encounters:
        res = schemas.ConsultResponse(
            encounter_id=e.id,
            profile_id=e.profile_id,
            raw_symptoms=e.raw_symptoms,
            duration=e.duration or "unknown",
            severity_level=e.severity_level,
            risk_score=e.risk_score,
            symptom_summary=e.symptom_summary or "",
            clinical_notes=e.clinical_notes or "",
            hospitals_recommended=json.loads(e.hospitals_recommended) if e.hospitals_recommended else [],
            benefits_identified=json.loads(e.benefits_identified) if e.benefits_identified else [],
            home_care_guidance=e.home_care_guidance or "",
            created_at=e.created_at,
            medications_suggested=[]
        )
        res_list.append(res)
    return res_list

# --- MEDICATION REMINDERS ---

@app.post("/api/reminders", response_model=schemas.ReminderResponse, status_code=status.HTTP_201_CREATED)
def create_reminder(reminder: schemas.ReminderCreate, db: Session = Depends(get_db)):
    db_reminder = models.MedicationReminder(
        profile_id=reminder.profile_id,
        medication_name=reminder.medication_name,
        dosage=reminder.dosage,
        frequency=reminder.frequency,
        time_of_day=reminder.time_of_day,
        is_active=True
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

@app.get("/api/profiles/{profile_id}/reminders", response_model=List[schemas.ReminderResponse])
def get_reminders(profile_id: int, db: Session = Depends(get_db)):
    reminders = db.query(models.MedicationReminder).filter(models.MedicationReminder.profile_id == profile_id).all()
    return reminders

@app.put("/api/reminders/{reminder_id}", response_model=schemas.ReminderResponse)
def update_reminder(reminder_id: int, reminder_update: schemas.ReminderUpdate, db: Session = Depends(get_db)):
    db_reminder = db.query(models.MedicationReminder).filter(models.MedicationReminder.id == reminder_id).first()
    if not db_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    update_data = reminder_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_reminder, key, value)
        
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

@app.delete("/api/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    db_reminder = db.query(models.MedicationReminder).filter(models.MedicationReminder.id == reminder_id).first()
    if not db_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    db.delete(db_reminder)
    db.commit()
    return None

# --- DASHBOARD ENDPOINT ---

@app.get("/api/dashboard/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_profiles = db.query(models.Profile).count()
    total_encounters = db.query(models.Encounter).count()
    emergency_alerts_count = db.query(models.Encounter).filter(models.Encounter.severity_level == "EMERGENCY").count()
    active_reminders_count = db.query(models.MedicationReminder).filter(models.MedicationReminder.is_active == True).count()
    
    # Recent 5 encounters across the platform
    recent = db.query(models.Encounter).order_by(models.Encounter.created_at.desc()).limit(5).all()
    recent_encounters = []
    for r in recent:
        prof = db.query(models.Profile).filter(models.Profile.id == r.profile_id).first()
        recent_encounters.append({
            "encounter_id": r.id,
            "patient_name": prof.name if prof else "Unknown",
            "symptoms": r.symptom_summary or r.raw_symptoms[:40] + "...",
            "severity_level": r.severity_level,
            "risk_score": r.risk_score,
            "created_at": r.created_at.isoformat()
        })
        
    # Get risk trends (chronological list of risk scores of last 10 encounters)
    trends = db.query(models.Encounter).order_by(models.Encounter.created_at.asc()).limit(15).all()
    risk_trends = []
    for t in trends:
        prof = db.query(models.Profile).filter(models.Profile.id == t.profile_id).first()
        risk_trends.append({
            "date": t.created_at.strftime("%Y-%m-%d %H:%M"),
            "risk_score": t.risk_score,
            "patient": prof.name if prof else "Unknown",
            "severity": t.severity_level
        })

    return {
        "total_profiles": total_profiles,
        "total_encounters": total_encounters,
        "emergency_alerts_count": emergency_alerts_count,
        "active_reminders_count": active_reminders_count,
        "recent_encounters": recent_encounters,
        "risk_trends": risk_trends
    }
