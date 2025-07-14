import logging
import os
import datetime


class Logger:
    _logger = None

    def __new__(cls, *args, **kwargs):
        if cls._logger is None:

            print("Logger new")
            cls._logger = super().__new__(cls, *args, **kwargs)
            cls._logger = logging.getLogger("mlscoringinference")
            cls._logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s %(name)s [%(levelname)s | %(filename)s : %(funcName)s : %(lineno)s] --> %(message)s')

            now = datetime.datetime.now()
            dirname = "./log"

            if not os.path.isdir(dirname):
                os.mkdir(dirname)
            fileHandler = logging.FileHandler(
                dirname + "/log_" + now.strftime("%Y-%m-%d")+".log")

            streamHandler = logging.StreamHandler()

            fileHandler.setFormatter(formatter)
            streamHandler.setFormatter(formatter)

            cls._logger.addHandler(fileHandler)
            cls._logger.addHandler(streamHandler)

        return cls._logger