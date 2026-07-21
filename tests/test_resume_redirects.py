from types import SimpleNamespace

from app.routers.resume import get_post_upload_redirect


def test_hr_user_redirects_to_hr_dashboard_after_upload():
    user = SimpleNamespace(role="hr")

    assert get_post_upload_redirect(user) == "/hr/dashboard"


def test_candidate_user_redirects_to_candidate_dashboard_after_upload():
    user = SimpleNamespace(role="candidate")

    assert get_post_upload_redirect(user) == "/dashboard/"
