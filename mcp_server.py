import os
from fastapi import FastAPI, HTTPException, Request
from dotenv import load_dotenv
import httpx
from typing import List, Dict, Any

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

# --- Extended Read-Only Endpoints ---

@app.get("/incidents", summary="List incidents")
async def list_incidents(limit: int = 10, query: str = None):
    """List recent incidents (optionally filter by query)."""
    params = {"sysparm_limit": limit}
    if query:
        params["sysparm_query"] = query
    data = await servicenow_get("/api/now/table/incident", params=params)
    return data["result"]

@app.get("/incident/{incident_number}", summary="Get incident details")
async def get_incident(incident_number: str):
    """Get details for a specific incident by number."""
    params = {"sysparm_query": f"number={incident_number}", "sysparm_limit": 1}
    data = await servicenow_get("/api/now/table/incident", params=params)
    if not data.get("result"):
        raise HTTPException(status_code=404, detail="Incident not found.")
    return data["result"][0]

@app.get("/users", summary="List users")
async def list_users(limit: int = 10, query: str = None):
    """List users (optionally filter by query)."""
    params = {"sysparm_limit": limit}
    if query:
        params["sysparm_query"] = query
    data = await servicenow_get("/api/now/table/sys_user", params=params)
    return data["result"]

@app.get("/user/{user_id}", summary="Get user details")
async def get_user(user_id: str):
    """Get details for a specific user by sys_id or user_name."""
    # Try by sys_id first, then by user_name
    params = {"sysparm_query": f"sys_id={user_id}", "sysparm_limit": 1}
    data = await servicenow_get("/api/now/table/sys_user", params=params)
    if data.get("result"):
        return data["result"][0]
    # Try by user_name
    params = {"sysparm_query": f"user_name={user_id}", "sysparm_limit": 1}
    data = await servicenow_get("/api/now/table/sys_user", params=params)
    if not data.get("result"):
        raise HTTPException(status_code=404, detail="User not found.")
    return data["result"][0]

@app.get("/tables", summary="List available tables")
async def list_tables(limit: int = 20, query: str = None):
    """List available tables in ServiceNow."""
    params = {"sysparm_limit": limit}
    if query:
        params["sysparm_query"] = query
    data = await servicenow_get("/api/now/table/sys_db_object", params=params)
    return data["result"]

@app.get("/table-schema/{table_name}", summary="Get table schema")
async def get_table_schema(table_name: str):
    """Get the schema (fields) for a given table."""
    params = {"sysparm_query": f"name={table_name}", "sysparm_fields": "name,label,super_class_name,description"}
    data = await servicenow_get("/api/now/table/sys_db_object", params=params)
    if not data.get("result"):
        raise HTTPException(status_code=404, detail="Table not found.")
    # Get fields for the table
    fields_data = await servicenow_get("/api/now/table/sys_dictionary", params={"sysparm_query": f"name={table_name}", "sysparm_fields": "element,column_label,internal_type,mandatory,max_length,reference"})
    return {"table": data["result"][0], "fields": fields_data["result"]}

# Knowledge Articles
@app.get("/knowledge-articles", summary="List knowledge articles")
async def list_knowledge_articles(limit: int = 10, query: str = None):
    params = {"sysparm_limit": limit}
    if query:
        params["sysparm_query"] = query
    data = await servicenow_get("/api/now/table/kb_knowledge", params=params)
    return data["result"]

@app.get("/knowledge-article/{article_id}", summary="Get knowledge article details")
async def get_knowledge_article(article_id: str):
    params = {"sysparm_query": f"sys_id={article_id}", "sysparm_limit": 1}
    data = await servicenow_get("/api/now/table/kb_knowledge", params=params)
    if not data.get("result"):
        raise HTTPException(status_code=404, detail="Knowledge article not found.")
    return data["result"][0]

# Groups
@app.get("/groups", summary="List groups")
async def list_groups(limit: int = 10, query: str = None):
    params = {"sysparm_limit": limit}
    if query:
        params["sysparm_query"] = query
    data = await servicenow_get("/api/now/table/sys_user_group", params=params)
    return data["result"]

@app.get("/group/{group_id}", summary="Get group details")
async def get_group(group_id: str):
    params = {"sysparm_query": f"sys_id={group_id}", "sysparm_limit": 1}
    data = await servicenow_get("/api/now/table/sys_user_group", params=params)
    if not data.get("result"):
        raise HTTPException(status_code=404, detail="Group not found.")
    return data["result"][0]

# Catalog Items
@app.get("/catalog-items", summary="List catalog items")
async def list_catalog_items(limit: int = 10, query: str = None):
    params = {"sysparm_limit": limit}
    if query:
        params["sysparm_query"] = query
    data = await servicenow_get("/api/now/table/sc_cat_item", params=params)
    return data["result"]

