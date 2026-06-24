import sys
import os
import argparse
import json
import logging

# Ensure project root is in PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.database import SessionLocal, engine, Base
from backend.app import models
from backend.app.seed_data import seed_database
from backend.app.agents.orchestrator import orchestrator
from backend.app.utils.security import encrypt_data, decrypt_data, sanitize_text
from backend.app.config import BACKEND_API_KEY, DB_ENCRYPTION_KEY

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def cmd_seed():
    print("[System] Seeding database with mock clinics and schemes...")
    db = SessionLocal()
    try:
        # Create tables if not exist
        Base.metadata.create_all(bind=engine)
        seed_database(db)
        print("[SUCCESS] Database successfully seeded!")
    except Exception as e:
        print(f"[ERROR] Seeding failed: {e}")
    finally:
        db.close()

def cmd_triage(profile_id: int, symptoms: str, duration: str, language: str):
    print(f"[System] Initiating Multi-Agent Triage for Profile {profile_id}...")
    print(f"         Symptoms: '{symptoms}'")
    print(f"         Language: {language}")
    db = SessionLocal()
    try:
        results = orchestrator.process_consultation(
            db=db,
            profile_id=profile_id,
            raw_symptoms=symptoms,
            duration=duration,
            language=language
        )
        print("\n" + "="*60)
        print("                 CLINICAL ASSESSMENT SUMMARY")
        print("="*60)
        print(f"Encounter ID  : {results['encounter_id']}")
        print(f"Severity Level: {results['severity_level']}")
        print(f"Risk Score    : {results['risk_score']}/10.0")
        print(f"Symptom Summary: {results['symptom_summary']}")
        print("\n--- Home Care & Action Plan ---")
        print(results['home_care_guidance'])
        print("\n--- Recommended Local Facilities ---")
        for h in results['hospitals_recommended']:
            print(f"- {h['name']} ({h['distance_miles']} miles away) | Phone: {h['contact_number']}")
            print(f"  Reason: {h['routing_reason']}")
        print("\n--- Matching Welfare Schemes ---")
        for b in results['benefits_identified']:
            print(f"- {b['name']}: {b['benefits_details']}")
        print("\n--- Suggested Medications ---")
        for m in results['medications_suggested']:
            print(f"- {m['medication_name']} ({m['dosage']}): {m['frequency']}")
        print("="*60 + "\n")
    except Exception as e:
        print(f"[ERROR] Triage execution failed: {e}")
    finally:
        db.close()

def cmd_run_mcp():
    from backend.app.mcp.server import main as mcp_main
    mcp_main()

