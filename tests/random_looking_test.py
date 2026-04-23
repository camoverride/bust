from luma.core.interface.serial import spi
from luma.oled.device import ssd1331
from PIL import Image, ImageDraw
import time
import random



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
    # New random target
    if random.random() < 0.02:
        target_x = random.randint(-10, 10)
        target_y = random.randint(-10, 10)

    # Smooth movement
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

    # Create image
    image = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(image)

    draw_eye(draw, pupil_x, pupil_y, blink)

    # Send same frame to display
    device.display(image)

    time.sleep(0.03)
