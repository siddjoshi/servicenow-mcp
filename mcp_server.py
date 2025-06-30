import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import httpx

# Load environment variables from .env file
load_dotenv()

SERVICENOW_INSTANCE = os.getenv("SERVICENOW_INSTANCE")
SERVICENOW_USERNAME = os.getenv("SERVICENOW_USERNAME")
SERVICENOW_PASSWORD = os.getenv("SERVICENOW_PASSWORD")

if not all([SERVICENOW_INSTANCE, SERVICENOW_USERNAME, SERVICENOW_PASSWORD]):
    raise RuntimeError("Please set SERVICENOW_INSTANCE, SERVICENOW_USERNAME, and SERVICENOW_PASSWORD in your .env file.")

app = FastAPI(title="ServiceNow MCP Server")

# Helper function to make authenticated requests to ServiceNow
async def servicenow_get(endpoint: str, params: dict = None):
    url = f"{SERVICENOW_INSTANCE}{endpoint}"
    auth = (SERVICENOW_USERNAME, SERVICENOW_PASSWORD)
    async with httpx.AsyncClient() as client:
        response = await client.get(url, auth=auth, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

@app.get("/test-auth", summary="Test ServiceNow authentication")
async def test_auth():
    """Test ServiceNow credentials by calling a simple endpoint."""
    try:
        # Use a simple endpoint to test authentication
        data = await servicenow_get("/api/now/table/sys_user?sysparm_limit=1")
        return {"success": True, "result": data}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {e}")

@app.get("/table-description/{table_name}", summary="Get ServiceNow table description")
async def get_table_description(table_name: str):
    """Get the description of a ServiceNow table."""
    try:
        data = await servicenow_get(f"/api/now/table/sys_db_object", params={"sysparm_query": f"name={table_name}", "sysparm_fields": "label,super_class_name,sys_name,description"})
        if not data.get("result"):
            raise HTTPException(status_code=404, detail="Table not found.")
        return data["result"][0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/incident-short-description/{incident_number}", summary="Get short description for an incident")
async def get_incident_short_description(incident_number: str):
    """Get the short description for a given incident number."""
    try:
        params = {
            "sysparm_fields": "short_description",
            "sysparm_query": f"number={incident_number}"
        }
        data = await servicenow_get("/api/now/table/incident", params=params)
        if not data.get("result"):
            raise HTTPException(status_code=404, detail="Incident not found.")
        return {"incident_number": incident_number, "short_description": data["result"][0]["short_description"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 