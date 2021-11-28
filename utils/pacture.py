from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random
import os


def get_random():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def get_png():
    current = os.path.dirname(__file__)
    img_obj = Image.new('RGB', (150, 35), get_random())
    img_draw = ImageDraw.Draw(img_obj)
    img_font = ImageFont.truetype(f'{current}/font.ttf', 30)
    code = ''
    for i in range(6):
        random_upper = chr(random.randint(65, 90))
        random_lower = chr(random.randint(97, 122))
        random_int = str(random.randint(0, 9))
        tmp = random.choice([random_int, random_lower, random_upper])
        img_draw.text((i * 20 + 12, 0), tmp, get_random(), img_font)
        code += tmp
    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')
    return code, io_obj.getvalue()
