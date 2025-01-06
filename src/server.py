import json
import os
from pathlib import Path
from unittest.mock import Mock

from flask import Flask, request, jsonify, send_file, Response

from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener

import logging

from models import Resolution, Rotation, Resize, BackgroundColour, Mode

from img_utils import resize_img, image_changed
from epd_utils import handle_epd_error, display_clear, display_img, get_epd

IMG_PATH = 'img.png'
DISPLAY_RESOLUTION = Resolution(800, 480)

logging.basicConfig(level=logging.DEBUG)

register_heif_opener()


def str_is_true(value) -> bool:
    return value in [True, 'true', '1']


def mock_epd() -> bool:
    return str_is_true(os.getenv('EPD_MOCK'))


epd = get_epd() if mock_epd() is False else Mock()

app = Flask(__name__)


@app.route("/", methods=['GET'])
def get_last_set_image() -> Response | tuple[Response, int]:
    if not Path(IMG_PATH).exists():
        logging.error(f'Existing image file doesn\'t exist')
        return jsonify(message='Framebuffer image not found'), 404

    try:
        return send_file(IMG_PATH)
    except Exception as e:
        logging.error(f'Unable to load last set image - {str(e)}')
        return jsonify(message='Unknown error fetching file'), 500


@app.route("/", methods=['POST'])
def show_image() -> tuple[Response, int]:
    try:
        img_file = request.files['image']
        image = Image.open(img_file.stream)
    except UnidentifiedImageError:
        return jsonify(message='"image" does not appear to be valid'), 422
    except Exception as e:
        logging.error(f'Unable to read image - {str(e)}')
        return jsonify(message=f'Unable to read image'), 422

    try:
        rotate = Rotation(int(request.form.get('rotate', Rotation.ROTATE_0.value)))
    except ValueError:
        return jsonify(message=f'"rotation" invalid, must be one of {", ".join([str(x.value) for x in Rotation])}'), 422

    try:
        resize = Resize(request.form.get('resize', Resize.FIT.value))
    except ValueError:
        return jsonify(message=f'"resize" invalid, must be one of {", ".join([x for x in Resize])}'), 422

    try:
        background = BackgroundColour(request.form.get('background', BackgroundColour.WHITE.value))
    except ValueError:
        return jsonify(message=f'"background" invalid, must be one of {", ".join([x for x in BackgroundColour])}'), 422

    try:
        mode = Mode(request.form.get('mode', Mode.FAST.value))
    except ValueError:
        return jsonify(message=f'"mode" invalid, must be one of {", ".join([x for x in Mode])}'), 422

    dither = str_is_true(request.form.get('dither', True))

    loc = locals()
    image_settings = {i: loc[i] for i in ('mode', 'dither', 'rotate', 'resize', 'background')}
    image_settings['image'] = img_file.filename
    image_settings['image_resolution'] = [image.width, image.height]
    logging.debug(f'Creating an image with the following settings: {json.dumps(image_settings)}')

    image_to_display = resize_img(image, dither, rotate, resize, background, DISPLAY_RESOLUTION)

    try:
        update_image = image_changed(Image.open(IMG_PATH), image_to_display)
    except Exception as e:
        logging.warning(f'Unable to determine image difference - {str(e)}')
        update_image = True

    if update_image:
        try:
            display_img(epd, image_to_display, mode)
            image_to_display.save(IMG_PATH)
        except Exception as e:
            return handle_epd_error(e)

    return jsonify(message='Success', updated=update_image), 200


@app.route("/", methods=['DELETE'])
def clear_image():
    try:
        display_clear(epd)
        Image.new('1', DISPLAY_RESOLUTION, 255).save(IMG_PATH)
        return jsonify(message='Success'), 200
    except Exception as e:
        return handle_epd_error(e)

if __name__ == "__main__":
    app.run(port=5000)