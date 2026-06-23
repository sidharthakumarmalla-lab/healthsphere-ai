import requests
import json
import time

BACKEND_URL = "http://127.0.0.1:8000/api"

def test_indian_localization():
    print("--- Running Indian Version Integration Tests ---")
    
    # 1. Create Patient in Maharashtra (PIN 400001)
    mh_patient = {
        "name": "Ramesh Sawant",
        "age": 45,
        "gender": "Male",
        "relationship": "Self",
        "medical_history": ["Hypertension (High BP)"],
        "allergies": [],
        "location_zip": "400001",
        "monthly_income": 9500.0 # eligible for Mahatma Jyotirao Phule scheme
    }
    print("Creating MH profile...")
    r = requests.post(f"{BACKEND_URL}/profiles", json=mh_patient)
    assert r.status_code == 201
    mh_prof_id = r.json()["id"]
    print(f"[PASS] MH Patient Profile created! ID: {mh_prof_id}")

    # 2. Perform consultation in HINDI for mild cold
    consult_request = {
        "profile_id": mh_prof_id,
        "raw_symptoms": "Ramesh has had a fever, mild sore throat, and a stuffed nose for 2 days. He is also feeling a bit dehydrated.",
        "duration": "2 days",
        "language": "Hindi"
    }
    
    print("\nRunning Symptom Triage in HINDI...")
    start = time.time()
    r = requests.post(f"{BACKEND_URL}/consult", json=consult_request)
    duration = time.time() - start
    assert r.status_code == 200, f"Consultation failed: {r.text}"
    result = r.json()
    print(f"[PASS] Consultation completed in {duration:.2f} seconds!")
    print(f"   Severity level: {result['severity_level']}")
    print(f"   Risk score: {result['risk_score']}/10.0")
    
    # Secure printing of Hindi summary to prevent terminal crash
    try:
        print(f"   Symptom Summary (Expected Hindi): {result['symptom_summary']}")
    except UnicodeEncodeError:
        print("   Symptom Summary: [Unicode print skipped in current terminal]")

    try:
        print(f"   Home Care Guidance Preview: {result['home_care_guidance'][:120]}...")
    except UnicodeEncodeError:
        print("   Home Care Guidance: [Unicode print skipped in current terminal]")
    
    # Verify Indian public clinics recommended
    recommended_hospitals = [h['name'] for h in result['hospitals_recommended']]
    print(f"   Clinics recommended: {recommended_hospitals}")
    assert any("Karjat" in name or "Sion" in name for name in recommended_hospitals), "Local MH clinics not found"

    # Verify Maharashtra scheme matched
    recommended_schemes = [b['name'] for b in result['benefits_identified']]
    print(f"   Welfare schemes identified: {recommended_schemes}")
    assert any("Mahatma Jyotirao Phule" in name for name in recommended_schemes), "MJPJAY scheme not matched"

    # Verify Indian medicine mapping & Hindi name
    print(f"   Suggested Medications (Expected Indian/Hindi):")
    for m in result['medications_suggested']:
        try:
            print(f"   - {m['medication_name']} ({m['dosage']}): {m['frequency']}")
        except UnicodeEncodeError:
            print(f"   - [Medication print skipped due to Unicode encoding]")

    # 3. Create Patient in Rajasthan (PIN 302001)
    rj_patient = {
        "name": "Kamla Devi",
        "age": 28,
        "gender": "Female",
        "relationship": "Spouse",
        "medical_history": ["Pregnancy"],
        "allergies": [],
        "location_zip": "302001",
        "monthly_income": 14000.0 # eligible for Chiranjeevi & Janani Suraksha
    }
    print("\nCreating RJ profile...")
    r = requests.post(f"{BACKEND_URL}/profiles", json=rj_patient)
    assert r.status_code == 201
    rj_prof_id = r.json()["id"]
    print(f"[PASS] RJ Patient Profile created! ID: {rj_prof_id}")

    # 4. Perform consultation in English for pregnancy check
    consult_request_rj = {
        "profile_id": rj_prof_id,
        "raw_symptoms": "Kamla is 6 months pregnant and is having mild backache and swelling in her ankles. No bleeding, no severe pain.",
        "duration": "3 days",
        "language": "English"
    }
    print("\nRunning Maternal Triage in English...")
    r = requests.post(f"{BACKEND_URL}/consult", json=consult_request_rj)
    assert r.status_code == 200
    result_rj = r.json()
    print(f"   Clinics recommended: {[h['name'] for h in result_rj['hospitals_recommended']]}")
    
    recommended_schemes_rj = [b['name'] for b in result_rj['benefits_identified']]
    print(f"   Welfare schemes identified: {recommended_schemes_rj}")
    
    # Verify Rajasthan scheme & maternal scheme matched
    assert any("Chiranjeevi" in name for name in recommended_schemes_rj), "Chiranjeevi scheme not matched"
    assert any("Janani Suraksha" in name for name in recommended_schemes_rj), "Janani Suraksha Yojana not matched"
    print("[PASS] All Indian Version Integration Tests passed!")

if __name__ == "__main__":
    test_indian_localization()
