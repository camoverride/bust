from luma.core.interface.serial import spi
from luma.oled.device import ssd1331
from PIL import Image, ImageDraw
import time
import random
import mediapipe as mp
from picamera2 import Picamera2
import cv2
import numpy as np



# Initialize the camera.
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"format": "RGB888", "size": (640, 480)}
)
picam2.configure(config)
picam2.start()

# Initialize mediapipe face tracking.
mp_face = mp.solutions.face_detection
mp_draw = mp.solutions.drawing_utils
face_detector = mp_face.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.5)


def detect_and_draw_faces(
        frame: np.ndarray) -> tuple[np.ndarray, list]:
    """
    Detect faces, draw bounding boxes, and print center coordinates.
    Returns annotated frame and the center-point of the bounding box.
    This is used for face tracking (center point) and debugging.

    Parameters
    ----------
    frame: np.ndarray
        A frame returned from the camera.

    Returns
    -------
    tuple[np.ndarray, list]
        A tuple containing
            - np.ndarray: the annotated frame
            - list: the coordinates of the center of the face bb.
    """
    h, w, _ = frame.shape

    # MediaPipe expects RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_detector.process(rgb)

    if results.detections:
        for detection in results.detections:
            bbox = detection.location_data.relative_bounding_box

            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            bw = int(bbox.width * w)
            bh = int(bbox.height * h)

            # Draw rectangle around the face.
            cv2.rectangle(frame, (x, y), (x + bw, y + bh), (0, 255, 0), 2)

            # Center point of the face.
            cx = x + bw // 2
            cy = y + bh // 2
            face_center_coords = [cx, cy]

            # Draw center dot.
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)


    return frame, face_center_coords


# SPI setups
serial = spi(
    port=0,
    device=0,
    gpio_DC=25,
    gpio_RST=24)


device = ssd1331(
    serial,
    width=96,
    height=64)


# Create shared image buffer
width, height = 96, 64

# Eye parameters
eye_center = (48, 32)
eye_radius = 28
pupil_radius = 10

pupil_x = 0
pupil_y = 0
target_x = 0
target_y = 0

blink = 0
blink_timer = random.randint(50, 150)


def draw_eye(
        draw,
        px,
        py,
        blink_level):
    cx, cy = eye_center

    # Eyeball
    draw.ellipse(
        (cx - eye_radius, cy - eye_radius,
         cx + eye_radius, cy + eye_radius),
        fill="white"
    )

    # Constrain pupil
    px = max(-10, min(10, px))
    py = max(-10, min(10, py))

    # Pupil
    draw.ellipse(
        (cx - pupil_radius + px,
         cy - pupil_radius + py,
         cx + pupil_radius + px,
         cy + pupil_radius + py),
        fill="black"
    )

    # Eyelid (blink)
    if blink_level > 0:
        h = int(eye_radius * 2 * blink_level)
        draw.rectangle(
            (cx - eye_radius, cy - eye_radius,
             cx + eye_radius, cy - eye_radius + h),
            fill="black"
        )
        draw.rectangle(
            (cx - eye_radius, cy + eye_radius - h,
             cx + eye_radius, cy + eye_radius),
            fill="black"
        )


while True:
    # Capture frame.
    frame = picam2.capture_array()

    # Rotate 90 degrees clockwise.
    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # Show frame.
    frame, coords = detect_and_draw_faces(frame)
    cv2.imshow("Pi Camera Feed", frame)
    print(coords)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # New random target.
    if random.random() < 0.02:
        target_x = random.randint(-10, 10)
        target_y = random.randint(-10, 10)

    # Smooth movement.
    pupil_x += (target_x - pupil_x) * 0.2
    pupil_y += (target_y - pupil_y) * 0.2

    # Blink logic
    blink_timer -= 1
    if blink_timer <= 0:
        blink += 0.2
        if blink >= 1:
            blink = 1
        if blink >= 1 and random.random() < 0.3:
            blink_timer = random.randint(80, 200)
    else:
        blink -= 0.2
        if blink < 0:
            blink = 0

    # Create image.
    image = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(image)

    draw_eye(draw, pupil_x, pupil_y, blink)

    # Send same frame to display.
    device.display(image)

    time.sleep(0.03)



cv2.destroyAllWindows()
picam2.stop()
