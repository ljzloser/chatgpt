import datetime
import json
import os


class Log:
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


class ChatLog:
    def __init__(self, filename):
        self.chatName = f'Chat/{filename}.txt'

    def write(self, role, content):
        datadict = {"role": role, "content": content}
        data = json.dumps(datadict) + '\n'
        with open(file=self.chatName, mode='a', encoding='UTF-8') as f:
            f.write(data)
            f.close()

    def read(self) -> list:
        with open(file=self.chatName, mode='r', encoding='UTF-8') as f:
            chatList = []
            for d in f.read().split('\n'):
                if d != '':
                    s = json.loads(d)
                    chatList.append(s)
            f.close()
            return chatList

    def delete(self):
        os.remove(self.chatName)
