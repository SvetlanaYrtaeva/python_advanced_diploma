from io import BytesIO

from fastapi.testclient import TestClient


def test_upload_avif_media(client: TestClient):
    response = client.post(
        "/api/medias",
        headers={"api-key": "alice-key"},
        files={
            "file": (
                "test-image.avif",
                BytesIO(b"fake avif content"),
                "image/avif",
            ),
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["result"] is True
    assert isinstance(data["media_id"], int)


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


def test_follow_and_unfollow_user(client: TestClient):
    follow_response = client.post(
        "/api/users/2/follow",
        headers={"api-key": "alice-key"},
    )

    assert follow_response.status_code == 200
    assert follow_response.json()["result"] is True

    unfollow_response = client.delete(
        "/api/users/2/follow",
        headers={"api-key": "alice-key"},
    )

    assert unfollow_response.status_code == 200
    assert unfollow_response.json()["result"] is True


def test_like_and_unlike_tweet(client: TestClient):
    create_response = client.post(
        "/api/tweets",
        headers={"api-key": "alice-key"},
        json={
            "tweet_data": "Твит для лайка",
            "tweet_media_ids": [],
        },
    )

    assert create_response.status_code == 201

    tweet_id = create_response.json()["tweet_id"]

    like_response = client.post(
        f"/api/tweets/{tweet_id}/likes",
        headers={"api-key": "bob-key"},
    )

    assert like_response.status_code == 200
    assert like_response.json()["result"] is True

    unlike_response = client.delete(
        f"/api/tweets/{tweet_id}/likes",
        headers={"api-key": "bob-key"},
    )

    assert unlike_response.status_code == 200
    assert unlike_response.json()["result"] is True


def test_delete_own_tweet(client: TestClient):
    create_response = client.post(
        "/api/tweets",
        headers={"api-key": "alice-key"},
        json={
            "tweet_data": "Твит для удаления",
            "tweet_media_ids": [],
        },
    )

    tweet_id = create_response.json()["tweet_id"]

    delete_response = client.delete(
        f"/api/tweets/{tweet_id}",
        headers={"api-key": "alice-key"},
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["result"] is True


def test_user_cannot_delete_foreign_tweet(client: TestClient):
    create_response = client.post(
        "/api/tweets",
        headers={"api-key": "alice-key"},
        json={
            "tweet_data": "Твит Alice",
            "tweet_media_ids": [],
        },
    )

    tweet_id = create_response.json()["tweet_id"]

    delete_response = client.delete(
        f"/api/tweets/{tweet_id}",
        headers={"api-key": "bob-key"},
    )

    assert delete_response.status_code == 403
    assert delete_response.json()["result"] is False


def test_invalid_api_key(client: TestClient):
    response = client.get(
        "/api/users/me",
        headers={"api-key": "wrong-key"},
    )

    assert response.status_code == 401
    assert response.json()["result"] is False


def test_following_feed(client: TestClient):
    follow_response = client.post(
        "/api/users/2/follow",
        headers={"api-key": "alice-key"},
    )

    assert follow_response.status_code == 200

    tweet_response = client.post(
        "/api/tweets",
        headers={"api-key": "bob-key"},
        json={
            "tweet_data": "Твит Bob для ленты",
            "tweet_media_ids": [],
        },
    )

    assert tweet_response.status_code == 201

    feed_response = client.get(
        "/api/tweets",
        headers={"api-key": "alice-key"},
    )

    assert feed_response.status_code == 200

    data = feed_response.json()

    assert data["result"] is True
    assert isinstance(data["tweets"], list)


def test_request_without_api_key(client: TestClient):
    response = client.get("/api/users/me")

    assert response.status_code == 401
    assert response.json()["result"] is False


def test_duplicate_like(client: TestClient):
    create_response = client.post(
        "/api/tweets",
        headers={"api-key": "alice-key"},
        json={
            "tweet_data": "Tweet for duplicate like",
            "tweet_media_ids": [],
        },
    )

    tweet_id = create_response.json()["tweet_id"]

    first_like = client.post(
        f"/api/tweets/{tweet_id}/likes",
        headers={"api-key": "bob-key"},
    )

    second_like = client.post(
        f"/api/tweets/{tweet_id}/likes",
        headers={"api-key": "bob-key"},
    )

    assert first_like.status_code == 200
    assert second_like.status_code == 400
    assert second_like.json()["result"] is False


def test_user_cannot_follow_himself(client: TestClient):
    response = client.post(
        "/api/users/1/follow",
        headers={"api-key": "alice-key"},
    )

    assert response.status_code == 400
    assert response.json()["result"] is False


def test_invalid_media_type(client: TestClient):
    response = client.post(
        "/api/medias",
        headers={"api-key": "alice-key"},
        files={
            "file": (
                "document.txt",
                BytesIO(b"not an image"),
                "text/plain",
            ),
        },
    )

    assert response.status_code == 400
    assert response.json()["result"] is False
