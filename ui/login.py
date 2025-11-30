from textual.app import App, ComposeResult
from textual.widgets import Input, Static
from typing import Tuple
import tempfile
import os
import json
import base64
import requests
from PIL import Image
from rich_pixels import Pixels


async def login() -> Tuple[str, str]:
    """Basic login UI - returns username, password"""

    class _LoginApp(App[Tuple[str, str]]):
        def compose(self) -> ComposeResult:
            yield Static("Login")
            yield Input(placeholder="Username", id="username")
            yield Input(placeholder="Password", password=True, id="password")

        def on_input_submitted(self, event: Input.Submitted) -> None:
            if event.input.id == "username":
                self.query_one("#password", Input).focus()
            elif event.input.id == "password":
                username = self.query_one("#username", Input).value
                password = self.query_one("#password", Input).value
                self.exit((username, password))

    result = await _LoginApp().run_async()
    if result is None:
        raise KeyboardInterrupt("Login cancelled by user")
    return result


async def login_with_captcha_url(url: str) -> Tuple[str, str, str, str]:
    """
    Captcha login UI - fetches captcha from URL and returns username, password, num, key

    Args:
        url: Captcha URL that returns JSON with image and key

    Returns:
        Tuple of (username, password, captcha_code, captcha_key)
    """
    # Get captcha data from URL
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

    class _CaptchaLoginApp(App[Tuple[str, str, str, str]]):
        def compose(self) -> ComposeResult:
            yield Static("Login with Captcha")
            yield Input(placeholder="Username", id="username")
            yield Input(placeholder="Password", password=True, id="password")
            # Display image using rich-pixels
            try:
                # Load image with PIL
                image = Image.open(image_path)

                # Convert to RGB if needed
                if image.mode != "RGB":
                    image = image.convert("RGB")

                # Create Pixels widget for Textual
                pixels = Pixels.from_image(image, resize=(100, 40))
                yield Static(pixels)
            except Exception as e:
                yield Static(f"[Image display error: {str(e)}]")
            yield Input(placeholder="Enter captcha code", id="captcha")

        def on_input_submitted(self, event: Input.Submitted) -> None:
            if event.input.id == "username":
                self.query_one("#password", Input).focus()
            elif event.input.id == "password":
                self.query_one("#captcha", Input).focus()
            elif event.input.id == "captcha":
                username = self.query_one("#username", Input).value
                password = self.query_one("#password", Input).value
                captcha_code = self.query_one("#captcha", Input).value
                if username and password and captcha_code:
                    self.exit((username, password, captcha_code, key))

        def on_mount(self) -> None:
            # Clean up temp file after 60 seconds
            self.set_timer(
                60.0,
                lambda: os.unlink(image_path) if os.path.exists(image_path) else None,
            )

    while True:
        result = await _CaptchaLoginApp().run_async()
        if result is None:
            raise KeyboardInterrupt("Login cancelled by user")

        username, password, captcha_code, key = result

        # Check if captcha code was provided
        if not captcha_code:
            print("No captcha code entered. Retrying...")
            continue

        return result


def show_image(image_data: bytes) -> str:
    """Save image and display with chafa in terminal"""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(image_data)
        image_path = f.name

    return image_path
