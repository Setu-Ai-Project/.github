"""Tests for certificate generation, issuance, and the award_xp certificate hook.

Tests 1-12 cover services/certificates.py.
Test 13 covers the award_xp hook in services/progression.py.

Storage is stubbed with monkeypatch -- no network calls, no Cloudinary.
"""

from io import BytesIO

import pytest
from PIL import Image
from sqlmodel import Session, select

from models.certificate import Certificate
from models.challenge import Challenge
from models.completed_challenge import CompletedChallenge
from models.module import Module
from models.sub_module import SubModule
from models.user import User
from services.certificates import (
    ModuleNotFound,
    generate_certificate_image,
    is_module_completed,
    issue_certificate,
)
from services.progression import _execute_award_xp

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _stub_upload(monkeypatch):
    """Patch upload_image to return a stub URL without any network call."""
    calls = []

    def fake_upload(data: bytes, name: str) -> str:
        calls.append(name)
        return f"https://stub.example.com/certificates/{name}.png"

    monkeypatch.setattr("services.certificates.upload_image", fake_upload)
    return calls


def _make_user(session: Session, *, name="Test User", email="test@example.com") -> User:
    user = User(
        name=name,
        email=email,
        hashed_password="hash",
        total_xp=0,
        level=1,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _make_module(session: Session, *, title="Test Module") -> Module:
    mod = Module(title=title, description="Desc", order=1)
    session.add(mod)
    session.commit()
    session.refresh(mod)
    return mod


def _make_sub_module(session: Session, module_id: int) -> SubModule:
    sm = SubModule(title="Sub", description="Sub desc", order=1, module_id=module_id)
    session.add(sm)
    session.commit()
    session.refresh(sm)
    return sm


def _make_challenge(session: Session, sub_module_id: int, *, xp: int = 50) -> Challenge:
    ch = Challenge(sub_module_id=sub_module_id, title="Challenge", xp_reward=xp)
    session.add(ch)
    session.commit()
    session.refresh(ch)
    return ch


def _complete(session: Session, user_id: int, challenge_id: int, *, xp: int = 50) -> None:
    cc = CompletedChallenge(user_id=user_id, challenge_id=challenge_id, xp_awarded=xp)
    session.add(cc)
    session.commit()


# ---------------------------------------------------------------------------
# Test 1 -- last challenge of a module creates exactly one certificate
# ---------------------------------------------------------------------------

def test_1_last_challenge_creates_one_certificate(monkeypatch, session: Session):
    calls = _stub_upload(monkeypatch)

    user = _make_user(session)
    mod = _make_module(session)
    sm = _make_sub_module(session, mod.id)
    ch1 = _make_challenge(session, sm.id)
    ch2 = _make_challenge(session, sm.id)

    # Complete first challenge -- module not yet done
    _complete(session, user.id, ch1.id)

    # Complete last challenge -- triggers certificate
    _execute_award_xp(session, user.id, ch2.id)

    certs = session.exec(
        select(Certificate).where(
            Certificate.user_id == user.id,
            Certificate.module_id == mod.id,
        )
    ).all()
    assert len(certs) == 1
    assert certs[0].image_url == (
        f"https://stub.example.com/certificates/"
        f"certificate_user_{user.id}_module_{mod.id}.png"
    )
    assert len(calls) == 1


# ---------------------------------------------------------------------------
# Test 2 -- another challenge in that module creates no second certificate
# ---------------------------------------------------------------------------

def test_2_another_challenge_no_second_certificate(monkeypatch, session: Session):
    calls = _stub_upload(monkeypatch)

    user = _make_user(session)
    mod = _make_module(session)
    sm = _make_sub_module(session, mod.id)
    ch1 = _make_challenge(session, sm.id)
    ch2 = _make_challenge(session, sm.id)

    # Complete both -- cert issued after ch2
    _execute_award_xp(session, user.id, ch1.id)
    _execute_award_xp(session, user.id, ch2.id)

    # Add a third challenge and complete it -- module already done, no new cert
    ch3 = _make_challenge(session, sm.id)
    _execute_award_xp(session, user.id, ch3.id)

    certs = session.exec(
        select(Certificate).where(
            Certificate.user_id == user.id,
            Certificate.module_id == mod.id,
        )
    ).all()
    assert len(certs) == 1
    assert len(calls) == 1


# ---------------------------------------------------------------------------
# Test 3 -- repeating the last challenge creates no second certificate
# ---------------------------------------------------------------------------

def test_3_repeat_last_challenge_no_second_certificate(monkeypatch, session: Session):
    calls = _stub_upload(monkeypatch)

    user = _make_user(session)
    mod = _make_module(session)
    sm = _make_sub_module(session, mod.id)
    ch = _make_challenge(session, sm.id)

    _execute_award_xp(session, user.id, ch.id)   # first -- cert issued
    _execute_award_xp(session, user.id, ch.id)   # repeat -- already_completed path

    certs = session.exec(
        select(Certificate).where(
            Certificate.user_id == user.id,
            Certificate.module_id == mod.id,
        )
    ).all()
    assert len(certs) == 1
    assert len(calls) == 1


# ---------------------------------------------------------------------------
# Test 4 -- incomplete module gets no certificate
# ---------------------------------------------------------------------------

def test_4_incomplete_module_no_certificate(monkeypatch, session: Session):
    calls = _stub_upload(monkeypatch)

    user = _make_user(session)
    mod = _make_module(session)
    sm = _make_sub_module(session, mod.id)
    ch1 = _make_challenge(session, sm.id)
    _make_challenge(session, sm.id)  # ch2 left incomplete

    _execute_award_xp(session, user.id, ch1.id)

    certs = session.exec(
        select(Certificate).where(
            Certificate.user_id == user.id,
            Certificate.module_id == mod.id,
        )
    ).all()
    assert len(certs) == 0
    assert len(calls) == 0


# ---------------------------------------------------------------------------
# Test 5 -- upload_image raising still awards XP and level, response unchanged
# ---------------------------------------------------------------------------

def test_5_upload_raises_still_awards_xp(monkeypatch, session: Session):
    def exploding_upload(data: bytes, name: str) -> str:
        raise RuntimeError("Simulated storage failure")

    monkeypatch.setattr("services.certificates.upload_image", exploding_upload)

    user = _make_user(session)
    mod = _make_module(session)
    sm = _make_sub_module(session, mod.id)
    ch = _make_challenge(session, sm.id, xp=75)

    result = _execute_award_xp(session, user.id, ch.id)

    assert result["xp_awarded"] == 75
    assert result["total_xp"] == 75
    assert result["already_completed"] is False
    assert result["level"] == 1

    expected_keys = {
        "user_id", "challenge_id", "xp_awarded", "total_xp",
        "level", "previous_level", "leveled_up", "xp_to_next_level",
        "badges_unlocked", "already_completed",
    }
    assert set(result.keys()) == expected_keys

    db_user = session.get(User, user.id)
    assert db_user.total_xp == 75

    cc = session.exec(
        select(CompletedChallenge).where(
            CompletedChallenge.user_id == user.id,
            CompletedChallenge.challenge_id == ch.id,
        )
    ).first()
    assert cc is not None

    certs = session.exec(
        select(Certificate).where(Certificate.user_id == user.id)
    ).all()
    assert len(certs) == 0


# ---------------------------------------------------------------------------
# Test 6 -- generate_certificate_image returns PNG bytes, exactly 1200x850
# ---------------------------------------------------------------------------

def test_6_generate_certificate_image_returns_correct_png():
    data = generate_certificate_image("Alice", "Python Basics", "January 01, 2025")

    assert data[:8] == b"\x89PNG\r\n\x1a\n", "Output is not a valid PNG"

    img = Image.open(BytesIO(data))
    assert img.width == 1200
    assert img.height == 850
    assert img.format == "PNG"


# ---------------------------------------------------------------------------
# Test 7 -- one user's certificate is never affected by another user
# ---------------------------------------------------------------------------

def test_7_one_user_cert_not_affected_by_another(monkeypatch, session: Session):
    calls = _stub_upload(monkeypatch)

    user_a = _make_user(session, name="User A", email="a@example.com")
    user_b = _make_user(session, name="User B", email="b@example.com")

    mod = _make_module(session)
    sm = _make_sub_module(session, mod.id)
    ch = _make_challenge(session, sm.id)

    _execute_award_xp(session, user_a.id, ch.id)

    certs_a = session.exec(
        select(Certificate).where(
            Certificate.user_id == user_a.id,
            Certificate.module_id == mod.id,
        )
    ).all()
    certs_b = session.exec(
        select(Certificate).where(
            Certificate.user_id == user_b.id,
            Certificate.module_id == mod.id,
        )
    ).all()

    assert len(certs_a) == 1
    assert len(certs_b) == 0
    assert len(calls) == 1


# ---------------------------------------------------------------------------
# Test 8 -- issue_certificate twice returns the same row, one insert, upload once
# ---------------------------------------------------------------------------

def test_8_issue_certificate_idempotent(monkeypatch, session: Session):
    calls = _stub_upload(monkeypatch)

    user = _make_user(session)
    mod = _make_module(session)

    cert1 = issue_certificate(session, user, mod.id)
    cert2 = issue_certificate(session, user, mod.id)

    assert cert1.id == cert2.id
    assert cert1.image_url == cert2.image_url

    all_certs = session.exec(
        select(Certificate).where(
            Certificate.user_id == user.id,
            Certificate.module_id == mod.id,
        )
    ).all()
    assert len(all_certs) == 1
    assert len(calls) == 1


# ---------------------------------------------------------------------------
# Test 9 -- is_module_completed returns False for a module with zero challenges
# ---------------------------------------------------------------------------

def test_9_completion_helper_false_for_zero_challenges(session: Session):
    user = _make_user(session)
    mod = _make_module(session)
    _make_sub_module(session, mod.id)  # sub-module exists, but no challenges

    result = is_module_completed(session, user.id, mod.id)
    assert result is False


# ---------------------------------------------------------------------------
# Test 10 -- very long name and module title still produce 1200x850
# ---------------------------------------------------------------------------

def test_10_very_long_name_and_title_still_correct_size():
    long_name = "A" * 120
    long_title = "B" * 100

    data = generate_certificate_image(long_name, long_title, "October 22, 2026")

    img = Image.open(BytesIO(data))
    assert img.width == 1200
    assert img.height == 850


# ---------------------------------------------------------------------------
# Test 11 -- nonexistent module_id raises, upload never called, no row inserted
# ---------------------------------------------------------------------------

def test_11_nonexistent_module_raises(monkeypatch, session: Session):
    calls = _stub_upload(monkeypatch)

    user = _make_user(session)

    with pytest.raises(ModuleNotFound):
        issue_certificate(session, user, module_id=99999)

    assert len(calls) == 0

    certs = session.exec(select(Certificate).where(Certificate.user_id == user.id)).all()
    assert len(certs) == 0


# ---------------------------------------------------------------------------
# Test 12 -- after upload_image raises in award_xp, re-query confirms values persist
# ---------------------------------------------------------------------------

def test_12_upload_raises_in_award_xp_values_persist(monkeypatch, session: Session):
    def exploding_upload(data: bytes, name: str) -> str:
        raise RuntimeError("Storage down")

    monkeypatch.setattr("services.certificates.upload_image", exploding_upload)

    user = _make_user(session)
    mod = _make_module(session)
    sm = _make_sub_module(session, mod.id)
    ch = _make_challenge(session, sm.id, xp=60)

    _execute_award_xp(session, user.id, ch.id)

    db_user = session.get(User, user.id)
    assert db_user.total_xp == 60
    assert db_user.level == 1

    cc = session.exec(
        select(CompletedChallenge).where(
            CompletedChallenge.user_id == user.id,
            CompletedChallenge.challenge_id == ch.id,
        )
    ).first()
    assert cc is not None
    assert cc.xp_awarded == 60

    certs = session.exec(
        select(Certificate).where(Certificate.user_id == user.id)
    ).all()
    assert len(certs) == 0


# ---------------------------------------------------------------------------
# Test 13 -- is_module_completed raises, XP/level/response are still correct
# ---------------------------------------------------------------------------

def test_13_is_module_completed_raises_xp_and_response_intact(monkeypatch, session: Session):
    """If is_module_completed raises, the hook swallows it; XP, level, and the
    10-field response are unaffected."""

    def exploding_is_module_completed(sess, user_id, module_id):
        raise RuntimeError("Simulated DB error in completion check")

    monkeypatch.setattr(
        "services.progression.is_module_completed",
        exploding_is_module_completed,
    )

    user = _make_user(session)
    mod = _make_module(session)
    sm = _make_sub_module(session, mod.id)
    ch = _make_challenge(session, sm.id, xp=100)

    result = _execute_award_xp(session, user.id, ch.id)

    assert result["xp_awarded"] == 100
    assert result["total_xp"] == 100
    assert result["already_completed"] is False

    expected_keys = {
        "user_id", "challenge_id", "xp_awarded", "total_xp",
        "level", "previous_level", "leveled_up", "xp_to_next_level",
        "badges_unlocked", "already_completed",
    }
    assert set(result.keys()) == expected_keys

    db_user = session.get(User, user.id)
    assert db_user.total_xp == 100
