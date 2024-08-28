import logging
import os
import threading

lock = threading.Lock()
current_dir_path = os.path.abspath(os.path.dirname(__file__))


class LoggerUtil():
    def __init__(self):
        self.stream_handler = None
        self.file_handler = None
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)  # log等级总开关

    def get_new_logger(self):
        self.logger.handlers.clear()
        formatter = logging.Formatter(f"%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")

        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(logging.INFO)  # log等级的开关
        self.stream_handler.setFormatter(formatter)
        self.logger.addHandler(self.stream_handler)
        # 添加到logger
        return self.logger

    def get_logger(self):
        return self.logger

    def clear_handlers(self):
        self.logger.handlers.clear()


