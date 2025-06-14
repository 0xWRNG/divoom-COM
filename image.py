import math
from PIL import Image
import numpy as np
from pathlib import Path

def create_bit_array(numbers, bits_per_num):
    if bits_per_num == 8:
        return bytes(bytearray(numbers[::-1]))

    total_bits = len(numbers) * bits_per_num
    total_bytes = (total_bits + 7) // 8
    result = bytearray(total_bytes)

    for i, num in enumerate(numbers):
        start_idx = i * bits_per_num
        for bit_pos in range(bits_per_num):
            global_bit_idx = start_idx + bit_pos
            byte_idx = global_bit_idx // 8
            bit_in_byte = 7 - (global_bit_idx % 8)

            bit_val = (num >> (bits_per_num - 1 - bit_pos)) & 1
            result[byte_idx] |= bit_val << bit_in_byte

    return bytes(result[::-1])


def remove_alpha(img):
    if img.mode == 'P' and 'transparency' in img.info:
        img = img.convert('RGBA')
    if img.mode == 'LA':
        img = img.convert('RGBA')
    if img.mode == 'RGBA':
        bg = Image.new('RGBA', img.size, (0, 0, 0, 255))
        return Image.alpha_composite(bg, img).convert('RGB')

    return img.convert('RGB')


def image_to_payload(image_or_path, duration=0, reuse_palette=0):
    if isinstance(image_or_path, str) or isinstance(image_or_path, Path):
        img = remove_alpha(Image.open(image_or_path).resize((16, 16)))
    elif isinstance(image_or_path, Image.Image):
        img = image_or_path
    else:
        raise TypeError("Expected PIL.Image.Image or image_path")
    img = img.convert("P", palette=Image.ADAPTIVE, colors=255)

    palette = img.getpalette()

    color_data = bytes(palette)
    color_space = math.ceil(math.log2(len(color_data) / 3))

    data = np.array(img)
    data = np.flip(data, axis=(0, 1))
    encoded_img = create_bit_array(data.flatten(), color_space)

    frame = bytearray()
    frame.append(0xAA)

    if reuse_palette:
        frame_size = 1 + 2 + 2 + 1 + 1 + len(encoded_img)
    else:
        frame_size = 1 + 2 + 2 + 1 + 1 + len(color_data) + len(encoded_img)

    frame += frame_size.to_bytes(2, byteorder='little')
    frame += duration.to_bytes(2, byteorder='little')
    frame.append(reuse_palette)

    if reuse_palette:
        frame.append(0)
    else:
        frame.append(int(len(color_data) / 3))
        frame.extend(color_data)
    frame.extend(encoded_img)
    return frame
