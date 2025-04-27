import os
import logging

def setup_test_logger(log_path='logs/riley2_test.log'):
    os.makedirs('logs', exist_ok=True)
    logger = logging.getLogger('riley2_test')
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger
