import ctypes
from threading import Thread
from pathlib import Path
import keyboard
from PIL import Image, ImageEnhance, ImageOps

from core.device import *
from core.commands import Commands
from core.image import image_to_payload
from core.packet import build_packet



FRAME_DURATION = 0.5
KEY_WIDTH = 16
KEY_HEIGHT = 16

last_sent_time = [0]
last_key = [None]


MODIFIER_COLORS = {
    'ctrl': (0, 255, 255),
    'shift': (200, 100, 255),
    'alt': (255, 255, 100),
    'windows': (100, 255, 100),
}
MODIFIER_KEYS = {
    'ctrl', 'left ctrl', 'right ctrl',
    'shift', 'left shift', 'right shift',
    'alt', 'left alt', 'right alt',
    'windows', 'left windows', 'right windows',
    'caps lock'
}

key_aliases = {

    'right shift': 'shift',
    'right ctrl': 'ctrl',
    'right alt': 'alt',
    'home': 'hm',
    '/': 'slash',
    '\\': 'backslash',
    ':': 'colon',
    '"': 'quote',
    '*': 'asterisk',
    '<': 'less',
    '>': 'greater',
    '?': 'question',
    'page up': 'pu',
    'page down': 'pd',
    'insert': 'ins',
    'delete': 'del',
    'num lock': 'nl',
    'print screen': 'ps',
    'scroll lock': 'sl',
    'pause': 'pb',
}



def load_all_key_images(path = Path("assets/keys")):
    image_map = {}
    if isinstance(path, str):
        path = Path(path)
    for file in path.glob("*.png"):
        name = file.stem.lower()

        image = Image.open(file).convert("L")
        image_map[name] = image
    print(f"- Loaded {len(image_map)} keys")

    return image_map

def get_image_for_event(event_name: str):
    key = key_aliases.get(event_name.lower(), event_name.lower())
    return key_image_map.get(key)


def apply_mod_color(img, modifiers):
    active_mods = [mod for mod in MODIFIER_COLORS if modifiers.get(mod)]
    if not active_mods:
        return img.convert("RGB")

    img = img.convert("L")
    img_colored = Image.new("RGB", img.size)

    w, h = img.size
    part_h = h // len(active_mods)

    for i, mod in enumerate(active_mods):
        color = MODIFIER_COLORS[mod]
        top = i * part_h
        bottom = (i + 1) * part_h if i < len(active_mods) - 1 else h

        part = img.crop((0, top, w, bottom))
        colored_part = ImageOps.colorize(part, black="black", white=color)
        img_colored.paste(colored_part, (0, top))

    return img_colored



def send_image(img, device):
    packets = build_packet(Commands.Image, image_to_payload(img))
    device.send_packet(packets)



def is_capslock_on():
    return bool(ctypes.WinDLL("User32.dll").GetKeyState(0x14) & 1)

def get_modifiers():
    shift_active = (
        (keyboard.is_pressed('shift') or
        keyboard.is_pressed('right shift')) ^
        is_capslock_on()
    )
    return {
        'ctrl': keyboard.is_pressed('ctrl') or
                keyboard.is_pressed('right ctrl'),
        'shift': shift_active,
        'alt': keyboard.is_pressed('alt') or
               keyboard.is_pressed('right alt'),
        'windows': keyboard.is_pressed('windows') or
               keyboard.is_pressed('left windows')
    }

def fade_out_worker(device, last_key_ref, last_sent_time_ref):
    while True:
        time.sleep(0.05)
        if last_key_ref[0] is None:
            continue
        if time.time() - last_sent_time_ref[0] >= 0.5:
            key = last_key_ref[0]
            key_img = get_image_for_event(key)
            if key_img:
                modifiers = get_modifiers()
                colored = apply_mod_color(key_img, modifiers)

                for alpha in [0.7, 0.5,0.3, 0.1]:
                    dark = ImageEnhance.Brightness(colored).enhance(alpha)
                    send_image(dark, device)
                    time.sleep(0.07)

                black = Image.new("RGB", (KEY_WIDTH, KEY_HEIGHT), "black")
                send_image(black, device)

            last_key_ref[0] = None
            last_sent_time_ref[0] = 0


def start_key_display(device, path):
    global key_image_map
    key_image_map = load_all_key_images(path)

    print("[*] Pressed key display started")

    Thread(target=fade_out_worker, args=(device, last_key, last_sent_time), daemon=True).start()
    while True:
        event = keyboard.read_event()
        key = event.name.lower()
        if key in MODIFIER_KEYS:
            continue

        if event.event_type == keyboard.KEY_DOWN:
            if key != last_key[0]:
                key_img = get_image_for_event(key)
                if key_img:
                    modifiers = get_modifiers()
                    colored = apply_mod_color(key_img, modifiers)
                    send_image( colored,device)

                    last_sent_time[0] = time.time()
                    last_key[0] = key
            else:
                last_sent_time[0] = time.time()
                last_key[0] = key
