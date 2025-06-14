from PIL import Image
from image import remove_alpha


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
