import os
import math
import time
import pyautogui
from PIL import Image
from screeninfo import get_monitors

from core.image import image_to_payload, remove_alpha
from core.packet import build_packet
from core.commands import Commands
from utils.console_utils import Colors, print_progress


def start_compass_display(device, compass_dir):
    if not os.path.isdir(compass_dir):
        print(f'{Colors.FAIL.value}[X] Directory does not exist{Colors.ENDC.value}')
        return

    compass_frames = []
    for filename in os.listdir(compass_dir):
        image_path = os.path.join(compass_dir, filename)
        img = Image.open(image_path)
        img = remove_alpha(img)
        compass_frames.append(img)

    if not compass_frames:
        print(f'{Colors.FAIL.value}[X] No valid images found in directory{Colors.ENDC.value}')
        return

    monitors = get_monitors()
    min_x = min(m.x for m in monitors)
    min_y = min(m.y for m in monitors)
    max_x = max(m.x + m.width for m in monitors)
    max_y = max(m.y + m.height for m in monitors)

    center_x = (min_x + max_x) // 2
    center_y = (min_y + max_y) // 2
    prev_sector = -1

    print("[*] Compass mode started. Move your mouse around the center of the screen.")

    while True:
        mouse_x, mouse_y = pyautogui.position()
        dx = mouse_x - center_x
        dy = mouse_y - center_y

        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        angle_deg = (angle_deg - 90 + 360) % 360

        sector_count = len(compass_frames)
        sector = int(angle_deg / (360 / sector_count)) % sector_count

        if sector != prev_sector:
            img = compass_frames[sector]
            payload = image_to_payload(image_or_path=img)
            packets = build_packet(Commands.Image, payload=payload)
            print_progress(sector, sector_count)
            device.send_packet(packets)
            prev_sector = sector

        time.sleep(0.05)