@app.get("/catalog-item/{item_id}", summary="Get catalog item details")
async def get_catalog_item(item_id: str):
    params = {"sysparm_query": f"sys_id={item_id}", "sysparm_limit": 1}
    data = await servicenow_get("/api/now/table/sc_cat_item", params=params)
    if not data.get("result"):
        raise HTTPException(status_code=404, detail="Catalog item not found.")
    return data["result"][0]

# Requests
@app.get("/requests", summary="List requests")
async def list_requests(limit: int = 10, query: str = None):
    params = {"sysparm_limit": limit}
    if query:
        params["sysparm_query"] = query
    data = await servicenow_get("/api/now/table/sc_request", params=params)
    return data["result"]

@app.get("/request/{request_id}", summary="Get request details")
async def get_request(request_id: str):
    params = {"sysparm_query": f"sys_id={request_id}", "sysparm_limit": 1}
    data = await servicenow_get("/api/now/table/sc_request", params=params)
    if not data.get("result"):
        raise HTTPException(status_code=404, detail="Request not found.")
    return data["result"][0]

# Requested Items
@app.get("/requested-items", summary="List requested items (RITMs)")
async def list_requested_items(limit: int = 10, query: str = None):
    params = {"sysparm_limit": limit}
    if query:
        params["sysparm_query"] = query
    data = await servicenow_get("/api/now/table/sc_req_item", params=params)
    return data["result"]

@app.get("/requested-item/{ritm_id}", summary="Get requested item details")
async def get_requested_item(ritm_id: str):
    params = {"sysparm_query": f"sys_id={ritm_id}", "sysparm_limit": 1}
    data = await servicenow_get("/api/now/table/sc_req_item", params=params)
    if not data.get("result"):
        raise HTTPException(status_code=404, detail="Requested item not found.")
    return data["result"][0]

# Change Requests
@app.get("/change-requests", summary="List change requests")
async def list_change_requests(limit: int = 10, query: str = None):
    params = {"sysparm_limit": limit}
    if query:
        params["sysparm_query"] = query
    data = await servicenow_get("/api/now/table/change_request", params=params)
    return data["result"]

@app.get("/change-request/{change_id}", summary="Get change request details")
async def get_change_request(change_id: str):
    params = {"sysparm_query": f"sys_id={change_id}", "sysparm_limit": 1}
    data = await servicenow_get("/api/now/table/change_request", params=params)
    if not data.get("result"):
        raise HTTPException(status_code=404, detail="Change request not found.")
    return data["result"][0]

# Tasks
@app.get("/tasks", summary="List tasks")
async def list_tasks(limit: int = 10, query: str = None):
    params = {"sysparm_limit": limit}
    if query:
        params["sysparm_query"] = query
    data = await servicenow_get("/api/now/table/task", params=params)
    return data["result"]

@app.get("/task/{task_id}", summary="Get task details")
async def get_task(task_id: str):
    params = {"sysparm_query": f"sys_id={task_id}", "sysparm_limit": 1}
    data = await servicenow_get("/api/now/table/task", params=params)
    if not data.get("result"):
        raise HTTPException(status_code=404, detail="Task not found.")
    return data["result"][0]

# Problems
@app.get("/problems", summary="List problems")
async def list_problems(limit: int = 10, query: str = None):
    params = {"sysparm_limit": limit}
    if query:
        params["sysparm_query"] = query
    data = await servicenow_get("/api/now/table/problem", params=params)
    return data["result"]

@app.get("/problem/{problem_id}", summary="Get problem details")
async def get_problem(problem_id: str):
    params = {"sysparm_query": f"sys_id={problem_id}", "sysparm_limit": 1}
    data = await servicenow_get("/api/now/table/problem", params=params)
    if not data.get("result"):
        raise HTTPException(status_code=404, detail="Problem not found.")
    return data["result"][0]

# Assets
@app.get("/assets", summary="List assets")
async def list_assets(limit: int = 10, query: str = None):
    params = {"sysparm_limit": limit}
    if query:
        params["sysparm_query"] = query
    data = await servicenow_get("/api/now/table/alm_asset", params=params)
    return data["result"]

@app.get("/asset/{asset_id}", summary="Get asset details")
async def get_asset(asset_id: str):
    params = {"sysparm_query": f"sys_id={asset_id}", "sysparm_limit": 1}
    data = await servicenow_get("/api/now/table/alm_asset", params=params)
    if not data.get("result"):
        raise HTTPException(status_code=404, detail="Asset not found.")
    return data["result"][0]

# Configuration Items (CMDB)
@app.get("/cmdb-items", summary="List configuration items (CIs)")
async def list_cmdb_items(limit: int = 10, query: str = None):
    params = {"sysparm_limit": limit}
    if query:
        params["sysparm_query"] = query
    data = await servicenow_get("/api/now/table/cmdb_ci", params=params)
    return data["result"]

@app.get("/cmdb-item/{ci_id}", summary="Get configuration item details")
async def get_cmdb_item(ci_id: str):
    params = {"sysparm_query": f"sys_id={ci_id}", "sysparm_limit": 1}
    data = await servicenow_get("/api/now/table/cmdb_ci", params=params)
    if not data.get("result"):
        raise HTTPException(status_code=404, detail="Configuration item not found.")
    return data["result"][0]

