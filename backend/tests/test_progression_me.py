"""Tests for GET /progress/me endpoint."""

from datetime import datetime, timezone
import pytest
from sqlmodel import Session, select

from config.progression_rules import xp_to_next_level
from main import app
from middleware.auth import get_current_user_id
from models.badge import Badge
from models.certificate import Certificate
from models.module import Module
from models.user import User
from models.user_badge import UserBadge


def _create_user(
    session: Session,
    clerk_id: str = "clerk_test_123",
    email: str = "test@example.com",
    total_xp: int = 0,
    level: int = 1,
) -> User:
    user = User(
        name="Test Learner",
        email=email,
        hashed_password="hashed_test_password",
        clerk_user_id=clerk_id,
        total_xp=total_xp,
        level=level,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def test_progress_me_brand_new_user(client, session: Session):
    """Brand-new user: 200, level 1, total_xp 0, xp_to_next_level matches progression_rules, empty badges & certificates."""
    user = _create_user(session, clerk_id="clerk_newbie", email="newbie@example.com", total_xp=0, level=1)
    app.dependency_overrides[get_current_user_id] = lambda: "clerk_newbie"

    response = client.get("/progress/me")

    assert response.status_code == 200
    data = response.json()
    assert data["level"] == 1
    assert data["total_xp"] == 0
    assert data["xp_to_next_level"] == xp_to_next_level(0)
    assert data["badges"] == []
    assert data["certificates"] == []


def test_progress_me_user_with_badges(client, session: Session):
    """User with two badges: both returned with slug, name, awarded_at, in order."""
    user = _create_user(session, clerk_id="clerk_badged", email="badged@example.com")
    app.dependency_overrides[get_current_user_id] = lambda: "clerk_badged"

    badge_a = Badge(slug="first_steps", name="First Steps", rule_type="xp_total", rule_value=10)
    badge_b = Badge(slug="getting_warm", name="Getting Warm", rule_type="xp_total", rule_value=50)
    session.add_all([badge_a, badge_b])
    session.commit()
    session.refresh(badge_a)
    session.refresh(badge_b)

    t1 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 1, 2, 12, 0, 0, tzinfo=timezone.utc)

    # Insert out of order to ensure database ordering is exercised
    ub2 = UserBadge(user_id=user.id, badge_id=badge_b.id, awarded_at=t2)
    ub1 = UserBadge(user_id=user.id, badge_id=badge_a.id, awarded_at=t1)
    session.add_all([ub2, ub1])
    session.commit()

    response = client.get("/progress/me")

    assert response.status_code == 200
    data = response.json()
    assert len(data["badges"]) == 2
    assert data["badges"][0]["slug"] == "first_steps"
    assert data["badges"][0]["name"] == "First Steps"
    assert data["badges"][0]["awarded_at"] is not None
    assert data["badges"][1]["slug"] == "getting_warm"
    assert data["badges"][1]["name"] == "Getting Warm"
    assert data["badges"][1]["awarded_at"] is not None
    # Verify ascending order
    assert data["badges"][0]["awarded_at"] < data["badges"][1]["awarded_at"]


def test_progress_me_user_with_certificate(client, session: Session):
    """User with a certificate: returned with module_id, image_url, issued_at."""
    user = _create_user(session, clerk_id="clerk_certified", email="certified@example.com")
    app.dependency_overrides[get_current_user_id] = lambda: "clerk_certified"

    mod = Module(title="Foundations", description="Module 1", order=1)
    session.add(mod)
    session.commit()
    session.refresh(mod)

    issued_time = datetime(2026, 2, 1, 15, 30, 0, tzinfo=timezone.utc)
    cert = Certificate(
        user_id=user.id,
        module_id=mod.id,
        image_url="https://setuai.dev/certs/mod1.png",
        issued_at=issued_time,
    )
    session.add(cert)
    session.commit()

    response = client.get("/progress/me")

    assert response.status_code == 200
    data = response.json()
    assert len(data["certificates"]) == 1
    c = data["certificates"][0]
    assert c["module_id"] == mod.id
    assert c["image_url"] == "https://setuai.dev/certs/mod1.png"
    assert c["issued_at"] is not None


