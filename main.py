# main.py
import logging
import asyncio
from schools.config import SCHOOL_CONFIGS, SchoolConfig
from schools.rollcall import handle_rollcall
from ui.select import select_school

logger = logging.getLogger(__name__)


async def main() -> None:
    
    school_key = await select_school()
    logger.info("Selected school: %s", school_key)

    config: SchoolConfig | None = SCHOOL_CONFIGS.get(school_key)
    if config is None:
        logger.error("Unsupported school: %s", school_key)
        return

    # 1. 登入（每間學校 auth 寫法不一樣，但都藏在 auth_func 裡）
    session = await config.auth_func()
    logger.info("Authenticated session for school: %s", school_key)
    # 2. 有 endpoint 的學校才進行 rollcall
    if config.endpoint:
        await handle_rollcall(
            auth_session=session,
            endpoint=config.endpoint,
            latitude=config.latitude,
            longitude=config.longitude,
        )
    else:
        logger.info("School %s has no rollcall endpoint configured.", school_key)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
