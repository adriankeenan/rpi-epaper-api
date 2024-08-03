from typing import Tuple
from PIL import Image

from models import Resolution, Rotation, Resize, BackgroundColour

def resize_img(img: Image, rotation: Rotation, resize: Resize, background: BackgroundColour, display_res: Resolution) -> Image:
    # Rotate
    out_img = img.rotate(angle=rotation, expand=True)

    # Scale image
    if resize == Resize.FIT:
        scaled_resolution = get_resize_scale(out_img, False, display_res)
    elif resize == Resize.CROP:
        scaled_resolution = get_resize_scale(out_img, True, display_res)
    elif resize == Resize.NONE:
        scaled_resolution = (img.width, img.height)
    else:
        scaled_resolution = display_res

    scaled_image = out_img.resize(scaled_resolution)

    # Add scaled image to full size canvas
    bg_colour = 255 if background == BackgroundColour.WHITE else 0
    x = int((display_res.width - scaled_image.width) / 2)
    y = int((display_res.height - scaled_image.height) / 2)
    canvas = Image.new('1', display_res, bg_colour)
    canvas.paste(scaled_image, (x, y))
    return canvas

def get_resize_scale(img: Image, crop: bool, display_res: Resolution) -> Tuple[int, int]:
    width_scale = display_res.width / img.width
    height_scale = display_res.height / img.height
    scale = max(width_scale, height_scale) if crop else min(width_scale, height_scale)
    return int(img.width * scale), int(img.height * scale)
