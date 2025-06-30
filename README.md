# ServiceNow MCP Server

A Python-based MCP (Model Context Protocol) server for interacting with ServiceNow via REST APIs. Credentials and instance URL are managed securely using environment variables.

## Features
- Secure configuration via `.env` file (no hardcoded credentials)
- REST API endpoints for ServiceNow interaction
- Easily extensible for new ServiceNow use cases
- Comprehensive read-only access to ServiceNow data

## Available Tools (Read-Only Endpoints)

Below is a list of all available read-only tools (API endpoints) provided by this MCP server:

| Endpoint | Description |
|---|---|
| `/test-auth` | Test ServiceNow authentication and connectivity |
| `/incidents` | List recent incidents (with optional query and limit) |
| `/incident/{incident_number}` | Get details for a specific incident by number |
| `/incident-short-description/{incident_number}` | Get the short description for a specific incident |
| `/users` | List users (with optional query and limit) |
| `/user/{user_id}` | Get details for a specific user by sys_id or user_name |
| `/tables` | List available tables in ServiceNow |
| `/table-description/{table_name}` | Get the description and metadata for a ServiceNow table |
| `/table-schema/{table_name}` | Get the schema (fields) for a given table |
| `/knowledge-articles` | List knowledge base articles |
| `/knowledge-article/{article_id}` | Get details for a specific knowledge article |
| `/groups` | List user groups |
| `/group/{group_id}` | Get details for a specific group |
| `/catalog-items` | List service catalog items |
| `/catalog-item/{item_id}` | Get details for a specific catalog item |
| `/requests` | List service requests |
| `/request/{request_id}` | Get details for a specific service request |
| `/requested-items` | List requested items (RITMs) |
| `/requested-item/{ritm_id}` | Get details for a specific requested item |
| `/change-requests` | List change requests |
| `/change-request/{change_id}` | Get details for a specific change request |
| `/tasks` | List tasks |
| `/task/{task_id}` | Get details for a specific task |
| `/problems` | List problem records |
| `/problem/{problem_id}` | Get details for a specific problem record |
| `/assets` | List assets |
| `/asset/{asset_id}` | Get details for a specific asset |
| `/cmdb-items` | List configuration items (CIs) from the CMDB |
| `/cmdb-item/{ci_id}` | Get details for a specific configuration item |
| `/audit-records` | List audit records |
| `/system-logs` | List system logs |

All endpoints are **GET** only and do not modify ServiceNow data.

## MCP Resources and Prompt Support

This server is designed to be compatible with MCP clients (such as Cursor, Claude Desktop, and VS Code) that support HTTP/REST-based MCP servers. Each endpoint can be used as a "tool" or "resource" in these clients.

- **MCP Resources:**
  - Each endpoint is exposed as a REST resource and can be registered as a tool in MCP-compatible clients.
  - The `/resources` endpoint returns a machine-readable list of all available tools/resources, including their names, descriptions, input parameters, and HTTP methods. This allows MCP clients to automatically discover and register the server's capabilities.
  - **Example:**
    ```http
    GET /resources
    ```
    **Response:**
    ```json
    {
      "resources": [
        {
          "name": "get_incident",
          "description": "Get details for a specific incident by number",
          "path": "/incident/{incident_number}",
          "method": "GET",
          "parameters": [
            {"name": "incident_number", "type": "string", "description": "Incident number"}
          ]
        },
        ...
      ]
    }
    ```

- **Prompt Support:**
  - The `/prompt` endpoint allows clients to send a natural language prompt and receive a mapping to the appropriate tool/resource and parameters.
  - **Example:**
    ```http
    POST /prompt
    Content-Type: application/json
    {
      "prompt": "Get the short description for incident INC0008001"
    }
    ```
    **Response:**
    ```json
    {
      "tool": "get_incident_short_description",
      "endpoint": "/incident-short-description/INC0008001",
      "method": "GET",
      "parameters": {
        "incident_number": "INC0008001"
      }
    }
    ```
  - If the prompt cannot be mapped, the response will include an error message.

### How to Use in an MCP Client

1. **Tool Discovery:**
   - Configure your MCP client to call the `/resources` endpoint to automatically discover all available tools and their parameters.
   - The client can then present these tools in its UI or use them for auto-completion and workflow automation.

