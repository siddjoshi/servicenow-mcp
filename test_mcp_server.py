import pytest
from httpx import AsyncClient
from fastapi import status
from mcp_server import app
from unittest.mock import patch, AsyncMock

# Helper to mock ServiceNow API responses
def mock_servicenow_get(endpoint, params=None):
    # Map endpoint to mock data
    if endpoint.startswith("/api/now/table/sys_user?") or endpoint == "/api/now/table/sys_user":
        return {"result": [{"sys_id": "user1", "user_name": "testuser"}]}
    if endpoint.startswith("/api/now/table/incident?") or endpoint == "/api/now/table/incident":
        return {"result": [{"number": "INC0001", "short_description": "Test incident"}]}
    if endpoint.startswith("/api/now/table/sys_db_object"):
        return {"result": [{"name": "incident", "label": "Incident"}]}
    if endpoint.startswith("/api/now/table/sys_dictionary"):
        return {"result": [{"element": "number", "column_label": "Number"}]}
    if endpoint.startswith("/api/now/table/kb_knowledge"):
        return {"result": [{"sys_id": "kb1", "short_description": "Test KB"}]}
    if endpoint.startswith("/api/now/table/sys_user_group"):
        return {"result": [{"sys_id": "group1", "name": "Test Group"}]}
    if endpoint.startswith("/api/now/table/sc_cat_item"):
        return {"result": [{"sys_id": "cat1", "name": "Test Catalog Item"}]}
    if endpoint.startswith("/api/now/table/sc_request"):
        return {"result": [{"sys_id": "req1", "number": "REQ0001"}]}
    if endpoint.startswith("/api/now/table/sc_req_item"):
        return {"result": [{"sys_id": "ritm1", "number": "RITM0001"}]}
    if endpoint.startswith("/api/now/table/change_request"):
        return {"result": [{"sys_id": "chg1", "number": "CHG0001"}]}
    if endpoint.startswith("/api/now/table/task"):
        return {"result": [{"sys_id": "task1", "number": "TASK0001"}]}
    if endpoint.startswith("/api/now/table/problem"):
        return {"result": [{"sys_id": "prob1", "number": "PRB0001"}]}
    if endpoint.startswith("/api/now/table/alm_asset"):
        return {"result": [{"sys_id": "asset1", "name": "Test Asset"}]}
    if endpoint.startswith("/api/now/table/cmdb_ci"):
        return {"result": [{"sys_id": "ci1", "name": "Test CI"}]}
    if endpoint.startswith("/api/now/table/sys_audit"):
        return {"result": [{"sys_id": "audit1", "fieldname": "Test Field"}]}
    if endpoint.startswith("/api/now/table/syslog"):
        return {"result": [{"sys_id": "log1", "message": "Test Log"}]}
    return {"result": []}

@pytest.mark.asyncio
@patch("mcp_server.servicenow_get", new_callable=lambda: AsyncMock(side_effect=mock_servicenow_get))
async def test_all_list_endpoints(mock_get):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        endpoints = [
            "/incidents", "/users", "/tables", "/knowledge-articles", "/groups", "/catalog-items", "/requests", "/requested-items", "/change-requests", "/tasks", "/problems", "/assets", "/cmdb-items", "/audit-records", "/system-logs"
        ]
        for ep in endpoints:
            resp = await ac.get(ep)
            assert resp.status_code == status.HTTP_200_OK
            assert isinstance(resp.json(), list) or isinstance(resp.json(), dict)

@pytest.mark.asyncio
@patch("mcp_server.servicenow_get", new_callable=lambda: AsyncMock(side_effect=mock_servicenow_get))
async def test_all_detail_endpoints_success(mock_get):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        detail_endpoints = [
            ("/incident/INC0001", "number"),
            ("/user/user1", "sys_id"),
            ("/knowledge-article/kb1", "sys_id"),
            ("/group/group1", "sys_id"),
            ("/catalog-item/cat1", "sys_id"),
            ("/request/req1", "sys_id"),
            ("/requested-item/ritm1", "sys_id"),
            ("/change-request/chg1", "sys_id"),
            ("/task/task1", "sys_id"),
            ("/problem/prob1", "sys_id"),
            ("/asset/asset1", "sys_id"),
            ("/cmdb-item/ci1", "sys_id"),
        ]
        for ep, key in detail_endpoints:
            resp = await ac.get(ep)
            assert resp.status_code == status.HTTP_200_OK
            assert key in resp.json()

@pytest.mark.asyncio
@patch("mcp_server.servicenow_get", new_callable=lambda: AsyncMock(return_value={"result": []}))
async def test_all_detail_endpoints_not_found(mock_get):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        detail_endpoints = [
            "/incident/doesnotexist",
            "/user/doesnotexist",
            "/knowledge-article/doesnotexist",
            "/group/doesnotexist",
            "/catalog-item/doesnotexist",
            "/request/doesnotexist",
            "/requested-item/doesnotexist",
            "/change-request/doesnotexist",
            "/task/doesnotexist",
            "/problem/doesnotexist",
            "/asset/doesnotexist",
            "/cmdb-item/doesnotexist",
        ]
        for ep in detail_endpoints:
            resp = await ac.get(ep)
            assert resp.status_code == status.HTTP_404_NOT_FOUND 