# Audit Records
@app.get("/audit-records", summary="List audit records")
async def list_audit_records(limit: int = 10, query: str = None):
    params = {"sysparm_limit": limit}
    if query:
        params["sysparm_query"] = query
    data = await servicenow_get("/api/now/table/sys_audit", params=params)
    return data["result"]

# System Logs
@app.get("/system-logs", summary="List system logs")
async def list_system_logs(limit: int = 10, query: str = None):
    params = {"sysparm_limit": limit}
    if query:
        params["sysparm_query"] = query
    data = await servicenow_get("/api/now/table/syslog", params=params)
    return data["result"]

# --- MCP /resources and /prompt endpoints ---

# Define tool/resource metadata statically for now
MCP_RESOURCES = [
    {
        "name": "test_auth",
        "description": "Test ServiceNow authentication and connectivity",
        "path": "/test-auth",
        "method": "GET",
        "parameters": []
    },
    {
        "name": "list_incidents",
        "description": "List recent incidents (with optional query and limit)",
        "path": "/incidents",
        "method": "GET",
        "parameters": [
            {"name": "limit", "type": "integer", "description": "Number of incidents to return"},
            {"name": "query", "type": "string", "description": "ServiceNow query string (optional)"}
        ]
    },
    {
        "name": "get_incident",
        "description": "Get details for a specific incident by number",
        "path": "/incident/{incident_number}",
        "method": "GET",
        "parameters": [
            {"name": "incident_number", "type": "string", "description": "Incident number"}
        ]
    },
    {
        "name": "get_incident_short_description",
        "description": "Get the short description for a specific incident",
        "path": "/incident-short-description/{incident_number}",
        "method": "GET",
        "parameters": [
            {"name": "incident_number", "type": "string", "description": "Incident number"}
        ]
    },
    {
        "name": "list_users",
        "description": "List users (with optional query and limit)",
        "path": "/users",
        "method": "GET",
        "parameters": [
            {"name": "limit", "type": "integer", "description": "Number of users to return"},
            {"name": "query", "type": "string", "description": "ServiceNow query string (optional)"}
        ]
    },
    {
        "name": "get_user",
        "description": "Get details for a specific user by sys_id or user_name",
        "path": "/user/{user_id}",
        "method": "GET",
        "parameters": [
            {"name": "user_id", "type": "string", "description": "User sys_id or user_name"}
        ]
    },
    {
        "name": "list_tables",
        "description": "List available tables in ServiceNow",
        "path": "/tables",
        "method": "GET",
        "parameters": [
            {"name": "limit", "type": "integer", "description": "Number of tables to return"},
            {"name": "query", "type": "string", "description": "ServiceNow query string (optional)"}
        ]
    },
    {
        "name": "get_table_description",
        "description": "Get the description and metadata for a ServiceNow table",
        "path": "/table-description/{table_name}",
        "method": "GET",
        "parameters": [
            {"name": "table_name", "type": "string", "description": "Table name"}
        ]
    },
    {
        "name": "get_table_schema",
        "description": "Get the schema (fields) for a given table",
        "path": "/table-schema/{table_name}",
        "method": "GET",
        "parameters": [
            {"name": "table_name", "type": "string", "description": "Table name"}
        ]
    },
    # ... Add all other endpoints similarly ...
    # For brevity, not all endpoints are listed here, but you would include all from the README table
]

@app.get("/resources", summary="List all available MCP resources/tools")
async def get_resources():
    """Return a list of all available tools/resources with metadata."""
    return {"resources": MCP_RESOURCES}

@app.post("/prompt", summary="Map a prompt to a tool/resource")
async def prompt_tool(request: Request):
    """Accept a prompt and map it to a tool/resource (basic pattern matching)."""
    data = await request.json()
    prompt = data.get("prompt", "").lower()
    # Simple rule-based mapping
    if "short description" in prompt and "incident" in prompt:
        # Extract incident number
        import re
        match = re.search(r"inc\d+", prompt, re.IGNORECASE)
        if match:
            inc_num = match.group(0).upper()
            return {
                "tool": "get_incident_short_description",
                "endpoint": f"/incident-short-description/{inc_num}",
                "method": "GET",
                "parameters": {"incident_number": inc_num}
            }
    if "list users" in prompt or "show users" in prompt:
        return {
            "tool": "list_users",
            "endpoint": "/users",
            "method": "GET",
            "parameters": {}
        }
    if "incident" in prompt and "details" in prompt:
        match = re.search(r"inc\d+", prompt, re.IGNORECASE)
        if match:
            inc_num = match.group(0).upper()
            return {
                "tool": "get_incident",
                "endpoint": f"/incident/{inc_num}",
                "method": "GET",
                "parameters": {"incident_number": inc_num}
            }
    # Add more rules as needed for other endpoints
    return {"error": "Could not map prompt to a tool. Please rephrase or use a supported pattern."} 