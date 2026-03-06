from datetime import datetime, timedelta


def test_create_link_auth(client, auth_headers):
    response = client.post(
        "/links/shorten/auth",
        json={
            "original_url": "https://youtube.com",
            "custom_alias": "authlink"
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["short_code"] == "authlink"
    assert data["owner_id"] is not None


def test_update_link_auth(client, auth_headers):
    client.post(
        "/links/shorten/auth",
        json={
            "original_url": "https://youtube.com",
            "custom_alias": "editme"
        },
        headers=auth_headers
    )

    response = client.put(
        "/links/editme",
        json={"original_url": "https://wikipedia.org"},
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["original_url"] == "https://wikipedia.org/"


def test_delete_link_auth(client, auth_headers):
    client.post(
        "/links/shorten/auth",
        json={
            "original_url": "https://youtube.com",
            "custom_alias": "deleteme"
        },
        headers=auth_headers
    )

    response = client.delete("/links/deleteme", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Link deleted"


def test_update_without_auth_forbidden(client):
    response = client.put(
        "/links/unknown",
        json={"original_url": "https://wikipedia.org"}
    )

    assert response.status_code in (401, 403)


def test_create_link_with_project_name(client, auth_headers):
    response = client.post(
        "/links/shorten/auth",
        json={
            "original_url": "https://youtube.com",
            "custom_alias": "project1",
            "project_name": "analytics"
        },
        headers=auth_headers
    )

    assert response.status_code == 200


def test_get_links_by_project(client, auth_headers):
    client.post(
        "/links/shorten/auth",
        json={
            "original_url": "https://youtube.com",
            "custom_alias": "project2",
            "project_name": "analytics"
        },
        headers=auth_headers
    )

    response = client.get("/projects/analytics/links")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_expired_links_list(client):
    expired_time = (datetime.utcnow() - timedelta(minutes=1)).isoformat()

    client.post("/links/shorten", json={
        "original_url": "https://google.com",
        "custom_alias": "expired1",
        "expires_at": expired_time
    })

    response = client.get("/links/expired")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_cleanup_unused_links(client, auth_headers):
    response = client.delete("/links/cleanup", params={"days": 30}, headers=auth_headers)
    assert response.status_code == 200
    assert "deleted_links" in response.json()