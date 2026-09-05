import logging

logger = logging.getLogger(__name__)


def send_email(*, recipient: str, subject: str, body: str) -> None:
    # Provider integration belongs here; credentials must come from configuration.
    logger.info("Email queued", extra={"recipient": recipient, "subject": subject})
