import logging
from sys import path

from PIL import Image
from flask import Response, jsonify

from models import Mode

try:
    path.append('lib')
    # noinspection PyUnresolvedReferences
    from waveshare_epd import epd4in26
except Exception as e:
    logging.warning('could not import wavesare lib')


def get_epd():
    return epd4in26.EPD()


def display_clear(epd):
    epd.init()
    epd.Clear()
    epd.sleep()


def display_img(epd, image: Image, mode: Mode):
    if mode == Mode.PARTIAL:
        epd.init()
        for i in range(2):
            epd.display_Partial(epd.getbuffer(image))
    else:
        epd.init_Fast()
        epd.display_Fast(epd.getbuffer(image))
    epd.sleep()


def handle_epd_error(e: Exception) -> tuple[Response, int]:
    if isinstance(e, IOError):
        logging.error(f'IOError on display write: {str(e)}')
        return jsonify(message='Unexpected error'), 500
    elif isinstance(e, KeyboardInterrupt):
        logging.info('Display write interrupted due to KeyboardInterrupt')
        epd4in26.epdconfig.module_exit(cleanup=True)
        return jsonify(message='Cancelled'), 500
    else:
        logging.error(f'Unexpected error occurred - {str(e)}')
        return jsonify(message='Unexpected error occurred'), 500
