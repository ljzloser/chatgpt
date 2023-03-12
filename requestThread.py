import json

# import requests
from PyQt5.QtCore import QThread, pyqtSignal, QUrl, QEventLoop
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager, QNetworkReply

from configXml import Config


class RequestThread(QThread):
    showError = pyqtSignal(str)
    returnResult = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        config = Config()
        key = config.read('key')
        self.result = ''
        self.key = f'Bearer {key}'
        self.json_Data = {}
        self.url = 'https://api.openai.com/v1/chat/completions'

    def setJson(self, dataJson):
        self.json_Data = dataJson

    def run(self):
        try:
            manager = QNetworkAccessManager()
            request = QNetworkRequest(QUrl(self.url))
            request.setHeader(QNetworkRequest.ContentTypeHeader, 'application/json')
            request.setRawHeader(b'Authorization', self.key.encode())
            reply = manager.post(request, json.dumps(self.json_Data).encode())
            # 等待请求完成
            loop = QEventLoop()
            reply.finished.connect(loop.quit)
            loop.exec_()
            # 处理响应
            if reply.error() == QNetworkReply.NoError:
                resultJson = json.loads(reply.readAll().data().decode('utf-8'))
                if 'choices' in resultJson:
                    self.result = resultJson['choices'][0]['message']['content']
                    self.returnResult.emit(self.result)
                elif 'data' in resultJson:
                    self.result = resultJson['data'][0]['b64_json']
                    self.returnResult.emit(self.result)
            else:
                resultJson = json.loads(reply.readAll().data().decode('utf-8'))
                if 'error' in resultJson:
                    if 'message' in resultJson['error']:
                        self.showError.emit(reply.errorString() + resultJson['error']['message'])
                        print(reply.errorString() + resultJson['error']['message'])
                    else:
                        self.showError.emit(reply.errorString() + str(resultJson['error']))
                        print(reply.errorString() + str(resultJson['error']))

            reply.deleteLater()
        except Exception as e:
            self.showError.emit(str(e))
