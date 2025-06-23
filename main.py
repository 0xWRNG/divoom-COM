import os.path
from pathlib import Path
import argparse
from PIL import Image

from core.device import *
from core.packet import build_packet
from core.commands import Commands
from core.image import image_to_payload
from features.animation import gif_to_payload, read_divoom16
from utils.console_utils import Colors


def main():
    parser = argparse.ArgumentParser(
        description='Utility for simple controlling Divoom Ditoo device over COM port'
    )

    top_level = parser.add_subparsers(dest='category', required=True)

    # --- send ---
    send = top_level.add_parser('send', help='Send data to device')
    send_sub = send.add_subparsers(dest='send_type', required=True)

    send_image = send_sub.add_parser('image', help='Send image to device')
    send_image.add_argument('image_path', type=str, help='Path to image')

    send_gif = send_sub.add_parser('gif', help='Send gif to device')
    send_gif.add_argument('gif_path', type=str, help='Path to gif')

    send_divoom16 = send_sub.add_parser('divoom16', help='Send preprocessed .divoom16 file to device')
    send_divoom16.add_argument('divoom16_path', type=str, help='Path to .divoom16 file')

    send_image_slideshow = send_sub.add_parser('slideshow', help='Send set of images to device')
    send_image_slideshow.add_argument('images_directory', type=str, help='Images directory')
    send_image_slideshow.add_argument('timeout', type=float, help='Timeout in ms')
    send_image_slideshow.add_argument('--loop', required=False, type=bool, help='Loop slideshow')

    # --- set ---
    set_cmd = top_level.add_parser('set', help='Set parameters on device')
    set_sub = set_cmd.add_subparsers(dest='set_type', required=True)

    set_brightness = set_sub.add_parser('brightness', help='Set screen brightness')
    set_brightness.add_argument('brightness', type=int, help='Brightness in percents')

    # --- make ---
    make = top_level.add_parser('make', help='Make preprocessed files')
    make_sub = make.add_subparsers(dest='make_type', required=True)

    make_divoom16 = make_sub.add_parser('divoom16', help='Convert gif to .divoom16 format')
    make_divoom16.add_argument('gif_path', type=str, help='Path to gif')
    make_divoom16.add_argument('output_path', type=str, help='Output .divoom16 file path')

    make_gif_from_strip = make_sub.add_parser('gif_from_strip', help='Makes gif 16 by 16 from strip of 16 by 16*X')
    make_gif_from_strip.add_argument('strip_path', type=str, help='Path to strip')
    make_gif_from_strip.add_argument('gif_path', type=str, help='Path to result gif')

    make_rotating_gif = make_sub.add_parser('rotating_gif', help='Makes image rotation')
    make_rotating_gif.add_argument('image_path', type=str, help='Path to strip')
    make_rotating_gif.add_argument('gif_path', type=str, help='Path to result gif')

    # --- live ---
    live = top_level.add_parser('live', help='Live modes')
    live_sub = live.add_subparsers(dest='live_type', required=True)

    compass = live_sub.add_parser('compass', help='Compass representing mouse position')
    compass.add_argument('compass_path', type=str, help='Path to compass frames')

    keystrokes = live_sub.add_parser('keystrokes', help='Displaying keystokes mode')

    args = parser.parse_args()

    # --- Command execution ---
    packets = []
    if args.category == 'send':
        device = DitooDevice.from_json('config.json')
        if args.send_type == 'image':
            if not os.path.isfile(args.image_path):
                print(f'{Colors.FAIL.value}[X] File does not exist{Colors.ENDC.value}')
                return
            packets = build_packet(Commands.Image, image_to_payload(Path(args.image_path)))
        elif args.send_type == 'gif':
            if not os.path.isfile(args.gif_path):
                print(f'{Colors.FAIL.value}[X] File does not exist{Colors.ENDC.value}')
                return
            packets = build_packet(Commands.Animation, gif_to_payload(Path(args.gif_path)))
        elif args.send_type == 'divoom16':
            if not os.path.isfile(args.divoom16_path):
                print(f'{Colors.FAIL.value}[X] File does not exist{Colors.ENDC.value}')
                return
            packets = build_packet(Commands.Animation, read_divoom16(Path(args.divoom16_path)))
        elif args.send_type == 'slideshow':
            if not os.path.isdir(args.images_directory):
                print(f'{Colors.FAIL.value}[X] Directory does not exist{Colors.ENDC.value}')
                return
            if args.timeout < 0:
                print(f'{Colors.WARNING}[!] Incorrect brightness value{Colors.ENDC.value}')
                return
            folder = args.images_directory
            files = os.listdir(args.images_directory)
            while True:
                count = 0
                for name in files:
                    count += 1
                    print_progress(count, len(files))
                    full_path = os.path.join(folder, name)
                    if os.path.isfile(full_path) and Image.open(full_path).size == (16, 16):
                        device.send_packet(
                            build_packet(Commands.Image, payload=image_to_payload(image_or_path=full_path)))
                        time.sleep(args.timeout)
                if args.loop is None or not args.loop:
                    break
        if len(packets) != 0:
            device.send_packet(packets)

    elif args.category == 'set':
        from features.brightness import make_brightness_payload
        if args.set_type == 'brightness':
            if 0 > args.brightness > 100:
                print('[X] Incorrect brightness value')
                return
            device = DitooDevice.from_json('config.json')
            packets = build_packet(Commands.Brightness, make_brightness_payload(args.brightness))
            device.send_packet(packets)

    elif args.category == 'make':
        if args.make_type == 'divoom16':
            if not os.path.isfile(args.gif_path):
                print(f'{Colors.FAIL.value}[X] File does not exist{Colors.ENDC.value}')
                return
            gif_to_payload(
                gif_path=Path(args.gif_path),
                save_path=Path(args.output_path)
            )
        if args.make_type == 'gif_from_strip':
            from utils.gif_utils import create_gif_from_strip
            if not os.path.isfile(args.strip_path):
                print(f'{Colors.FAIL.value}[X] File does not exist{Colors.ENDC.value}')
                return
            gif_path = Path(args.gif_path)
            strip_path = Path(args.strip_path)
            create_gif_from_strip(path_to_strip=strip_path, output_gif_path=gif_path)
        if args.make_type == 'rotating_gif':
            from utils.gif_utils import rotate_image_to_gif
            if not os.path.isfile(args.image_path):
                print(f'{Colors.FAIL.value}[X] File does not exist{Colors.ENDC.value}')
                return
            gif_path = Path(args.gif_path)
            image_path = Path(args.image_path)
            rotate_image_to_gif(input_path=image_path, output_path=gif_path)
    elif args.category == 'live':
        device = DitooDevice.from_json('config.json')

        if args.live_type == 'compass':
            from features.compass import start_compass_display
            start_compass_display(device, args.compass_path)

        elif args.live_type == 'keystrokes':
            from features.keystrokes import start_key_display
            start_key_display(device)




if __name__ == "__main__":
    main()
