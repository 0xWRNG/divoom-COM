from PIL import Image, ImageDraw, ImageFont
import os

size = (16, 16)
duration = 500  # 0.5 сек на кадр
output_file = "digits_gradient.gif"

frames = []
for digit in range(65):  # от 0 до 64
    img = Image.new('L', size)  # 'L' — оттенки серого
    for y in range(size[1]):
        shade = int(255 * y / (size[1] - 1))  # линейный градиент по вертикали
        for x in range(size[0]):
            img.putpixel((x, y), shade)

    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('fonts/smallest_pixel-7.ttf')

    # Форматируем текст
    text = str(digit)

    # Определяем позицию
    text_bbox = font.getbbox(text)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    if digit < 10:
        position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2 - 2)
    else:
        position = (1, (size[1] - text_height) // 2 - 2)

    # Рисуем белый текст (255 — максимум для 'L')
    draw.text(position, text, font=font, fill='black')

    frames.append(img.convert('P'))  # GIF требует 'P' (палитровый) режим

# Сохраняем GIF
frames[0].save(
    output_file,
    save_all=True,
    append_images=frames[1:],
    duration=duration,
    loop=0,
    optimize=False
)

print(f"Готово! GIF сохранён как {output_file}")
print(f"Количество кадров: {len(frames)}")
print(f"Общая длительность: {len(frames) * 0.5:.1f} секунд")
