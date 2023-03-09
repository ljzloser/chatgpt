import datetime
import os


class WriteLog:
    def __init__(self):
        self.logName = ''
        self.write('********************开始写入日志文件********************\n')

    def write(self, debug: str):
        if not os.path.exists('log'):
            os.mkdir('log')
        self.logName = f'log/{datetime.datetime.now().strftime("%Y-%m-%d")}.log'
        with open(file=self.logName, mode='a', encoding='UTF-8') as f:
            f.write(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  :  {debug}\n\n')
            f.close()
        pass

    def read(self, date: str):
        pass
