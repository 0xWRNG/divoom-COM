from PIL import Image, ImageSequence
import image
import os
from pathlib import Path


def palette_to_set(byte_arr):
    return {
        tuple(byte_arr[i:i + 3])
        for i in range(1, len(byte_arr), 3)
        if i + 2 < len(byte_arr)
    }


def gif_to_payload(gif_path, save_path=''):
    gif = Image.open(gif_path)
    all_gif = bytearray()
    if getattr(gif, "is_animated", False):
        prev_palette = set(tuple())
        for i, frame in enumerate(ImageSequence.Iterator(gif)):
            duration = frame.info.get("duration", 200)
            frame = frame.convert("RGB").resize((16, 16))
            frame = frame.convert("P", palette=Image.ADAPTIVE, colors=255)
            new_palette = palette_to_set(frame.getpalette())
            if new_palette != prev_palette:
                all_gif.extend(image.image_to_payload(image_or_path=frame, duration=duration))
            else:
                all_gif.extend(image.image_to_payload(image_or_path=frame, duration=duration, reuse_palette=1))
            prev_palette = new_palette

    else:
        all_gif.extend(image.image_to_payload(image_or_path=gif))

    if save_path != '':
        with open(save_path, "wb") as f:
            f.write(all_gif)

    return all_gif


def read_divoom16(file_path):
    if Path(file_path).suffix != '.divoom16':
        raise TypeError("Expected divoom16 format")
    read_file = bytearray()
    with open(file_path, 'rb') as f:
        while byte := f.read(1):
            read_file.extend(byte)
    return read_file


