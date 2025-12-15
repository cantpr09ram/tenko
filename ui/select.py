import questionary
import asyncio
from dotenv import load_dotenv
import os
school = ["tku", "fju", "au"]



async def select_school() -> str:
    load_dotenv()
    result = os.getenv("SCHOOL")
    if not result:
        result = await questionary.select(
            "Select your school",
            choices=school
        ).ask_async()

    return result if result is not None else "tku"

if __name__ == "__main__":
    
    selected_school = asyncio.run(select_school())
    print(f"Selected school: {selected_school}")