2. **Prompt-Based Invocation:**
   - Send a POST request to `/prompt` with a natural language prompt.
   - The server will respond with the mapped tool, endpoint, HTTP method, and parameters.
   - The client can then invoke the mapped endpoint directly, or present the mapping to the user for confirmation.

3. **Manual Tool Registration:**
   - If your client does not support automatic discovery, you can manually register the endpoints using the documentation above or the `/resources` output.

**Note:** The `/prompt` endpoint currently uses simple rule-based mapping. For more advanced prompt understanding, you can extend the logic or integrate with an LLM.

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

## Using the MCP Server with Popular Tools

### 1. Using with Cursor

Cursor supports integration with MCP servers for AI-driven code and workflow automation. To use this MCP server with Cursor:

- Ensure the MCP server is running (`uvicorn mcp_server:app --reload`).
- Open Cursor and go to the settings or extensions panel.
- Locate the MCP integration settings (may be under "AI" or "MCP Servers").
- Add a new MCP server with the following details:
  - **Type:** HTTP/REST
  - **URL:** `http://localhost:8000` (or your server's address)
  - **Endpoints:** As documented above
- Save and test the connection. Cursor should now be able to send requests to your MCP server and receive ServiceNow data.

**Troubleshooting:**
- Ensure the MCP server is running and accessible from your machine.
- Check for firewall or port conflicts.
- Review server logs for errors.

### 2. Using with Claude Desktop

Claude Desktop can be configured to use custom MCP servers for enhanced AI capabilities.

- Start the MCP server as above.
- Open Claude Desktop.
- Go to the Developer menu and select "Open App configuration file" (usually `claude_desktop_config.json`).
- Add or update the MCP server entry, for example:
  ```json
  {
    "mcpServers": {
      "ServiceNow": {
        "command": "python",
        "args": [
          "-m", "uvicorn", "mcp_server:app", "--reload"
        ],
        "env": {
          "SERVICENOW_INSTANCE": "https://your-instance.service-now.com",
          "SERVICENOW_USERNAME": "your-username",
          "SERVICENOW_PASSWORD": "your-password"
        }
      }
    }
  }
  ```
- Save the file and restart Claude Desktop.
- The ServiceNow MCP server should now be available as a tool within Claude Desktop.

**Troubleshooting:**
- Ensure the MCP server is running and the configuration file is correct.
- Restart Claude Desktop after changes.
- Check the MCP server logs for errors.

### 3. Using with Visual Studio Code (VS Code)

Visual Studio Code now supports MCP natively, allowing seamless integration with MCP servers for AI-powered development workflows.

#### How to Configure the MCP Server in VS Code

1. **Start the MCP server**
   ```bash
   uvicorn mcp_server:app --reload
   ```
2. **Open VS Code**
3. **Go to the Command Palette** (`Ctrl+Shift+P` or `Cmd+Shift+P`)
4. **Search for "MCP: Add Server"** (or similar, depending on your MCP extension/version)
5. **Enter the MCP server details:**
   - **Name:** ServiceNow MCP
   - **URL:** `http://localhost:8000` (or your server's address)
   - **Type:** HTTP/REST
6. **Save the configuration**
7. **Use the MCP server with AI features** (such as code completion, workflow automation, or ServiceNow data queries) directly within VS Code.

#### Example Usage
- Use the AI chat or command palette to send prompts like:
  - "Get the short description for incident INC0008001 from ServiceNow."
  - "Describe the 'incident' table in ServiceNow."
- The MCP server will process these requests and return results in the VS Code interface.

**Troubleshooting:**
- Ensure the MCP server is running and accessible from your machine.
- Check for firewall or port conflicts.
- If the MCP server does not appear, ensure you have the latest version of the MCP extension installed in VS Code.
- Review the output or logs for errors.

## Extending
Add new endpoints in `mcp_server.py` to support more ServiceNow API use cases.

## References
- [How to create your own ServiceNow MCP Server](https://www.servicenow.com/community/developer-articles/how-to-create-your-own-servicenow-mcp-server/ta-p/3298144)
- [ServiceNow REST API Documentation](https://developer.servicenow.com/dev.do#!/reference/api/rome/rest/c_TableAPI) 