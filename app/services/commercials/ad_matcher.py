import imagehash
import json

from PIL import Image


def match_ad(
    frame_path,
    client
):

    try:

        frame_hash = imagehash.phash(

            Image.open(
                frame_path
            )
        )

        sample_images = json.loads(

            client.sample_images
            or "[]"
        )

        for image_path in sample_images:

            image_hash = imagehash.phash(

                Image.open(
                    "." + image_path
                )
            )

            similarity = (

                100
                -
                abs(
                    frame_hash
                    -
                    image_hash
                )
            )

            if similarity >= 85:

                return True

    except Exception:

        pass

    return False
