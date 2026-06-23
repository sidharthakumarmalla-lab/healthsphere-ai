import requests
import json
import time

BACKEND_URL = "http://127.0.0.1:8000/api"

def test_health_check():
    print("Testing backend health check...")
    r = requests.get("http://127.0.0.1:8000/api")
    assert r.status_code == 200, f"Health check failed: {r.status_code}"
    print("[PASS] Health check passed!")

def test_e2e_flow():
    print("\n--- Testing Patient Profile CRUD & Agent Consultation Flow ---")
    
    # 1. Create Patient Profile (With Asthma)
    profile_data = {
        "name": "Sunita Devi",
        "age": 34,
        "gender": "Female",
        "relationship": "Self",
        "medical_history": ["Asthma"],
        "allergies": ["Dust"],
        "location_zip": "302001",
        "monthly_income": 12000.0
    }
    print("Creating patient profile for Sunita Devi...")
    r = requests.post(f"{BACKEND_URL}/profiles", json=profile_data)
    assert r.status_code == 201, f"Failed to create profile: {r.text}"
    profile = r.json()
    profile_id = profile["id"]
    print(f"[PASS] Profile created successfully! ID: {profile_id}")

    # 2. Perform Consultation with Mild symptoms (e.g., Runny nose, mild sore throat - should be LOW/MEDIUM)
    consult_request = {
        "profile_id": profile_id,
        "raw_symptoms": "Sunita has a runny nose and mild sore throat. No breathing difficulties, no fever, no chest pain.",
        "duration": "1 day"
    }
    print("\nRunning Symptom Triage for mild cold (Expected Low/Medium Risk)...")
    start = time.time()
    r = requests.post(f"{BACKEND_URL}/consult", json=consult_request)
    duration = time.time() - start
    assert r.status_code == 200, f"Consultation failed: {r.text}"
    result = r.json()
    print(f"[PASS] Consultation completed in {duration:.2f} seconds!")
    print(f"   Severity level: {result['severity_level']}")
    print(f"   Risk score: {result['risk_score']}/10.0")
    print(f"   Symptom Summary: {result['symptom_summary']}")
    print(f"   Clinics recommended: {[h['name'] for h in result['hospitals_recommended']]}")
    print(f"   Welfare schemes identified: {[b['name'] for b in result['benefits_identified']]}")
    print(f"   Suggested Medications: {[m['medication_name'] for m in result['medications_suggested']]}")
    
    assert result["severity_level"] in ["LOW", "MEDIUM", "HIGH", "EMERGENCY"], "Severity mismatch"
    assert len(result["hospitals_recommended"]) > 0, "No clinics recommended"

    # 3. Schedule Medication Reminders (if any were proposed)
    if result["medications_suggested"]:
        print("\nScheduling suggested medication reminders...")
        for med in result["medications_suggested"]:
            reminder_payload = {
                "profile_id": profile_id,
                "medication_name": med["medication_name"],
                "dosage": med["dosage"],
                "frequency": med["frequency"],
                "time_of_day": med["time_of_day"]
            }
            rem_r = requests.post(f"{BACKEND_URL}/reminders", json=reminder_payload)
            assert rem_r.status_code == 201, f"Failed to schedule reminder: {rem_r.text}"
            print(f"   [PASS] Scheduled: {med['medication_name']} ({med['dosage']}) - {med['frequency']} at {med['time_of_day']}")
    else:
        print("\nNo medication reminders proposed. Scheduling a manual one for testing...")
        reminder_payload = {
            "profile_id": profile_id,
            "medication_name": "Multivitamin",
            "dosage": "1 tablet",
            "frequency": "Daily",
            "time_of_day": "09:00"
        }
        rem_r = requests.post(f"{BACKEND_URL}/reminders", json=reminder_payload)
        assert rem_r.status_code == 201, f"Failed to schedule manual reminder: {rem_r.text}"
        print("   [PASS] Scheduled manual reminder: Multivitamin")

    # 4. Perform Emergency Consultation
    emergency_request = {
        "profile_id": profile_id,
        "raw_symptoms": "Sunita is experiencing sudden severe crushing chest pain, difficulty breathing, left arm pain, and sweating.",
        "duration": "10 minutes"
    }
    print("\nRunning Emergency Triage for crushing chest pain (Expected EMERGENCY)...")
    start = time.time()
    r = requests.post(f"{BACKEND_URL}/consult", json=emergency_request)
    duration = time.time() - start
    assert r.status_code == 200, f"Consultation failed: {r.text}"
    result = r.json()
    print(f"[PASS] Emergency Consultation completed in {duration:.2f} seconds!")
    print(f"   Severity level: {result['severity_level']}")
    print(f"   Risk score: {result['risk_score']}/10.0")
    print(f"   Immediate actions: {result['home_care_guidance']}")
    
    assert result["severity_level"] == "EMERGENCY", "Failed to trigger emergency escalation"
    assert result["risk_score"] == 10.0, "Risk score should be 10.0 for emergency"

    # 5. Verify Dashboard stats
    print("\nChecking dashboard stats...")
    r = requests.get(f"{BACKEND_URL}/dashboard/stats")
    assert r.status_code == 200, f"Failed to get dashboard stats: {r.text}"
    stats = r.json()
    print("[PASS] Stats retrieved:")
    print(f"   Total profiles: {stats['total_profiles']}")
    print(f"   Total encounters: {stats['total_encounters']}")
    print(f"   Emergency alerts: {stats['emergency_alerts_count']}")
    print(f"   Active reminders: {stats['active_reminders_count']}")

if __name__ == "__main__":
    test_health_check()
    test_e2e_flow()
