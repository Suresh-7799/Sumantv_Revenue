import cv2
import yt_dlp
import easyocr


from rapidfuzz import fuzz


TARGET_WORDS = [

    "annamayya",

    "australia",

    "amalapuram",

    "amaravati",

    "anantapur",

    "bhainsa",

    "bangalore",

    "bhadrachalam",

    "bhimavaram",

    "bheemili",

    "california",

    "chirala",

    "chittoor",

    "chikkaballapur",

    "dharmapuri",

    "dwaraka tirumala",

    "darsi",

    "newyork",

    "new jersey",

    "guntur",

    "jagtial",

    "kakinada",

    "karimnagar",

    "khammam",

    "kadapa",

    "kannada",

    "kandukur",

    "kalwakurthy",

    "kurnool",

    "kuppam",

    "kothagudem",

    "mahabubabad",

    "mangalagiri",

    "manakondur",

    "markapuram",

    "mulugu",

    "mandapeta",

    "nalgonda",

    "nizamabad",

    "narsipatnam",

    "nirmal",

    "ongole",

    "palakurthy",

    "palnadu",

    "prakasam",

    "peddapalli",

    "pithapuram",

    "rajahmundry",

    "rampachodavaram",

    "rajanagaram",

    "siricilla",

    "singapore",

    "srikakulam",

    "siddipet",

    "suryapet",

    "tirupati",

    "tuni",

    "texas",

    "undi",

    "visakhapatnam",

    "vizianagaram",

    "warangal",

    "yadadri",

    "annavaram",

    "madhira",

    "eluru",

    "florida",

    "mahabubnagar",

    "nagarkurnool",

    "uae",

    "nandyala",

    "nellore"
]


reader = easyocr.Reader(

    ["en"],

    gpu=False
)



def scan_youtube_video(video_url):

    ydl_opts = {

        "format":
        "best[ext=mp4]",

        "quiet":
        True,

        "noplaylist":
        True
    }

    with yt_dlp.YoutubeDL(
        ydl_opts
    ) as ydl:

        info = ydl.extract_info(

            video_url,

            download=False
        )

    stream_url = info.get(
        "url"
    )

    channel_name = info.get(
        "channel",
        ""
    )

    video_title = info.get(
        "title",
        ""
    )

    duration = info.get(
        "duration",
        0
    )

    cap = cv2.VideoCapture(
        stream_url
    )

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    if fps <= 0:

        fps = 30

    frame_interval = int(
        fps * 4
    )

    frame_count = 0

    while True:

        from app.dashboard.routes import (
            SCAN_RUNNING
        )

        if not SCAN_RUNNING:

            cap.release()

            return {

                "channel_name":
                channel_name,

                "video_title":
                video_title,

                "results":[]
            }

        success, frame = cap.read()

        if not success:
            break

        current_time = int(
            frame_count / fps
        )

        # SKIP FIRST 10 SECONDS

        if current_time < 5:

            frame_count += 1

            continue

        # SCAN MAX FIRST 4 MINUTES ONLY

        scan_limit = min(

            240,

            duration
        )

        if current_time > scan_limit:

            break

        if frame_count % frame_interval == 0:

            frame = cv2.resize(

                frame,

                (960,540)
            )

            height = frame.shape[0]

            width = frame.shape[1]
            

            bottom_area = frame[
                int(height * 0.45):height,
                0:width
            ]

            for area in [

                bottom_area
            ]:

                hsv = cv2.cvtColor(

                    area,

                    cv2.COLOR_BGR2HSV
                )

                lower_red = (
                    0,
                    15,
                    15
                )

                upper_red = (
                    180,
                    255,
                    255
                )

                mask = cv2.inRange(

                    hsv,

                    lower_red,

                    upper_red
                )

                contours, _ = cv2.findContours(

                    mask,

                    cv2.RETR_EXTERNAL,

                    cv2.CHAIN_APPROX_SIMPLE
                )

                contours = sorted(

                    contours,

                    key=cv2.contourArea,

                    reverse=True
                )[:20]

                for contour in contours:

                    x, y, w, h = cv2.boundingRect(
                        contour
                    )

                    # IGNORE SMALL NOISE

                    if w < 90:
                        continue                  

                    if h < 28:
                        continue

                    # HORIZONTAL STRIP ONLY

                    ratio = w / h

                    # ACCEPT EVEN SHORT STRIPS

                    if ratio < 1.8:
                        continue

                    strip_crop = area[
                        y:y+h,
                        x:x+w
                    ]
                    
                    gray = cv2.cvtColor(

                        strip_crop,

                        cv2.COLOR_BGR2GRAY
                    )

                    gray = cv2.resize(

                        gray,

                        None,

                        fx=2,

                        fy=2
                    )

                    _, gray = cv2.threshold(

                        gray,

                        140,

                        255,

                        cv2.THRESH_BINARY
                    )

                    from app.dashboard.routes import (
                        SCAN_RUNNING
                    )

                    if not SCAN_RUNNING:

                        cap.release()

                        return {

                            "channel_name":
                            channel_name,

                            "video_title":
                            video_title,

                            "results":[]
                        }

                    results = reader.readtext(

                        gray,

                        detail=0,

                        paragraph=False,

                        allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz "
                    )

                    from app.dashboard.routes import (
                        SCAN_RUNNING
                    )

                    if not SCAN_RUNNING:

                        cap.release()

                        return {

                            "channel_name":
                            channel_name,

                            "video_title":
                            video_title,

                            "results":[]
                        }

                    for item in results:

                        detected_text = (
                            item
                            .lower()
                            .strip()
                        )

                        detected_text = (
                            detected_text
                            .replace(
                                "0",
                                "o"
                            )
                            .replace(
                                "1",
                                "i"
                            )
                        )

                        if len(detected_text) < 3:
                            continue

                        # REMOVE SYMBOLS

                        detected_text = (
                            detected_text
                            .replace("|","")
                            .replace(":","")
                            .replace(".","")
                        )

                        best_match = None

                        best_score = 0

                        for word in TARGET_WORDS:

                            score = fuzz.ratio(

                                detected_text,

                                word
                            )

                            if score > best_score:

                                best_score = score

                                best_match = word

                        # STRONG FUZZY MATCH

                        if best_score >= 93:

                            cap.release()

                            return {

                                "channel_name":
                                channel_name,

                                "video_title":
                                video_title,

                                "results": [

                                    {

                                        "time":
                                        current_time,

                                        "text":
                                        best_match.title()
                                    }

                                ]
                            }

        frame_count += 1

    cap.release()

    return {

        "channel_name":
        channel_name,

        "video_title":
        video_title,

        "results": [

            {

                "time":
                0,

                "text":
                "No Strip Found"
            }

        ]
    }
