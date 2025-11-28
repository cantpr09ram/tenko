from textual.app import App, ComposeResult
from textual.widgets import Select

school = ["tku", "fju"]


async def select_school() -> str:
    class _SelectApp(App[str]):

        def compose(self) -> ComposeResult:
            yield Select(
                options=[(opt, opt) for opt in school],
                prompt="Select your school",
            )

        def on_select_changed(self, event: Select.Changed) -> None:
            self.exit(event.value)

    result = await _SelectApp().run_async()
    return result if result is not None else "tku"
