import logging
from contextlib import contextmanager
from sys import path

from PIL import Image
from flask import Response, jsonify
from filelock import Timeout as FileLockTimeout, FileLock


path.append('lib')
# noinspection PyUnresolvedReferences
from waveshare_epd import epd4in26

@contextmanager
def get_epd_lock():
    lock = FileLock('epd.lock', timeout=10)
    with lock.acquire():
        yield epd4in26.EPD()

def display_clear():
    with get_epd_lock() as epd:
        epd.init()
        epd.Clear()
        epd.sleep()

def display_img(image: Image):
    with get_epd_lock() as epd:
        epd.init()
        epd.Clear()
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
    elif isinstance(e, FileLockTimeout):
        logging.info('Could not obtain device lock')
        return jsonify(message='Device busy, please wait for current request to complete'), 409
    else:
        logging.error(f'Unexpected error occurred - {str(e)}')
        return jsonify(message='Unexpected error occurred'), 500