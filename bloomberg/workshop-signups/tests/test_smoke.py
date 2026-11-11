from app.reports import attendance
from app.services import signup_service


def test_basic_signup(db):
    assert signup_service.sign_up(db, "w1", "a1") == "signed_up"
    assert attendance.roster(db, "w1") == ["a1"]
