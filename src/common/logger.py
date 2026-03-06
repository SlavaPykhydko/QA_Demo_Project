import logging
import os
import sys
from datetime import datetime


def get_logger(name):
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        #set up output in stdout
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        #set up output in file
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 4. Handler for logging into file
        current_date = datetime.now().strftime("%Y-%m-%d")
        log_file_name = f"{log_dir}/automation_{current_date}.log"
        file_handler = logging.FileHandler(log_file_name, encoding='utf-8')

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger