# schools/config.py
from dataclasses import dataclass
from typing import Callable, Optional
import logging
import requests

from fju.http_headers import session_headers  # 或你實際使用的 Session 類型

logger = logging.getLogger(__name__)

Session = requests.Session  # 視你實際用的型別而定


@dataclass(frozen=True)
class SchoolConfig:
    key: str                            # "tku", "fju", ...
    auth_func: Callable[[], Session]    # 不吃參數，回傳已登入的 session
    endpoint: Optional[str] = None      # 有些學校可能不需要 endpoint（只登入）
    latitude: float = 25.174269373936202 # default latitude
    longitude: float = 121.45422774303604 # default longitude


def tku_auth() -> Session:
    from tku.http_headers import session_headers
    from tku.auth_module import Authenticator

    logger.info("🔐 Logging in (TKU)...")
    auth = Authenticator()
    session = auth.perform_auth()
    session.headers.update(session_headers())
    logger.info("TKU session initialized.")
    return session


def fju_auth() -> Session:
    from fju.auth_module import Authenticator
    from fju.http_headers import session_headers
    logger.info("🔐 Logging in (FJU)...")
    auth = Authenticator()
    session = auth.login()
    session.headers.update(session_headers())
    logger.info("FJU session initialized.")
    return session


SCHOOL_CONFIGS: dict[str, SchoolConfig] = {
    "tku": SchoolConfig(
        key="tku",
        auth_func=tku_auth,
        endpoint="https://iclass.tku.edu.tw",
        latitude=25.174269373936202,
        longitude=121.45422774303604
    ),
    "fju": SchoolConfig(
        key="fju",
        auth_func=fju_auth,
        endpoint="https://elearn2.fju.edu.tw",
        latitude=25.03659879562293,
        longitude=121.4328216507679
    ),
    # 未來要 100 間學校，就在這裡繼續加：
    # "abc": SchoolConfig(key="abc", auth_func=abc_auth, endpoint="https://..."),
}
