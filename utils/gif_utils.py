import os

from core.image import remove_alpha
from PIL import Image
import math


def create_gif_from_strip(path_to_strip, output_gif_path, frame_size=(16, 16), duration=100, loop=0):
    strip = remove_alpha(Image.open(path_to_strip))

    width, height = strip.size
    frame_width, frame_height = frame_size

    frame_count = height // frame_height
    frames = []

    for i in range(frame_count):
        box = (0, i * frame_height, frame_width, (i + 1) * frame_height)
        frame = strip.crop(box)
        frames.append(frame)

    frames[0].save(
        output_gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=loop
    )

    print(f"Gif saved: {output_gif_path}")


def rotate_image_to_gif(input_path, output_path="rotated_y.gif", step=5, duration=100, final_size=(16, 16), canvas_size=(64, 64)):
    front = Image.open(input_path).convert("RGB").resize(canvas_size, Image.BICUBIC)
    back = front.transpose(Image.FLIP_LEFT_RIGHT)
    def simulate_y_rotation(img: Image.Image, angle_deg: float, canvas_size=(64, 64)) -> Image.Image:
        angle_rad = math.radians(angle_deg)
        scale = abs(math.cos(angle_rad))
        new_width = max(2, round(img.width * scale))

        resized = img.resize((new_width, img.height), Image.BICUBIC)
        bg = Image.new("RGB", canvas_size, (0, 0, 0))
        offset_x = (canvas_size[0] - new_width) // 2
        bg.paste(resized, (offset_x, 0))
        return bg

    frames = []

    for angle in range(0, 360, step):
        if angle < 90 or angle > 270:
            source = front
        else:
            source = back
        rotated = simulate_y_rotation(source, angle, canvas_size=canvas_size)
        small = rotated.resize(final_size, Image.BICUBIC)
        frames.append(small)

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0
    )
    print(f"Gif saved: {output_path}")
