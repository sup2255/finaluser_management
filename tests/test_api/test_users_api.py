import pytest
from httpx import AsyncClient
from urllib.parse import urlencode
from app.models.user_model import UserRole
from app.services.jwt_service import decode_token
from app.utils.nickname_gen import generate_nickname


# ---------- TEST USER CREATION AND ACCESS DENIAL ---------- #
@pytest.mark.asyncio
async def test_create_user_access_denied(async_client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    user_data = {
        "nickname": generate_nickname(),
        "email": "test@example.com",
        "password": "StrongPassword#123!"
    }
    response = await async_client.post("/users/", json=user_data, headers=headers)
    assert response.status_code == 403


# ---------- TEST RETRIEVE USER ---------- #
@pytest.mark.asyncio
async def test_retrieve_user_access_allowed(async_client, admin_user, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.get(f"/users/{admin_user.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == str(admin_user.id)

@pytest.mark.asyncio
async def test_retrieve_user_access_denied(async_client, verified_user, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.get(f"/users/{verified_user.id}", headers=headers)
    assert response.status_code == 403


# ---------- TEST UPDATE USER ---------- #
@pytest.mark.asyncio
async def test_update_user_email_access_allowed(async_client, admin_user, admin_token):
    updated_data = {"email": f"updated_{admin_user.id}@example.com"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.put(f"/users/{admin_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == updated_data["email"]

@pytest.mark.asyncio
async def test_update_user_email_access_denied(async_client, verified_user, user_token):
    updated_data = {"email": f"updated_{verified_user.id}@example.com"}
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(f"/users/{verified_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 403


# ---------- TEST ROLE UPDATES ---------- #
@pytest.mark.asyncio
async def test_role_update_success(async_client, admin_token, test_user_id):
    new_role = {"role": "manager"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.put(f"/users/{test_user_id}/role", json=new_role, headers=headers)
    assert response.status_code == 200
    assert response.json()["role"] == "manager"

@pytest.mark.asyncio
async def test_role_update_invalid_role(async_client, admin_token, test_user_id):
    invalid_role = {"role": "invalid_role"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.put(f"/users/{test_user_id}/role", json=invalid_role, headers=headers)
    assert response.status_code == 422
    assert "Invalid role" in response.json()["detail"]

@pytest.mark.asyncio
async def test_role_update_unauthorized(async_client, test_user_id):
    new_role = {"role": "admin"}
    response = await async_client.put(f"/users/{test_user_id}/role", json=new_role)
    assert response.status_code == 401


# ---------- TEST LOGIN FUNCTIONALITY ---------- #
@pytest.mark.asyncio
async def test_login_success(async_client, verified_user):
    form_data = {
        "username": verified_user.email,
        "password": "MySuperPassword$1234"
    }
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    decoded_token = decode_token(data["access_token"])
    assert decoded_token["role"] == "AUTHENTICATED"

@pytest.mark.asyncio
async def test_login_incorrect_password(async_client, verified_user):
    form_data = {
        "username": verified_user.email,
        "password": "WrongPassword123!"
    }
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 401
    assert "Incorrect email or password." in response.json()["detail"]


# ---------- TEST USER LISTING ---------- #
@pytest.mark.asyncio
async def test_list_users_as_admin(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.get("/users/", headers=headers)
    assert response.status_code == 200
    assert "items" in response.json()

@pytest.mark.asyncio
async def test_list_users_as_manager(async_client, manager_token):
    headers = {"Authorization": f"Bearer {manager_token}"}
    response = await async_client.get("/users/", headers=headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_list_users_unauthorized(async_client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.get("/users/", headers=headers)
    assert response.status_code == 403  # Regular user access denied
# Test to ensure unauthorized users cannot retrieve user data
##@pytest.mark.asyncio
#async def test_retrieve_user_access_denied(async_client, verified_user, user_token):
 #   headers = {"Authorization": f"Bearer {user_token}"}
  #  response = await async_client.get(f"/users/{verified_user.id}", headers=headers)
   # assert response.status_code == 403
