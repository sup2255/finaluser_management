def test_create_user(client):
    response = client.post("/register", json={
        "email": "newuser@example.com",
        "password": "Secure*1234"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "newuser@example.com"
