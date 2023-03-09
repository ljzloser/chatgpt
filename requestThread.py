import json

from PyQt5.QtCore import QThread, pyqtSignal
from requests import post


class RequestThread(QThread):
    showError = pyqtSignal(str)
    returnResult = pyqtSignal(str)

    def __init__(self, json_Data):
        super(RequestThread, self).__init__()
        self.result = ''
        self.key = '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'
        self.json_Data = json_Data
        self.url = 'https://api.openai.com/v1/chat/completions'
        self.headers = json.loads(f'''{"Content-Type": "application/json",
                        "Authorization": "Bearer {self.key}"}''')

    def run(self) -> None:
        try:
            response = post(headers=self.headers, json=self.json_Data, url=self.url)
            if response.status_code == 200:
                resultJson: json = response.json()
                if 'error' in resultJson:
                    if 'message' in resultJson['error']:
                        self.showError.emit(resultJson['error']['message'])
                    else:
                        self.showError.emit(str(resultJson['error']))
                else:
                    self.result = resultJson['choices'][0]['message']['content']
                    self.returnResult.emit(self.result)
            else:
                self.showError.emit(f'响应状态码为{response.content}。')
        except Exception as e:
            self.showError.emit(str(e))

        pass
