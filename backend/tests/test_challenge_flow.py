"""End-to-end test of the full challenge -> session -> bug submission -> XP flow."""
from app.models.challenge import Challenge, ChallengeCategory


def _make_challenge(db_session, **overrides) -> Challenge:
    category = ChallengeCategory(name="Functional", slug="functional-cat", description="desc")
    db_session.add(category)
    db_session.commit()

    challenge = Challenge(
        category_id=category.id,
        title=overrides.get("title", "Sample Challenge"),
        description="Find the bug.",
        difficulty="beginner",
        type="functional",
        base_xp=50,
        is_published=True,
    )
    db_session.add(challenge)
    db_session.commit()
    db_session.refresh(challenge)
    return challenge


def test_list_and_get_challenges(client, db_session):
    _make_challenge(db_session, title="Listable Challenge")
    resp = client.get("/api/v1/challenges")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["title"] == "Listable Challenge"

    detail_resp = client.get(f"/api/v1/challenges/{items[0]['id']}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["description"] == "Find the bug."


def test_filter_challenges_by_type(client, db_session):
    _make_challenge(db_session, title="Functional One")
    resp = client.get("/api/v1/challenges", params={"type": "functional"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp_empty = client.get("/api/v1/challenges", params={"type": "security"})
    assert resp_empty.status_code == 200
    assert resp_empty.json() == []


def test_start_challenge_requires_auth(client, db_session):
    challenge = _make_challenge(db_session)
    resp = client.post(f"/api/v1/challenges/{challenge.id}/start")
    assert resp.status_code == 401


def test_full_bug_submission_flow_awards_xp_and_levels_up(client, db_session, register_and_login):
    challenge = _make_challenge(db_session, title="XP Flow Challenge")
    _, headers = register_and_login("xpflow@example.com", "xpflowuser", "Password123!", role="tester")

    start_resp = client.post(f"/api/v1/challenges/{challenge.id}/start", headers=headers)
    assert start_resp.status_code == 200
    session_body = start_resp.json()
    assert session_body["status"] == "active"

    submit_resp = client.post(
        f"/api/v1/challenges/{challenge.id}/submit-bug",
        headers=headers,
        json={
            "title": "Checkout total is wrong",
            "description": "Totals miscalculate with discount codes.",
            "steps_to_reproduce": "1. Add item 2. Apply code 3. Observe total",
            "actual_result": "Total is negative",
            "expected_result": "Total should never be negative",
            "severity": "critical",
            "priority": "urgent",
        },
    )
    assert submit_resp.status_code == 200, submit_resp.text
    body = submit_resp.json()
    assert body["xp_awarded"] == 100
    assert body["new_xp_total"] == 100
    assert body["new_level"] == 2
    assert body["status"] == "accepted"

    me_resp = client.get("/api/v1/users/me", headers=headers)
    profile = me_resp.json()["profile"]
    assert profile["xp_total"] == 100
    assert profile["level"] == 2
    assert profile["bugs_found_count"] == 1

    tx_resp = client.get("/api/v1/xp/me/transactions", headers=headers)
    assert tx_resp.status_code == 200
    transactions = tx_resp.json()
    assert len(transactions) == 1
    assert transactions[0]["amount"] == 100


def test_submit_bug_without_active_session_fails(client, db_session, register_and_login):
    challenge = _make_challenge(db_session, title="No Session Challenge")
    _, headers = register_and_login("nosession@example.com", "nosessionuser", "Password123!")

    resp = client.post(
        f"/api/v1/challenges/{challenge.id}/submit-bug",
        headers=headers,
        json={
            "title": "Some bug",
            "description": "desc",
            "steps_to_reproduce": "steps",
            "actual_result": "actual",
            "expected_result": "expected",
            "severity": "low",
        },
    )
    assert resp.status_code == 400


def test_developer_role_cannot_submit_bug(client, db_session, register_and_login):
    challenge = _make_challenge(db_session, title="Role Guard Challenge")
    _, headers = register_and_login(
        "devrole@example.com", "devroleuser", "Password123!", role="developer"
    )
    client.post(f"/api/v1/challenges/{challenge.id}/start", headers=headers)

    resp = client.post(
        f"/api/v1/challenges/{challenge.id}/submit-bug",
        headers=headers,
        json={
            "title": "Bug",
            "description": "desc",
            "steps_to_reproduce": "steps",
            "actual_result": "actual",
            "expected_result": "expected",
            "severity": "low",
        },
    )
    assert resp.status_code == 403


def test_duplicate_bug_awards_zero_xp(client, db_session, register_and_login):
    challenge = _make_challenge(db_session, title="Duplicate Challenge")
    _, headers = register_and_login("dupbug@example.com", "dupbuguser", "Password123!")
    client.post(f"/api/v1/challenges/{challenge.id}/start", headers=headers)

    resp = client.post(
        f"/api/v1/challenges/{challenge.id}/submit-bug",
        headers=headers,
        json={
            "title": "Already known bug",
            "description": "desc",
            "steps_to_reproduce": "steps",
            "actual_result": "actual",
            "expected_result": "expected",
            "severity": "high",
            "is_duplicate": True,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["xp_awarded"] == 0
    assert body["status"] == "duplicate"


def test_levels_endpoint_returns_table(client):
    resp = client.get("/api/v1/xp/levels")
    assert resp.status_code == 200
    levels = resp.json()["levels"]
    assert levels[0] == {"level": 1, "xp_required": 0}
    assert levels[1] == {"level": 2, "xp_required": 100}
    assert levels[4] == {"level": 5, "xp_required": 1000}
