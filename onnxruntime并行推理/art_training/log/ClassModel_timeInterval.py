import logging
from logging.handlers import TimedRotatingFileHandler

class Log(object):
    def __init__(self, name=__name__, path='mylog.log', level='DEBUG'):
        self.__name = name
        self.__path = path
        self.__level = level
        self.__logger = logging.getLogger(self.__name)
        self.__logger.setLevel(self.__level)

    def __ini_handler(self):
        """初始化handler"""
        stream_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(self.__path, encoding='utf-8')
        return stream_handler, file_handler

    def __set_handler(self, stream_handler, file_handler, level='DEBUG'):
        """设置handler级别并添加到logger收集器"""
        stream_handler.setLevel(level)
        file_handler.setLevel(level)
        self.__logger.addHandler(stream_handler)
        self.__logger.addHandler(file_handler)
        # 添加按照天分隔添加Handler
        # 日志切分的间隔时间单位;可选参数如下： “S”：Second 秒 “M”：Minutes 分钟 “H”：Hour 小时 “D”：Days 天 “W”：Week day（0 = Monday） “midnight”：Roll over at midnight
        # self.__logger.addHandler(TimedRotatingFileHandler(self.__path, when='D'))

    def __set_formatter(self, stream_handler, file_handler):
        """设置日志输出格式"""
        formatter = logging.Formatter('%(asctime)s'
                                      '-%(levelname)s-[schedule-pool]: %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        stream_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

    def __close_handler(self, stream_handler, file_handler):
        """关闭handler"""
        stream_handler.close()
        file_handler.close()

    @property
    def Logger(self):
        """构造收集器，返回looger"""
        stream_handler, file_handler = self.__ini_handler()
        self.__set_handler(stream_handler, file_handler)
        self.__set_formatter(stream_handler, file_handler)
        self.__close_handler(stream_handler, file_handler)
        return self.__logger


if __name__ == '__main__':
    # /home/wenhua/python/log/recor
    # 方式1
    # log = Log(__name__, 'file.log').Logger.error("hello word")
    # 方式2
    log=Log(__name__,'file.log').Logger
    log.error("hello word")
    log.info("nihao1")
    # logger = log.Logger
    # logger.debug('I am a debug message')
    # logger.info('I am a info message')
    # logger.warning('I am a warning message')
    # logger.error('I am a error message')
    # logger.critical('I am a critical message')