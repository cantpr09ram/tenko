import questionary
from typing import Tuple
import tempfile
import json
import base64
import requests
from PIL import Image
from rich_pixels import Pixels
from rich.console import Console


async def login() -> Tuple[str, str]:
    username = await questionary.text("Username:").ask_async()
    password = await questionary.password("Password:").ask_async()
    result = (username or "", password or "")
    return result


async def login_with_captcha_url(url: str) -> Tuple[str, str, str, str]:
    response = requests.get(url)
    response.raise_for_status()

    data = json.loads(response.text)
    image_data = data["image"]
    key = data["key"]

    # Remove data URL prefix and decode
    if image_data.startswith("data:image/png;base64,"):
        image_data = image_data.split(",", 1)[1]
    image_bytes = base64.b64decode(image_data)

    # Show image with chafa
    image_path = show_image(image_bytes)

    username = await questionary.text("Username:").ask_async()
    password = await questionary.password("Password:").ask_async()

    image = Image.open(image_path)
    if image.mode != "RGB":
        image = image.convert("RGB")

    pixels = Pixels.from_image(image, resize=(100, 40))

    Console().print(pixels)

    captcha = await questionary.text(f"Captcha (see image at {image_path}):").ask_async()
    result = (username or "", password or "", captcha or "", key)
    return result
    
    


def show_image(image_data: bytes) -> str:
    """Save image and display with chafa in terminal"""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(image_data)
        image_path = f.name

    return image_path
