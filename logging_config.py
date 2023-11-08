import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_file = 'app.log'
    log_handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=5)
    log_format = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

    log_handler.setFormatter(log_format)
    log_handler.setLevel(logging.DEBUG)

    logger = logging.getLogger('my_app')
    logger.addHandler(log_handler)
    return logger

logger = setup_logging()
logger.setLevel(logging.DEBUG)
