from app.realtime.socket import (
    broadcast_notification
)


class NotificationService:

    @staticmethod
    def send_notification(

        title,

        message,

        level="info"

    ):

        payload = {

            "title": title,

            "message": message,

            "level": level

        }

        broadcast_notification(
            payload
        )

        return payload