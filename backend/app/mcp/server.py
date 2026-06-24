import sys
import json
import logging

# Configure logging to sys.stderr so it doesn't interfere with JSON-RPC over stdout
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("healthsphere.mcp_server")

# Import database and models
try:
    from backend.app.database import SessionLocal
    from backend.app.models import HospitalMock, SchemeMock
    from backend.app.memory import memory_store
except ImportError as e:
    logger.error(f"Import error in MCP Server: {e}")
    # Enable running from within app directory too
    sys.path.append(".")
    from backend.app.database import SessionLocal
    from backend.app.models import HospitalMock, SchemeMock
    from backend.app.memory import memory_store

def list_local_hospitals(zip_code: str) -> str:
    db = SessionLocal()
    try:
        hospitals = db.query(HospitalMock).filter(HospitalMock.location_zip == zip_code).all()
        if not hospitals:
            hospitals = db.query(HospitalMock).filter(HospitalMock.location_zip == "default").all()
        result = []
        for h in hospitals:
            result.append({
                "name": h.name,
                "specialties": json.loads(h.specialties),
                "address": h.address,
                "contact_number": h.contact_number
            })
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error in tool list_local_hospitals: {e}")
        return json.dumps({"error": str(e)})
    finally:
        db.close()

def list_eligible_schemes(age: int, income: float, gender: str, zip_code: str) -> str:
    db = SessionLocal()
    try:
        schemes = db.query(SchemeMock).all()
        result = []
        for s in schemes:
            # Basic eligibility logic matching GovernmentBenefitsAgent
            eligible = True
            reason = []

            # Income rules
            if s.max_income and income > s.max_income:
                eligible = False
                reason.append(f"Income {income} exceeds scheme limit of {s.max_income}")

            # Age rules
            if s.min_age and age < s.min_age:
                eligible = False
                reason.append(f"Age {age} is below minimum requirement of {s.min_age}")

            # Scheme-specific keyword rules
            s_name_lower = s.name.lower()
            if "janani" in s_name_lower or "maternal" in s_name_lower:
                if gender.lower() != "female":
                    eligible = False
                    reason.append("Scheme only available to female patients")

            if eligible:
                result.append({
                    "name": s.name,
                    "description": s.description,
                    "eligibility_reason": "Matches age and income criteria." if not reason else "; ".join(reason),
                    "benefits_summary": s.benefits_details,
                    "application_steps": [
                        "Visit the nearest public health center or community desk.",
                        "Provide identity proof (Aadhaar Card) and income certificate.",
                        "Submit clinical assessment details to verify care requirement."
                    ]
                })
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error in tool list_eligible_schemes: {e}")
        return json.dumps({"error": str(e)})
    finally:
        db.close()

def retrieve_patient_memory(profile_id: int, query: str) -> str:
    try:
        past_encounters = memory_store.search_similar_encounters(
            profile_id=profile_id,
            current_symptoms=query,
            limit=3
        )
        return json.dumps(past_encounters, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error in tool retrieve_patient_memory: {e}")
        return json.dumps({"error": str(e)})

def handle_request(request: dict) -> dict:
    method = request.get("method")
    req_id = request.get("id")
    params = request.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "HealthSphereMCPServer",
                    "version": "1.0"
                }
            }
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "list_local_hospitals",
                        "description": "Retrieve recommended local clinics or health centers based on patient location PIN/ZIP code.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "zip_code": {"type": "string", "description": "Six-digit Indian PIN/ZIP code."}
                            },
                            "required": ["zip_code"]
                        }
                    },
                    {
                        "name": "list_eligible_schemes",
                        "description": "Check matching government welfare health schemes for a patient profile.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "age": {"type": "integer", "description": "Patient age in years."},
                                "income": {"type": "number", "description": "Family monthly income in INR."},
                                "gender": {"type": "string", "description": "Gender: Male, Female, Other."},
                                "zip_code": {"type": "string", "description": "PIN code."}
                            },
                            "required": ["age", "income", "gender", "zip_code"]
                        }
                    },
                    {
                        "name": "retrieve_patient_memory",
                        "description": "Fetch semantic historical triage logs matching symptoms for longitudinal context.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "profile_id": {"type": "integer", "description": "Unique integer ID of patient profile."},
                                "query": {"type": "string", "description": "Symptom description search query."}
                            },
                            "required": ["profile_id", "query"]
                        }
                    }
                ]
            }
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "list_local_hospitals":
            res_val = list_local_hospitals(args.get("zip_code", "default"))
        elif tool_name == "list_eligible_schemes":
            res_val = list_eligible_schemes(
                age=int(args.get("age", 30)),
                income=float(args.get("income", 0.0)),
                gender=args.get("gender", "Other"),
                zip_code=args.get("zip_code", "")
            )
        elif tool_name == "retrieve_patient_memory":
            res_val = retrieve_patient_memory(
                profile_id=int(args.get("profile_id")),
                query=args.get("query", "")
            )
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Tool '{tool_name}' not found."
                }
            }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": res_val
                    }
                ]
            }
        }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {
            "code": -32601,
            "message": f"Method '{method}' not supported."
        }
    }

def main():
    logger.info("Starting HealthSphere MCP Server on stdio...")
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except Exception as e:
            logger.error(f"Error parsing stdio JSON-RPC request: {e}")
            err_resp = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
