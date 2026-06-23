import json
from sqlalchemy.orm import Session
from backend.app.models import HospitalMock, SchemeMock

def seed_database(db: Session):
    # Check if already seeded
    if db.query(HospitalMock).first() is not None:
        return

    print("Seeding hospital mocks...")
    hospitals = [
        # Rural / Underserved Regional Clinics (North / Rajasthan - 302001)
        {
            "name": "Community Health Centre (CHC) - Ramgarh",
            "specialties": json.dumps(["General Medicine", "Pediatrics", "Obstetrics"]),
            "location_zip": "302001",
            "address": "Main Bazar, Ramgarh Rural, Rajasthan - 302001",
            "contact_number": "+91 141 234 5678"
        },
        {
            "name": "Primary Health Centre (PHC) - Devpura",
            "specialties": json.dumps(["General OPD", "Immunization", "First Aid"]),
            "location_zip": "302001",
            "address": "Panchayat Samiti Compound, Devpura Village - 302001",
            "contact_number": "+91 141 987 6543"
        },
        # Rural Clinics (East / Bihar - 841101 / 800001)
        {
            "name": "Sub-District Hospital - Sonpur",
            "specialties": json.dumps(["General Surgery", "Orthopedics", "Emergency Care", "Maternity"]),
            "location_zip": "841101",
            "address": "Station Road, Sonpur, Saran, Bihar - 841101",
            "contact_number": "+91 6158 222 111"
        },
        {
            "name": "Primary Health Centre (PHC) - Hariharpur",
            "specialties": json.dumps(["General OPD", "Malaria Triage", "Family Planning"]),
            "location_zip": "841101",
            "address": "Near Panchayat Bhawan, Hariharpur, Bihar - 841101",
            "contact_number": "+91 6158 999 888"
        },
        # Rural Clinics (Maharashtra - 400001)
        {
            "name": "Primary Health Centre (PHC) - Karjat Rural",
            "specialties": json.dumps(["General OPD", "Snakebite Triage", "Vaccination"]),
            "location_zip": "400001",
            "address": "Karjat Rural Road, Raigad, Maharashtra - 400001",
            "contact_number": "+91 2148 222 345"
        },
        {
            "name": "Lokmanya Tilak Municipal General Hospital (Sion Hospital)",
            "specialties": json.dumps(["Trauma Care", "Pediatrics", "Cardiology", "Obstetrics & Gynecology"]),
            "location_zip": "400001",
            "address": "Sion West, Mumbai, Maharashtra - 400022",
            "contact_number": "+91 22 2407 6381"
        },
        # Rural Clinics (Central / Madhya Pradesh - 466001)
        {
            "name": "Primary Health Centre (PHC) - Sehore Rural",
            "specialties": json.dumps(["General Medicine", "Vaccination", "Dehydration Treatment"]),
            "location_zip": "466001",
            "address": "Indore-Bhopal Highway, Sehore, Madhya Pradesh - 466001",
            "contact_number": "+91 7562 254 321"
        },
        {
            "name": "District Hospital - Sehore Town",
            "specialties": json.dumps(["Intensive Care", "Pediatrics", "Cardiology Clinic", "General Surgery"]),
            "location_zip": "466001",
            "address": "Civil Lines, Sehore, Madhya Pradesh - 466001",
            "contact_number": "+91 7562 222 300"
        },
        # Default Fallback Clinics (e.g. if zip code is arbitrary)
        {
            "name": "Adarsh Community Health Clinic",
            "specialties": json.dumps(["General Medicine", "Emergency Triage", "Maternal Care"]),
            "location_zip": "default",
            "address": "National Highway 48, Village Junction, Rural Sub-Division",
            "contact_number": "+91 11 2333 4444"
        },
        {
            "name": "Sub-Centre Government Dispensary",
            "specialties": json.dumps(["First Aid", "Basic Consultations", "Fever Clinic"]),
            "location_zip": "default",
            "address": "Sector 3, Community Hall Building, Rural Ward 12",
            "contact_number": "+91 11 5555 6666"
        }
    ]

    for h in hospitals:
        hospital_model = HospitalMock(**h)
        db.add(hospital_model)

    print("Seeding government health schemes...")
    schemes = [
        {
            "name": "Ayushman Bharat PM-JAY",
            "description": "Pradhan Mantri Jan Arogya Yojana is a national public health insurance fund of the Government of India that aims to provide free access to health insurance coverage for low income earners in the country.",
            "eligibility_rules": "Families listed in SECC database (mostly rural households, landless, low monthly income below 10,000 INR, or specific occupational criteria).",
            "min_age": 0,
            "max_income": 120000.0,
            "benefits_details": "Cashless hospitalization coverage of up to INR 5,00,000 per family per year for secondary and tertiary care hospitalization across all empaneled public and private hospitals."
        },
        {
            "name": "Janani Suraksha Yojana (JSY)",
            "description": "A safe motherhood intervention under the National Health Mission (NHM) being implemented with the objective of reducing maternal and neonatal mortality by promoting institutional delivery among poor pregnant women.",
            "eligibility_rules": "All pregnant women of low-income families residing in rural areas. No age limit, focuses on institutional delivery.",
            "min_age": 18,
            "max_income": 180000.0,
            "benefits_details": "Cash assistance of INR 1,400 to rural mothers and INR 600 to urban mothers for institutional deliveries, along with free transport and immunization."
        },
        {
            "name": "Mahatma Jyotirao Phule Jan Arogya Yojana",
            "description": "A flagship health insurance scheme of the Government of Maharashtra providing cashless quality medical care to families in Maharashtra.",
            "eligibility_rules": "Families holding Yellow, Orange, or Antyodaya Anna Yojana ration cards in Maharashtra (PIN code starts with 4).",
            "min_age": 0,
            "max_income": 120000.0,
            "benefits_details": "Cashless surgical and medical treatments up to INR 1,500,000 per family per year for 996 identified procedures."
        },
        {
            "name": "Mukhyamantri Chiranjeevi Swasthya Bima Yojana",
            "description": "Rajasthan government's health insurance scheme providing cashless treatment to all families in Rajasthan.",
            "eligibility_rules": "All families residing in Rajasthan (PIN code starts with 3). Free for small/marginal farmers, contract workers, and SECC list families; others pay nominal premium.",
            "min_age": 0,
            "max_income": 250000.0,
            "benefits_details": "Cashless health cover up to INR 2,500,000 per family per year for secondary and tertiary care treatments."
        },
        {
            "name": "National Programme for Health Care of the Elderly (NPHCE)",
            "description": "A dedicated programme to address the health needs of senior citizens by providing promotional, preventive, curative, and rehabilitative services.",
            "eligibility_rules": "Senior citizens aged 60 years and above.",
            "min_age": 60,
            "max_income": 1000000.0,
            "benefits_details": "Dedicated geriatric OPDs, free medical consultations, essential medicines, and rehabilitation services at public community health centers."
        }
    ]

    for s in schemes:
        scheme_model = SchemeMock(**s)
        db.add(scheme_model)

    db.commit()
    print("Database seeding completed.")
