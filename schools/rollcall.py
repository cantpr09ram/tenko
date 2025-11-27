# schools/rollcall.py
import logging
from getrollcall import wait_for_rollcall
from sendRadar import answer_rollcall_Radar
from sendNum import answer_rollcall_number_async

logger = logging.getLogger(__name__)


async def handle_rollcall(auth_session, endpoint: str, latitude: float, longitude: float) -> None:
    rollcall_id, source = wait_for_rollcall(session=auth_session, endpoint=endpoint)
    logger.info("Returned: rollcall_id=%s, source=%s", rollcall_id, source)

    if source == "number":
        data = await answer_rollcall_number_async(
            session = auth_session,
            rollcall_id = rollcall_id,
            endpoint=endpoint,
        )
        logger.info("Number rollcall response: %s", data)

    elif source == "radar":
        radar_response = await answer_rollcall_Radar(
            session = auth_session,
            rollcall_id = rollcall_id,
            endpoint=endpoint,
            latitude=latitude,
            longitude=longitude,
        )
        logger.info("Radar rollcall response: %s", radar_response.text)

    else:
        logger.warning("Unknown rollcall source: %s", source)
