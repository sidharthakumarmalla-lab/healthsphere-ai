import json
from backend.app.mcp.client import mcp_client

def lookup_local_hospitals(zip_code: str) -> str:
    """
    Search and find local clinics, primary health centers (PHCs), or community health centers (CHCs) matching a ZIP code.
    
    Args:
        zip_code: The patient's 6-digit location ZIP or PIN code.
        
    Returns:
        A JSON string containing list of matching hospital names, addresses, specialties, and contact details.
    """
    try:
        return mcp_client.call_tool("list_local_hospitals", {"zip_code": zip_code})
    except Exception as e:
        return json.dumps({"error": f"Failed to retrieve hospitals: {str(e)}"})

def lookup_welfare_benefits(age: int, income: float, gender: str, zip_code: str) -> str:
    """
    Search matching national and regional Indian government healthcare welfare schemes (e.g. PM-JAY) for which a patient is eligible.
    
    Args:
        age: The age of the patient in years.
        income: The monthly family income in INR.
        gender: The gender of the patient (Male, Female, or Other).
        zip_code: The patient's ZIP or PIN code.
        
    Returns:
        A JSON string containing list of eligible schemes, descriptions, coverage benefits, and enrollment steps.
    """
    try:
        return mcp_client.call_tool("list_eligible_schemes", {
            "age": int(age),
            "income": float(income),
            "gender": gender,
            "zip_code": zip_code
        })
    except Exception as e:
        return json.dumps({"error": f"Failed to check scheme eligibility: {str(e)}"})

def lookup_historical_memory(profile_id: int, query: str) -> str:
    """
    Retrieve past clinical assessment encounters and diagnostic summaries matching current symptoms to provide longitudinal context.
    
    Args:
        profile_id: Unique integer ID of the patient family member.
        query: Symptom search query terms.
        
    Returns:
        A JSON string listing matched past triage encounters and their clinical summaries.
    """
    try:
        return mcp_client.call_tool("retrieve_patient_memory", {
            "profile_id": int(profile_id),
            "query": query
        })
    except Exception as e:
        return json.dumps({"error": f"Failed to retrieve patient memories: {str(e)}"})
