def test_create_short_link_anonymous(client):
    payload = {"original_url": "https://google.com"}
    response = client.post("/links/shorten", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["original_url"] == "https://google.com/"
    assert data["short_code"] is not None


def test_create_short_link_with_custom_alias(client):
    payload = {
        "original_url": "https://google.com",
        "custom_alias": "mygoogle"
    }
    response = client.post("/links/shorten", json=payload)

    assert response.status_code == 200
    assert response.json()["short_code"] == "mygoogle"


def test_create_short_link_duplicate_alias(client):
    payload = {
        "original_url": "https://google.com",
        "custom_alias": "dup"
    }
    client.post("/links/shorten", json=payload)
    response = client.post("/links/shorten", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Custom alias already exists"


def test_redirect_short_link(client):
    create_response = client.post("/links/shorten", json={
        "original_url": "https://google.com",
        "custom_alias": "redir"
    })
    assert create_response.status_code == 200

    response = client.get("/links/redir", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"] == "https://google.com/"


def test_stats_for_link(client):
    client.post("/links/shorten", json={
        "original_url": "https://google.com",
        "custom_alias": "stats1"
    })

    client.get("/links/stats1", follow_redirects=False)

    response = client.get("/links/stats1/stats")
    assert response.status_code == 200

    data = response.json()
    assert data["original_url"] == "https://google.com/"
    assert data["click_count"] >= 1


def test_search_by_original_url(client):
    client.post("/links/shorten", json={
        "original_url": "https://google.com",
        "custom_alias": "search1"
    })

    response = client.get("/links/search", params={"original_url": "https://google.com/"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1