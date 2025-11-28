import json
import logging 
import cv2 
import numpy as np 
import pytesseract 
import requests
import base64 
import os 
from bs4 import BeautifulSoup 

if not logging.getLogger().hasHandlers():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

logger = logging.getLogger(__name__)

async def Ulearn_login(username: str, password: str):
    session = aiohttp.ClientSession(headers=Agent)

    try:
        # 1️⃣ 取得登入頁並解析 action URL
        async with session.get(URL) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            form = soup.find("form", class_="form-signin form-login")
            if not form:
                await session.close()
                return None, "無法取得登入表單"
            action_url = form["action"]

        # 2️⃣ 取得驗證碼並 OCR
        img, key = await codeImg(session)
        processed_img = await preprocess_image(img)
        text = pytesseract.image_to_string(processed_img, config=custom_config)
        code = text.replace(" ", "").strip()

        # 3️⃣ POST 登入
        payload = {
            "username": username,
            "password": password,
            "captchaCode": code,
            "captchaKey": key
        }

        async with session.post(action_url, data=payload) as login_resp:
            if login_resp.status != 200:
                await session.close()
                return None, "登入請求失敗"

            body = await login_resp.text()
            soup = BeautifulSoup(body, "html.parser")

            # 4️⃣ 以「登出」連結判斷登入是否成功
            if soup.find("a", string="登出"):
                return session, None
            else:
                err = soup.find("span", {"style": "color:red"})
                await session.close()
                if err:
                    return None, err.get_text(strip=True)
                return None, "登入失敗（不明原因）"

    except Exception as e:
        await session.close()
        return None, f"例外錯誤: {str(e)}"
