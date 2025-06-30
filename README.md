# ServiceNow MCP Server

A Python-based MCP (Model Context Protocol) server for interacting with ServiceNow via REST APIs. Credentials and instance URL are managed securely using environment variables.

## Features
- Secure configuration via `.env` file (no hardcoded credentials)
- REST API endpoints for ServiceNow interaction
- Easily extensible for new ServiceNow use cases

## Setup

1. **Clone the repository**
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables**
   - Copy `.env.example` to `.env` and fill in your ServiceNow instance URL, username, and password.

4. **Run the server**
   ```bash
   uvicorn mcp_server:app --reload
   ```

## Environment Variables

- `SERVICENOW_INSTANCE`: Your ServiceNow instance URL (e.g., https://dev12345.service-now.com)
- `SERVICENOW_USERNAME`: Your ServiceNow username
- `SERVICENOW_PASSWORD`: Your ServiceNow password

## Example Endpoints

### 1. Test Authentication
- **GET** `/test-auth`
- Verifies ServiceNow credentials are working.

### 2. Get Table Description
- **GET** `/table-description/{table_name}`
- Returns the description of a ServiceNow table.

### 3. Get Incident Short Description
- **GET** `/incident-short-description/{incident_number}`
- Returns the short description for a given incident number.

## Extending
Add new endpoints in `mcp_server.py` to support more ServiceNow API use cases.

## References
- [How to create your own ServiceNow MCP Server](https://www.servicenow.com/community/developer-articles/how-to-create-your-own-servicenow-mcp-server/ta-p/3298144)
- [ServiceNow REST API Documentation](https://developer.servicenow.com/dev.do#!/reference/api/rome/rest/c_TableAPI) 