# auth_module.py
import os
import requests
import urllib3
import requests
from fju.http_headers import session_headers
import re
from urllib.parse import urlparse, parse_qs
import logging
from getpass import getpass
from dotenv import load_dotenv

urllib3.disable_warnings()

if not logging.getLogger().hasHandlers():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

logger = logging.getLogger(__name__)


class Authenticator:
    def __init__(self):
        load_dotenv()
        self.username = os.getenv("USERNAMEID")
        self.password = os.getenv("PASSWORD")
        if not self.username or not self.password:
            logger.warning("USERNAMEID or PASSWORD not set. Prompting for credentials.")
            self.username, self.password = self._prompt_credentials()
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({"Referer": "https://elearn2.fju.edu.tw/"})
       
    def _prompt_credentials(self):
        username = input("Enter your username: ")
        password = getpass("Enter your password: ")
        return username, password
    
    def login(self):
        # Set up headers using the centralized headers
        headers = session_headers()
        headers.update({
            "host": "elearn2.fju.edu.tw",
            "content-type": "application/x-www-form-urlencoded",
            "referer": "https://elearn2.fju.edu.tw/cas/login",
            "user-agent": "TronClass/2.13.2(iPad; iOS 16.4.1; Scale/2.00)",
        })

        # Set username and password in form data
        form_data = {
            "username": self.username,
            "password": self.password
        }

        # Create a session to manage cookies
        session = requests.Session()

        # Get the login page to initialize session cookies
        session.get("https://elearn2.fju.edu.tw/d/server-time")


        # Send POST request with form data and headers
        url = "https://elearn2.fju.edu.tw/cas/v1/tickets"
        response = session.post(url, data=form_data, headers=headers)

        match = re.search(r'action="([^"]+)"', response.text)
        if not match:
            raise RuntimeError("TGT url not found in CAS response")

        tgt_url_raw = match.group(1)

        # ========= 關鍵：強制改成 HTTPS =========
        if tgt_url_raw.startswith("http://"):
            tgt_url = "https://" + tgt_url_raw[len("http://"):]
        else:
            tgt_url = tgt_url_raw

        # ========= 第二步：用 TGT 換 Service Ticket (ST) =========
        service_url = "https://elearn2.fju.edu.tw/api/cas-login"

        st_resp = session.post(
            tgt_url,
            data={"service": service_url},
            allow_redirects=False,  # 不要讓 POST 被轉成 GET
        )

        st = None

        # Case 1：CAS 乖乖照 REST 規範 → 200 + ST 在 body
        if st_resp.status_code == 200 and st_resp.text.strip():
            st = st_resp.text.strip()

        # Case 2：CAS 用 redirect 帶你去 service → ST 在 Location 的 ticket= 參數
        elif st_resp.status_code in (302, 303):
            loc = st_resp.headers.get("Location")
            if not loc:
                raise RuntimeError("302/303 but no Location header from CAS")
            parsed = urlparse(loc)
            qs = parse_qs(parsed.query)
            ticket_list = qs.get("ticket")
            if ticket_list:
                st = ticket_list[0]

        if not st:
            raise RuntimeError("Failed to extract Service Ticket (ST) from CAS response")


        # ========= 第三步：拿 ST 打目標 service（如果你要手動驗證） =========
        final_resp = session.get(
            service_url,
            params={"ticket": st},
            allow_redirects=False,  # 這裡要不要跟 redirect 看你需求
        )
        
        self.session = session
        return self.session
        