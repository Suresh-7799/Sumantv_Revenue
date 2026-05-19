import json

from app.extensions import (
    redis_client
)


class CacheService:

    DEFAULT_TTL = 300

    @staticmethod
    def set(

        key,

        value,

        ttl=DEFAULT_TTL

    ):

        try:

            redis_client.setex(

                key,

                ttl,

                json.dumps(value)

            )

            return True

        except Exception:

            return False

    @staticmethod
    def get(key):

        try:

            value = redis_client.get(key)

            if not value:

                return None

            return json.loads(value)

        except Exception:

            return None

    @staticmethod
    def delete(key):

        try:

            redis_client.delete(key)

            return True

        except Exception:

            return False

    @staticmethod
    def invalidate_workspace_cache(
        workspace_id
    ):

        CacheService.delete(
            f"workspace:{workspace_id}"
        )

    @staticmethod
    def get_workspace_cache(
        workspace_id
    ):

        return CacheService.get(
            f"workspace:{workspace_id}"
        )

    @staticmethod
    def set_workspace_cache(
        workspace_id,
        data
    ):

        return CacheService.set(

            f"workspace:{workspace_id}",

            data

        )