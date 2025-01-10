from typing import Tuple
from PIL import Image

from models import Resolution, Rotation, Resize, BackgroundColour, Mode
from epd_utils import palette_4gray


def resize_img(img: Image, mode: Mode, dither: bool, rotation: Rotation, resize: Resize, background: BackgroundColour,
               display_res: Resolution) -> Image:
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

    dither_setting = Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE

    if mode == Mode.FOUR_GRAY:
        # Palette is a flat array of each colour as RGB (3 elements), repeated 64 times in series to fill 256 slots
        epd_palette = sum([[colour] * 3*64 for colour in palette_4gray()], [])
        palette_image = Image.new("P", (16, 16), 0) # image size is arbitrary
        palette_image.putpalette(epd_palette)
        scaled_image = scaled_image.convert('RGB').quantize(palette=palette_image, dither=dither_setting)
    else:
        scaled_image = scaled_image.convert('1', dither=dither_setting)

    # Output image mode is grayscale for 4gray and mono for everything else
    image_mode = 'L' if mode == Mode.FOUR_GRAY else '1'

    # Add scaled image to full size canvas
    bg_colour = 255 if background == BackgroundColour.WHITE else 0
    x = int((display_res.width - scaled_image.width) / 2)
    y = int((display_res.height - scaled_image.height) / 2)
    canvas = Image.new(image_mode, display_res, bg_colour)
    canvas.paste(scaled_image, (x, y))
    return canvas


def get_resize_scale(img: Image, crop: bool, display_res: Resolution) -> Tuple[int, int]:
    width_scale = display_res.width / img.width
    height_scale = display_res.height / img.height
    scale = max(width_scale, height_scale) if crop else min(width_scale, height_scale)
    return int(img.width * scale), int(img.height * scale)


def image_changed(existing_image: Image, new_image: Image) -> bool:
    return list(new_image.getdata()) != list(existing_image.getdata())
