from datetime import date


def create_poll(client):
    res = client.post(
        "/api/polls",
        json={
            "title": "Familientreffen",
            "description": "Abstimmung",
            "timezone": "Europe/Berlin",
            "date_range_from": "2026-03-10",
            "date_range_to": "2026-03-20",
        },
    )
    assert res.status_code == 201
    return res.json()


def test_create_poll_returns_id_and_admin_token(client):
    body = create_poll(client)
    assert "poll_id" in body
    assert isinstance(body["admin_token"], str)
    assert len(body["admin_token"]) >= 16


def test_get_poll(client):
    poll = create_poll(client)
    res = client.get(f"/api/polls/{poll['poll_id']}")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == poll["poll_id"]
    assert data["title"] == "Familientreffen"
    assert data["candidate_days"] == []


def test_set_candidate_days_requires_admin_token(client):
    poll = create_poll(client)
    res = client.patch(
        f"/api/polls/{poll['poll_id']}",
        json={"candidate_days": ["2026-03-12", "2026-03-14"]},
    )
    assert res.status_code == 403

    ok = client.patch(
        f"/api/polls/{poll['poll_id']}",
        headers={"x-admin-token": poll["admin_token"]},
        json={"candidate_days": ["2026-03-12", "2026-03-14"]},
    )
    assert ok.status_code == 200
    assert ok.json()["candidate_days"] == ["2026-03-12", "2026-03-14"]


def test_submit_vote_new(client):
    poll = create_poll(client)
    client.patch(
        f"/api/polls/{poll['poll_id']}",
        headers={"x-admin-token": poll["admin_token"]},
        json={"candidate_days": ["2026-03-12", "2026-03-14"]},
    )

    vote = client.post(
        f"/api/polls/{poll['poll_id']}/votes",
        json={
            "participant_name": "Alex",
            "participant_token": "token-12345678",
            "choices": [
                {"day": "2026-03-12", "choice": "yes"},
                {"day": "2026-03-14", "choice": "maybe"},
            ],
        },
    )
    assert vote.status_code == 200
    assert "vote_id" in vote.json()


def test_submit_vote_update_with_same_participant_token(client):
    poll = create_poll(client)
    client.patch(
        f"/api/polls/{poll['poll_id']}",
        headers={"x-admin-token": poll["admin_token"]},
        json={"candidate_days": ["2026-03-12", "2026-03-14"]},
    )

    first = client.post(
        f"/api/polls/{poll['poll_id']}/votes",
        json={
            "participant_name": "Alex",
            "participant_token": "same-token-123456",
            "choices": [
                {"day": "2026-03-12", "choice": "yes"},
                {"day": "2026-03-14", "choice": "no"},
            ],
        },
    )
    second = client.post(
        f"/api/polls/{poll['poll_id']}/votes",
        json={
            "participant_name": "Alexandra",
            "participant_token": "same-token-123456",
            "choices": [
                {"day": "2026-03-12", "choice": "no"},
                {"day": "2026-03-14", "choice": "yes"},
            ],
        },
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["vote_id"] == second.json()["vote_id"]


def test_results_scoring_and_sorting_correctness(client):
    poll = create_poll(client)
    client.patch(
        f"/api/polls/{poll['poll_id']}",
        headers={"x-admin-token": poll["admin_token"]},
        json={"candidate_days": ["2026-03-12", "2026-03-13", "2026-03-14"]},
    )

    client.post(
        f"/api/polls/{poll['poll_id']}/votes",
        json={
            "participant_name": "A",
            "participant_token": "token-a-123456",
            "choices": [
                {"day": "2026-03-12", "choice": "yes"},
                {"day": "2026-03-13", "choice": "maybe"},
                {"day": "2026-03-14", "choice": "no"},
            ],
        },
    )
    client.post(
        f"/api/polls/{poll['poll_id']}/votes",
        json={
            "participant_name": "B",
            "participant_token": "token-b-123456",
            "choices": [
                {"day": "2026-03-12", "choice": "maybe"},
                {"day": "2026-03-13", "choice": "yes"},
                {"day": "2026-03-14", "choice": "no"},
            ],
        },
    )

    res = client.get(f"/api/polls/{poll['poll_id']}/results")
    assert res.status_code == 200
    days = res.json()["sorted_days"]

    # 2026-03-12: yes(1)*2 + maybe(1)=3
    # 2026-03-13: yes(1)*2 + maybe(1)=3
    # 2026-03-14: 0
    assert days[0]["score"] == 3
    assert days[1]["score"] == 3
    assert days[2]["score"] == 0
    assert days[0]["day"] == "2026-03-12"
    assert days[1]["day"] == "2026-03-13"
    assert days[0]["is_top"] is True
    assert days[1]["is_top"] is True
