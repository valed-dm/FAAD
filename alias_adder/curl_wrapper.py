import random

from curl_cffi.requests import Session

from core.config import settings
from core.logging_config import log


def create_session(proxy_config: dict) -> Session:
    """
    Creates a curl_cffi Session with a random browser profile and proxy config.
    """
    profile = random.choice(settings.BROWSER_PROFILES)
    session = Session(impersonate=profile, proxies=proxy_config)
    log.debug(f"Created session with profile: {profile}")
    return session
