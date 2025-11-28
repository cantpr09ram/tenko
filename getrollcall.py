import time
import logging
import requests

if not logging.getLogger().hasHandlers():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

logger = logging.getLogger(__name__)


def wait_for_rollcall(session: requests.Session, sec: int = 10, endpoint: str = "https://elearn2.fju.edu.tw") -> tuple[int, str]:
    """
    Polls the iClass rollcall API until the specified rollcall_id is found.

    Args:
        session (requests.Session): The session with proper headers set.
        target_rollcall_id (int): The rollcall_id to wait for.

    Returns:
        tuple: (rollcall_id, source) when found.
    """
    url = f"{endpoint}/api/radar/rollcalls?api_version=1.1.0"
    while True:
        try:
            response = session.get(url)
            response.raise_for_status()
            data = response.json()
            previous_rollcall_id = None
            rollcalls = data.get("rollcalls", [])
            for rollcall in rollcalls:
                if rollcall.get("rollcall_id") and rollcall["rollcall_id"] != previous_rollcall_id:
                    logger.info("Found rollcall: ID = %s, Source = %s", rollcall["rollcall_id"], rollcall["source"],)
                    previous_rollcall_id = rollcall["rollcall_id"]
                    return rollcall["rollcall_id"], rollcall["source"]

            logger.info("Rollcall not found yet. Waiting %s seconds...", sec)
            time.sleep(sec)

        except Exception as e:
            logger.error("Error occurred while waiting for rollcall: %s", e)
            time.sleep(5)
