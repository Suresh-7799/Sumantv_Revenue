import cv2
import os


def extract_frames(
    video_path,
    output_folder
):

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    cap = cv2.VideoCapture(
        video_path
    )

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    current_second = 0

    while current_second <= 30:

        frame_number = int(
            current_second * fps
        )

        cap.set(
            cv2.CAP_PROP_POS_FRAMES,
            frame_number
        )

        success, frame = cap.read()

        if not success:
            break

        cv2.imwrite(

            os.path.join(

                output_folder,

                f"{current_second}.jpg"
            ),

            frame
        )

        current_second += 1

    cap.release()