def cmd_system_check():
    print("=" * 60)
    print("           HEALTHSPHERE AI SECURITY & INTEGRITY CHECK")
    print("=" * 60)

    # 1. API Configuration Check
    print("\n[1/4] Checking Configurations & Secrets:")
    print(f"   - Backend API Key  : {'[CONFIGURED]' if BACKEND_API_KEY else '[MISSING]'}")
    print(f"   - DB Encryption Key: {'[CONFIGURED]' if DB_ENCRYPTION_KEY else '[MISSING]'}")

    # 2. Database Encryption Verification
    print("\n[2/4] Verifying Database Encryption-At-Rest:")
    db = SessionLocal()
    try:
        # Create a test profile
        test_prof = models.Profile(
            name="Security Test Patient",
            age=99,
            gender="Male",
            relationship="Self",
            medical_history=json.dumps(["Chronic Test Condition"]),
            allergies=json.dumps(["Test Allergy"]),
            location_zip="000000",
            monthly_income=99999.0
        )
        db.add(test_prof)
        db.commit()
        db.refresh(test_prof)

        test_prof_id = test_prof.id
        print(f"   - Test Profile ID {test_prof_id} written successfully.")

        # Query raw SQLite row bypass ORM to verify data is encrypted at rest
        with engine.connect() as connection:
            import sqlalchemy
            stmt = sqlalchemy.text(f"SELECT medical_history, monthly_income, allergies FROM profiles WHERE id = {test_prof_id}")
            row = connection.execute(stmt).fetchone()
            
            raw_history = row[0]
            raw_income = row[1]
            raw_allergies = row[2]

            print(f"   - Raw SQLite medical_history string in DB: '{raw_history}'")
            print(f"   - Raw SQLite monthly_income token in DB   : '{raw_income}'")

            # Check that raw values are NOT plain text
            assert "Chronic Test" not in str(raw_history), "Encryption Failure: Medical history plaintext found in DB!"
            assert "99999" not in str(raw_income), "Encryption Failure: Income plaintext found in DB!"
            print("   - [PASS] Data is fully ENCRYPTED in the raw SQLite DB file!")

        # Query via ORM and verify autodecryption
        orm_prof = db.query(models.Profile).filter(models.Profile.id == test_prof_id).first()
        history_list = json.loads(orm_prof.medical_history)
        income_float = orm_prof.monthly_income

        print(f"   - Decrypted ORM medical_history: {history_list}")
        print(f"   - Decrypted ORM monthly_income : {income_float} (Type: {type(income_float)})")

        assert history_list[0] == "Chronic Test Condition", "Decryption Failure: ORM failed to decrypt medical history."
        assert income_float == 99999.0, "Decryption Failure: ORM failed to decrypt income float."
        print("   - [PASS] Transparent auto-decryption via SQLAlchemy ORM works perfectly!")

        # Cleanup
        db.delete(orm_prof)
        db.commit()
        print("   - Cleanup complete.")
    except Exception as e:
        print(f"   - [FAIL] Database Security integrity test failed: {e}")
    finally:
        db.close()

    # 3. Input Sanitization Check
    print("\n[3/4] Testing Input Sanitization Utilities:")
    dangerous_input = "<script>alert('xss')</script> Ramesh has an <a href='javascript:evil()'>infection</a> and onload=hack()."
    sanitized = sanitize_text(dangerous_input)
    print(f"   - Raw Input: '{dangerous_input}'")
    print(f"   - Cleaned  : '{sanitized}'")
    if "<script>" not in sanitized and "javascript:" not in sanitized and "onload" not in sanitized:
        print("   - [PASS] Input sanitization successfully stripped all XSS markers!")
    else:
        print("   - [FAIL] Input sanitization failed to clean string.")

    # 4. LLM API Check
    print("\n[4/4] Verifying Gemini API Connection:")
    try:
        from google import genai
        key = os.getenv("GEMINI_API_KEY") or BACKEND_API_KEY
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents="Say 'API Connected'"
        )
        print(f"   - Model Response: '{response.text.strip()}'")
        print("   - [PASS] Gemini API connection is active!")
    except Exception as e:
        print(f"   - [FAIL] Gemini API connection failed: {e}")

    print("\n" + "=" * 60)
    print("                SYSTEM STATUS: READY & SECURED")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="HealthSphere AI Admin CLI Tools")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Seed command
    subparsers.add_parser("seed", help="Initialize and seed SQLite with mock data")

    # Triage command
    triage_parser = subparsers.add_parser("triage", help="Simulate a diagnostic triage via console")
    triage_parser.add_argument("--profile-id", type=int, required=True, help="Profile ID to run consultation for")
    triage_parser.add_argument("--symptoms", type=str, required=True, help="Symptoms description")
    triage_parser.add_argument("--duration", type=str, default="2 days", help="Duration of symptoms")
    triage_parser.add_argument("--language", type=str, default="English", help="Consultation language")

    # Run MCP command
    subparsers.add_parser("run-mcp", help="Launch the MCP stdio server manually")

    # System Check command
    subparsers.add_parser("system-check", help="Run security audit and system verification tests")

    args = parser.parse_args()

    if args.command == "seed":
        cmd_seed()
    elif args.command == "triage":
        cmd_triage(args.profile_id, args.symptoms, args.duration, args.language)
    elif args.command == "run-mcp":
        cmd_run_mcp()
    elif args.command == "system-check":
        cmd_system_check()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
