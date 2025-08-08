from curl_cffi.requests import Session

from core.config import settings
from core.logging_config import log


def login_to_freenet(session: Session, email: str, password: str) -> str:
    """
    Warms up the session and logs into Freenet, returning the access token.
    Raises an exception on failure.
    """
    log.info(f"[{email}] Warming up session...")
    session.get(
        settings.LOGIN_PAGE_URL,
        headers={"Referer": "https://www.google.com/"},
        timeout=30,
    )
    session.get(
        settings.OAUTH_HANDSHAKE_URL,
        headers={
            "Origin": settings.LOGIN_PAGE_URL.rstrip("/"),
            "Referer": settings.LOGIN_PAGE_URL,
        },
        timeout=30,
    )
    log.info(f"[{email}] Session warmed up.")

    login_payload = {
        "grant_type": "password",
        "username": email,
        "password": password,
        "world": "2",
        "webLogin": "true",
    }
    resp = session.post(
        settings.LOGIN_URL,
        data=login_payload,
        auth=(settings.CLIENT_ID, settings.CLIENT_SECRET),
        timeout=30,
    )
    resp.raise_for_status()
    access_token = resp.json()["access_token"]

    log.success(f"[{email}] Login successful.")
    return access_token