def test_progress_me_level_2_user(client, session: Session):
    """User with some XP and level 2: values and xp_to_next_level are correct."""
    user = _create_user(
        session,
        clerk_id="clerk_lvl2",
        email="lvl2@example.com",
        total_xp=180,
        level=2,
    )
    app.dependency_overrides[get_current_user_id] = lambda: "clerk_lvl2"

    response = client.get("/progress/me")

    assert response.status_code == 200
    data = response.json()
    assert data["total_xp"] == 180
    assert data["level"] == 2
    assert data["xp_to_next_level"] == xp_to_next_level(180)


def test_progress_me_no_token_returns_401(client, monkeypatch):
    """No token: returns 401."""
    monkeypatch.setenv("CLERK_SECRET_KEY", "sk_test_fake")
    # Ensure no dependency override is present for auth
    app.dependency_overrides.pop(get_current_user_id, None)

    response = client.get("/progress/me")

    assert response.status_code == 401


def test_progress_me_valid_token_unknown_user_returns_404(client, session: Session):
    """Valid token but no local user: 404 with 'User not found', and no user row is created."""
    app.dependency_overrides[get_current_user_id] = lambda: "clerk_ghost_user"

    users_before = len(session.exec(select(User)).all())

    response = client.get("/progress/me")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

    # Confirm no user record was created
    users_after = len(session.exec(select(User)).all())
    assert users_after == users_before
    assert (
        session.exec(select(User).where(User.clerk_user_id == "clerk_ghost_user")).first()
        is None
    )


def test_progress_me_not_captured_by_progress_id_route(client, session: Session):
    """/progress/me is not captured by the existing /progress/{id} route (no 422)."""
    user = _create_user(session, clerk_id="clerk_route_check", email="route@example.com")
    app.dependency_overrides[get_current_user_id] = lambda: "clerk_route_check"

    response = client.get("/progress/me")

    # If /{progress_id} had captured it, "me" would fail int conversion and return 422
    assert response.status_code == 200
    assert response.status_code != 422

    # Also prove existing /{progress_id} still works as expected (404 for unknown progress id)
    id_response = client.get("/progress/9999")
    assert id_response.status_code == 404
    assert id_response.json()["detail"] == "Progress not found"


def test_progress_me_does_not_leak_other_user_data(client, session: Session):
    """Another user's badges and certificates never appear in the response."""
    user_a = _create_user(session, clerk_id="clerk_user_a", email="a@example.com")
    user_b = _create_user(session, clerk_id="clerk_user_b", email="b@example.com")

    # Award badge and certificate to user_b only
    badge = Badge(slug="secret_badge", name="Secret Badge", rule_type="xp_total", rule_value=1)
    mod = Module(title="Mod B", description="desc", order=1)
    session.add_all([badge, mod])
    session.commit()
    session.refresh(badge)
    session.refresh(mod)

    ub = UserBadge(user_id=user_b.id, badge_id=badge.id)
    cert = Certificate(user_id=user_b.id, module_id=mod.id, image_url="https://secret.png")
    session.add_all([ub, cert])
    session.commit()

    # Query as user_a -> should see nothing
    app.dependency_overrides[get_current_user_id] = lambda: "clerk_user_a"
    res_a = client.get("/progress/me")
    assert res_a.status_code == 200
    data_a = res_a.json()
    assert data_a["badges"] == []
    assert data_a["certificates"] == []

    # Query as user_b -> should see their badge and certificate
    app.dependency_overrides[get_current_user_id] = lambda: "clerk_user_b"
    res_b = client.get("/progress/me")
    assert res_b.status_code == 200
    data_b = res_b.json()
    assert len(data_b["badges"]) == 1
    assert data_b["badges"][0]["slug"] == "secret_badge"
    assert len(data_b["certificates"]) == 1
    assert data_b["certificates"][0]["image_url"] == "https://secret.png"
