import os
import requests
from urllib.parse import urlparse, parse_qs, urljoin
import urllib3
import logging
from dotenv import load_dotenv
from ui.login import login, login_with_captcha_url
from schools.http_headers import session_headers
from bs4 import BeautifulSoup

urllib3.disable_warnings()
logger = logging.getLogger(__name__)


class Authenticator:
    def __init__(
        self, username: str, password: str, captcha_num: str, captcha_key: str
    ) -> None:
        self.username = username
        self.password = password
        self.captcha_num = captcha_num
        self.captcha_key = captcha_key
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({"Referer": "https://icidentity.asia.edu.tw/"})

    @classmethod
    async def create(cls) -> "Authenticator":
        load_dotenv()
        username = os.getenv("STUDENTID")
        password = os.getenv("PASSWORD")
        captcha_num = ""
        captcha_key = ""

        if not username or not password:
            logger.warning("STUDENTID or PASSWORD not set. Prompting for credentials.")
            username, password, captcha_num, captcha_key = await login_with_captcha_url(
                "https://tcidentity.asia.edu.tw/auth/realms/asia/captcha/code"
            )

        return cls(username, password, captcha_num, captcha_key)

    def login(self):
        headers = session_headers()
        headers.update(
            {
                "host": "tcidentity.asia.edu.tw",
                "content-type": "application/x-www-form-urlencoded",
                "referer": "https://tcidentity.asia.edu.tw",
                "user-agent": "TronClass/2.13.2(iPad; iOS 16.4.1; Scale/2.00)",
            }
        )

        AUTH_URL = (
            "https://tcidentity.asia.edu.tw/auth/realms/asia/protocol/openid-connect/auth"
            "?scope=openid"
            "&response_type=code"
            "&redirect_uri=https://cdn.jsdelivr.net/npm/40wisdomgarden/mobile-assets/latest/callback.html"
            "&client_id=TronClassApp"
        )

        TOKEN_URL = "https://tcidentity.asia.edu.tw/auth/realms/asia/protocol/openid-connect/token"

        TRON_LOGIN_URL = "https://tronclass.asia.edu.tw/api/login?login=access_token"

        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            session = requests.Session()
            session.headers.update(headers)

            # ---------------------------------------------------
            # Step 1: GET 授權頁，拿 HTML login form
            # ---------------------------------------------------
            resp = session.get(AUTH_URL)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")
            form = soup.find("form")

            if form is None:
                # 連 form 都找不到，直接丟 error 出去
                print("=== LOGIN DEBUG: no <form> found ===")
                print("url:", resp.url)
                print("body snippet:", resp.text[:1000])
                raise RuntimeError("在授權頁中找不到登入表單（<form>）")

            # 取得 form 的 action，如果是相對路徑，用 urljoin 補成絕對路徑
            raw_action = form.get("action")
            if isinstance(raw_action, list) and raw_action:
                action = raw_action[0]
            elif isinstance(raw_action, str):
                action = raw_action
            else:
                action = ""

            current_url = resp.url
            base_url = current_url if isinstance(current_url, str) else str(current_url)
            if not action:
                # 有些情況 action 可能是空，後端會用目前 URL 當目標
                login_url = base_url
            else:
                login_url = urljoin(base_url, action)

            # ---------------------------------------------------
            # Step 2: 組 POST payload：先把 hidden 欄位抓出來，再覆蓋 username/password/captcha
            # ---------------------------------------------------
            payload = {}

            for inp in form.find_all("input"):
                name = inp.get("name")
                if not name:
                    continue
                value = inp.get("value", "")
                payload[name] = value

            payload.update(
                {
                    "username": self.username,
                    "password": self.password,
                    "captchaCode": self.captcha_num,
                    "captchaKey": self.captcha_key,
                }
            )

            post_resp = session.post(login_url, data=payload, allow_redirects=True)

            # ---------------------------------------------------
            # Step 3-A: 從最後的 URL 抓 code
            # ---------------------------------------------------
            auth_code = None

            parsed = urlparse(post_resp.url)
            qs = parse_qs(parsed.query)
            if "code" in qs:
                auth_code = qs["code"][0]

            # ---------------------------------------------------
            # Step 3-B: 從 redirect history 找 code
            # ---------------------------------------------------
            if not auth_code:
                for h in post_resp.history:
                    loc = h.headers.get("Location", "")
                    if "code=" in loc:
                        parsed_loc = urlparse(loc)
                        qs_loc = parse_qs(parsed_loc.query)
                        if "code" in qs_loc:
                            auth_code = qs_loc["code"][0]
                            break

            # ---------------------------------------------------
            # Step 3-C: 還是沒有 code，輸出 debug 或重試
            # ---------------------------------------------------
            if not auth_code:
                logger.warning(
                    "Authorization code missing on attempt %d/%d; retrying",
                    attempt,
                    max_attempts,
                )
                if attempt < max_attempts:
                    continue
                print("history:")
                for i, h in enumerate(post_resp.history):
                    print(f"  [{i}] {h.status_code} -> {h.headers.get('Location')}")
                print("body snippet:", post_resp.text[:1000])
                raise RuntimeError("未取得 authorization code")

            # ---------------------------------------------------
            # Step 4: 用 code 換 access token
            # ---------------------------------------------------
            token_payload = {
                "grant_type": "authorization_code",
                "client_id": "TronClassApp",
                "code": auth_code,
                "redirect_uri": "https://cdn.jsdelivr.net/npm/40wisdomgarden/mobile-assets/latest/callback.html",
                # 如有需要可加 "scope": "openid"
            }

            token_headers = {
                "content-type": "application/x-www-form-urlencoded",
                "user-agent": headers["user-agent"],
            }

            token_resp = session.post(
                TOKEN_URL, data=token_payload, headers=token_headers
            )
            token_resp.raise_for_status()
            token_data = token_resp.json()
            access_token = token_data["access_token"]

            # ---------------------------------------------------
            # Step 5: 用 access token 登入 TronClass
            # ---------------------------------------------------

            session.headers.update(
                {
                    "Host": "tronclass.asia.edu.tw",
                    "Accept": "application/json, text/plain, */*",
                    "Sec-Fetch-Site": "cross-site",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Sec-Fetch-Mode": "cors",
                    "Content-Type": "application/json",
                    "Origin": "capacitor:localhost",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) TronClass/common",
                    "Sec-Fetch-Dest": "empty",
                    # 不要有 Content-Length
                }
            )

            tron_body = {
                "access_token": access_token,
                "org_id": 1,
            }

            tron_resp = session.post(
                TRON_LOGIN_URL,
                json=tron_body,
                headers=session.headers,
                timeout=10,
            )
            logger.info("🔐 Authentication successful")
            return session

        raise RuntimeError("未取得 authorization code after retries")
