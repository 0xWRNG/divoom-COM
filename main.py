from pathlib import Path
import argparse

from device import *
from brightness import make_brightness_payload
from packet import build_packet
from commands import Commands
from image import image_to_payload
from animation import gif_to_payload, read_divoom16
from gif_utils import create_gif_from_strip


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
    make_gif_from_strip.add_argument('gif_path', type=str, help='Path to result gif')
    make_gif_from_strip.add_argument('strip_path', type=str, help='Path to strip')
    args = parser.parse_args()

    # --- Command execution ---
    if args.category == 'send':
        device = DitooDevice.from_json('config.json')
        if args.send_type == 'image':
            packets = build_packet(Commands.Image, image_to_payload(Path(args.image_path)))
        elif args.send_type == 'gif':
            packets = build_packet(Commands.Animation, gif_to_payload(Path(args.gif_path)))
        elif args.send_type == 'divoom16':
            packets = build_packet(Commands.Animation, read_divoom16(Path(args.divoom16_path)))
        device.send_packet(packets)

    elif args.category == 'set':
        if args.set_type == 'brightness':
            device = DitooDevice.from_json('config.json')
            packets = build_packet(Commands.Brightness, make_brightness_payload(args.brightness))
            device.send_packet(packets)

    elif args.category == 'make':
        if args.make_type == 'divoom16':
            gif_to_payload(
                gif_path=Path(args.gif_path),
                save_path=Path(args.output_path)
            )
        if args.make_type == 'gif_from_strip':
            gif_path = Path(args.gif_path)
            strip_path = Path(args.strip_path)
            create_gif_from_strip(path_to_strip=strip_path, output_gif_path=gif_path)


if __name__ == "__main__":
    main()
