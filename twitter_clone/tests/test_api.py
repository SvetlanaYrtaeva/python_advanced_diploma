from fastapi.testclient import TestClient


def test_get_my_profile(client: TestClient):
    response = client.get(
        "/api/users/me",
        headers={"api-key": "alice-key"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["result"] is True
    assert data["user"]["name"] == "Alice"


def test_create_tweet(client: TestClient):
    response = client.post(
        "/api/tweets",
        headers={"api-key": "alice-key"},
        json={
            "tweet_data": "Мой первый твит",
            "tweet_media_ids": [],
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["result"] is True
    assert isinstance(data["tweet_id"], int)


def test_follow_user(client: TestClient):
    response = client.post(
        "/api/users/2/follow",
        headers={"api-key": "alice-key"},
    )

    assert response.status_code == 200
    assert response.json()["result"] is True


def test_like_tweet(client: TestClient):
    create_response = client.post(
        "/api/tweets",
        headers={"api-key": "alice-key"},
        json={
            "tweet_data": "Твит для лайка",
            "tweet_media_ids": [],
        },
    )

    tweet_id = create_response.json()["tweet_id"]

    like_response = client.post(
        f"/api/tweets/{tweet_id}/likes",
        headers={"api-key": "bob-key"},
    )

    assert like_response.status_code == 200
    assert like_response.json()["result"] is True