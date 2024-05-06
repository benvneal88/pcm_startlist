import logging
import os


def get_logger():
    _logger = logging.getLogger(__name__)

    if not _logger.hasHandlers():
        _logger.setLevel(logging.INFO)

        _stream_handler = logging.StreamHandler()
        _stream_handler.setLevel(logging.INFO)

        _formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        _stream_handler.setFormatter(_formatter)

        _logger.addHandler(_stream_handler)

    return _logger
