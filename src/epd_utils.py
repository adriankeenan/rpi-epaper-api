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
    if mode == Mode.FOUR_GRAY:
        epd.init_4GRAY()
        epd.display_4Gray(epd.getbuffer_4Gray(image))
    elif mode == Mode.PARTIAL:
        epd.init()
        # display_Partial will leave ghosting from the previous images. Calling a second time clears this almost
        # entirely.
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

def palette_4gray() -> list[int]:
    # @see https://github.com/waveshareteam/e-Paper/blob/ecdd8cf7bab311e6e290c84c68d474deafb7ca8d/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd4in26.py#L38
    # Copied, rather than imported, to allow access without importing epd lib (eg when mocking)
    return [0xff, 0xC0, 0x80, 0x00]