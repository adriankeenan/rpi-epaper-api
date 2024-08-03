from pathlib import Path

from flask import Flask, request, jsonify, send_file, Response
from PIL import Image, UnidentifiedImageError

import logging

from models import Resolution, Rotation, Resize, BackgroundColour

from img_utils import resize_img
from epd_utils import get_epd_lock, handle_epd_error, display_clear, display_img

IMG_PATH = 'img.png'
DISPLAY_RESOLUTION = Resolution(800, 480)

def get_last_set_image() -> Response | tuple[Response, int]:

    if not Path(IMG_PATH).exists():
        logging.error(f'Existing image file doesn\'t exist')
        return jsonify(message='Framebuffer image not found'), 404

    try:
        return send_file(IMG_PATH)
    except Exception as e:
        logging.error(f'Unable to load last set image - {str(e)}')
        return jsonify(message='Unknown error fetching file'), 500

def image_changed(new_image: Image) -> bool:
    try:
        existing_image = Image.open(IMG_PATH)
    except FileNotFoundError:
        return True
    except Exception as e:
        logging.error(e)
        return True

    return list(new_image.getdata()) != list(existing_image.getdata())

def show_image() -> tuple[Response, int]:

    try:
        img_file = request.files['image'].stream
        image = Image.open(img_file)
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

    image_to_display = resize_img(image, rotate, resize, background, DISPLAY_RESOLUTION)

    update_image = image_changed(image_to_display)
    if update_image:
        try:
            display_img(image_to_display)
            image_to_display.save(IMG_PATH)
        except Exception as e:
            return handle_epd_error(e)

    return jsonify(message='Success', updated=update_image), 200

def clear_image():
    try:
        display_clear()
        Image.new('1', DISPLAY_RESOLUTION, 255).save(IMG_PATH)
        return jsonify(message='Success'), 200
    except Exception as e:
        return handle_epd_error(e)


logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST', 'DELETE'])
def img():
    if request.method == 'GET':
        return get_last_set_image()

    if request.method == 'POST':
        return show_image()

    if request.method == 'DELETE':
        return clear_image()
