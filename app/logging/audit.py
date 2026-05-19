import logging


logging.basicConfig(

    level=logging.INFO,

    format=(
        "%(asctime)s "
        "%(levelname)s "
        "%(message)s"
    )

)


audit_logger = logging.getLogger(
    "audit"
)


def log_action(

    user,

    action,

    metadata=None

):

    audit_logger.info(

        {

            "user": user,

            "action": action,

            "metadata": metadata

        }

    )