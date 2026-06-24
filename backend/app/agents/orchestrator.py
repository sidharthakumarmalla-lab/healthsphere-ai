import json
from sqlalchemy.orm import Session
from backend.app.models import Profile, Encounter
from backend.app.memory import memory_store
from backend.app.agents.emergency import EmergencyAgent
from backend.app.agents.symptom_analysis import SymptomAnalysisAgent
from backend.app.agents.risk_assessment import RiskAssessmentAgent
from backend.app.agents.medical_research import MedicalResearchAgent
from backend.app.agents.hospital_discovery import HospitalDiscoveryAgent
from backend.app.agents.government_benefits import GovernmentBenefitsAgent
from backend.app.agents.treatment_guidance import TreatmentGuidanceAgent
from backend.app.agents.medicine_reminder import MedicineReminderAgent
from backend.app.agents.health_guardian import HealthGuardianAgent

class HealthSphereOrchestrator:
    def __init__(self):
        # Initialize all sub-agents
        self.emergency_agent = EmergencyAgent()
        self.symptom_agent = SymptomAnalysisAgent()
        self.risk_agent = RiskAssessmentAgent()
        self.research_agent = MedicalResearchAgent()
        self.hospital_agent = HospitalDiscoveryAgent()
        self.benefits_agent = GovernmentBenefitsAgent()
        self.treatment_agent = TreatmentGuidanceAgent()
        self.reminder_agent = MedicineReminderAgent()
        self.guardian_agent = HealthGuardianAgent()

    def process_consultation(self, db: Session, profile_id: int, raw_symptoms: str, duration: str = "unknown", language: str = "English") -> dict:
        # 1. Fetch Profile details
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise ValueError(f"Patient profile with ID {profile_id} not found.")

        profile_details = {
            "name": profile.name,
            "age": profile.age,
            "gender": profile.gender,
            "medical_history": profile.medical_history,
            "allergies": profile.allergies,
            "location_zip": profile.location_zip,
            "monthly_income": profile.monthly_income
        }

        # 2. Retrieve history and construct profile context using Health Guardian Memory Agent
        history_context = self.guardian_agent.synthesize_history_context(profile_id, raw_symptoms, profile_details)

        # 3. RUN Emergency Agent
        emergency_assessment = self.emergency_agent.assess(raw_symptoms, duration, language)
        
        if emergency_assessment.is_emergency:
            # Short-circuit: immediate emergency routing
            severity_level = "EMERGENCY"
            risk_score = 10.0
            symptom_summary = f"CRITICAL EMERGENCY: {emergency_assessment.reason}"
            clinical_notes = f"System identified an immediate emergency. Actions advised: {', '.join(emergency_assessment.immediate_actions)}"
            
            # Discover emergency hospitals
            hospital_resp = self.hospital_agent.discover(
                location_zip=profile.location_zip,
                symptoms=raw_symptoms,
                severity=severity_level,
                language=language
            )
            
            # Format outputs for database
            h_rec = [h.model_dump() for h in hospital_resp.recommended_hospitals]
            b_ident = []
            
            action_header = "तत्काल आवश्यक कार्रवाई (IMMEDIATE ACTIONS REQUIRED):" if language.lower() == "hindi" else "IMMEDIATE ACTIONS REQUIRED:"
            reason_header = "महत्वपूर्ण कारण (CRITICAL REASONING):" if language.lower() == "hindi" else "CRITICAL REASONING:"
            
            home_care_guidance = (
                f"**{action_header}**\n" + 
                "\n".join([f"- {action}" for action in emergency_assessment.immediate_actions]) +
                f"\n\n**{reason_header}** {emergency_assessment.reason}"
            )

            # Create Database Encounter
            encounter = Encounter(
                profile_id=profile_id,
                raw_symptoms=raw_symptoms,
                duration=duration,
                severity_level=severity_level,
                risk_score=risk_score,
                symptom_summary=symptom_summary,
                clinical_notes=clinical_notes,
                hospitals_recommended=json.dumps(h_rec),
                benefits_identified=json.dumps(b_ident),
                home_care_guidance=home_care_guidance
            )
            db.add(encounter)
            db.commit()
            db.refresh(encounter)

            # Vectorize and save memory
            mem_summary = self.guardian_agent.summarize_for_memory(
                symptoms=raw_symptoms,
                severity=severity_level,
                risk_score=risk_score,
                clinical_notes=clinical_notes
            )
            memory_store.add_encounter(encounter.id, profile_id, mem_summary)

            return {
                "encounter_id": encounter.id,
                "profile_id": profile_id,
                "raw_symptoms": raw_symptoms,
                "duration": duration,
                "severity_level": severity_level,
                "risk_score": risk_score,
                "symptom_summary": symptom_summary,
                "clinical_notes": clinical_notes,
                "hospitals_recommended": h_rec,
                "benefits_identified": b_ident,
                "home_care_guidance": home_care_guidance,
                "created_at": encounter.created_at,
                "medications_suggested": []
            }

        # 4. RUN Symptom Analysis Agent
        symptom_analysis = self.symptom_agent.analyze(raw_symptoms, history_context, language)

        # 5. RUN Risk Assessment Agent
        risk_assessment = self.risk_agent.assess(symptom_analysis.structured_summary, history_context)

        # 6. RUN Medical Research Agent
        research_result = self.research_agent.research(symptom_analysis.structured_summary, risk_assessment.severity_level, language)

        # 7. RUN Hospital Discovery Agent
        hospital_resp = self.hospital_agent.discover(
            location_zip=profile.location_zip,
            symptoms=symptom_analysis.structured_summary,
            severity=risk_assessment.severity_level,
            language=language
        )

        # 8. RUN Government Benefits Agent
        benefits_resp = self.benefits_agent.assess_benefits(
            profile_age=profile.age,
            profile_income=profile.monthly_income,
            symptoms=symptom_analysis.structured_summary,
            gender=profile.gender,
            location_zip=profile.location_zip,
            language=language
        )

        # 9. RUN Treatment Guidance Agent
        treatment_guidance = self.treatment_agent.formulate_guidance(
            symptom_summary=symptom_analysis.structured_summary,
            risk_level=risk_assessment.severity_level,
            research_summary=research_result.clinical_evidence,
            language=language
        )

        # 10. RUN Medicine Reminder Agent to extract reminders from treatment text
        med_reminders_resp = self.reminder_agent.generate_reminders(
            ", ".join(treatment_guidance.home_care_measures) + " | Notes: " + treatment_guidance.educational_notes,
            language
        )

        # 11. Compile and save to Database
        hospitals_list = [h.model_dump() for h in hospital_resp.recommended_hospitals]
        benefits_list = []
        for b in benefits_resp.eligible_schemes:
            benefits_list.append({
                "name": b.name,
                "description": b.description,
                "eligibility_rules": b.eligibility_reason,
                "benefits_details": f"Benefits: {b.benefits_summary}\n\nSteps to Apply:\n" + "\n".join([f"- {step}" for step in b.application_steps])
            })
        
        # Multilingual header mapping
        if language.lower() == "hindi":
            home_header = "### घरेलू उपचार एवं उपाय (Home Care Recommendations)\n"
            warning_header = "\n\n### गंभीर चेतावनी लक्षण (Warning Signs / Red Flags)\n"
            step_header = "\n\n### अनुशंसित अगले कदम (Recommended Next Steps)\n"
            insight_header = "\n\n### चिकित्सा अंतर्दृष्टि (Medical Insights)\n"
            disclaimer_header = "\n\n**अस्वीकरण (Disclaimer):** *"
        else:
            home_header = "### Home Care Recommendations\n"
            warning_header = "\n\n### Warning Signs (Red Flags)\n"
            step_header = "\n\n### Recommended Next Steps\n"
            insight_header = "\n\n### Medical Insights\n"
            disclaimer_header = "\n\n**Disclaimer:** *"

        home_care_formatted = (
            home_header +
            "\n".join([f"- {measure}" for measure in treatment_guidance.home_care_measures]) +
            warning_header +
            "\n".join([f"- {sign}" for sign in treatment_guidance.warning_signs]) +
            step_header +
            "\n".join([f"- {step}" for step in treatment_guidance.recommended_next_steps]) +
            insight_header + f"{treatment_guidance.educational_notes}" +
            disclaimer_header + f"{treatment_guidance.clinical_disclaimer}*"
        )

        encounter = Encounter(
            profile_id=profile_id,
            raw_symptoms=raw_symptoms,
            duration=duration,
            severity_level=risk_assessment.severity_level,
            risk_score=risk_assessment.risk_score,
            symptom_summary=symptom_analysis.structured_summary,
            clinical_notes=research_result.clinical_evidence,
            hospitals_recommended=json.dumps(hospitals_list),
            benefits_identified=json.dumps(benefits_list),
            home_care_guidance=home_care_formatted
        )
        db.add(encounter)
        db.commit()
        db.refresh(encounter)

        # 12. RUN Health Guardian Agent to summarize and index into Vector Memory
        mem_summary = self.guardian_agent.summarize_for_memory(
            symptoms=symptom_analysis.structured_summary,
            severity=risk_assessment.severity_level,
            risk_score=risk_assessment.risk_score,
            clinical_notes=research_result.clinical_evidence
        )
        memory_store.add_encounter(encounter.id, profile_id, mem_summary)

        # 13. Formulate medications suggested for front-end automated setup
        meds_suggested = [r.model_dump() for r in med_reminders_resp.proposed_reminders]

        return {
            "encounter_id": encounter.id,
            "profile_id": profile_id,
            "raw_symptoms": raw_symptoms,
            "duration": duration,
            "severity_level": risk_assessment.severity_level,
            "risk_score": risk_assessment.risk_score,
            "symptom_summary": symptom_analysis.structured_summary,
            "clinical_notes": research_result.clinical_evidence,
            "hospitals_recommended": hospitals_list,
            "benefits_identified": benefits_list,
            "home_care_guidance": home_care_formatted,
            "created_at": encounter.created_at,
            "medications_suggested": meds_suggested
        }

# Global Orchestrator instance
orchestrator = HealthSphereOrchestrator()
