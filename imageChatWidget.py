import base64
import datetime

from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QApplication, QFrame, QPushButton, QFileDialog, \
    QAction

from requestThread import RequestThread


class ImageChatWidget(QWidget):
    showError = pyqtSignal(str)

    def __init__(self):
        super(ImageChatWidget, self).__init__()
        # 创建请求进程
        self.requestThread = RequestThread()
        self.requestThread.url = 'https://api.openai.com/v1/images/generations'
        self.requestThread.returnResult.connect(self.setImage)
        self.requestThread.showError.connect(self.showError)
        # 纵向布局
        self.setWindowTitle("QtChatGpt-Image")
        self.layout = QVBoxLayout()
        self.pushButton = QPushButton(self)
        self.pushButton.setText('保存')
        self.pushButton.clicked.connect(self.save_image)
        self.titleLabel = QLabel(self)
        self.label = QLabel(self)
        self.label.setFrameShape(QFrame.Box)
        self.label.setFixedSize(512, 512)
        self.lineEdit = QLineEdit(self)
        self.lineEdit.returnPressed.connect(self.on_line_edit_return_pressed)
        self.sendAction = QAction("发送")
        icon = QIcon("res/send (2).png")
        self.sendAction.setIcon(icon)
        self.sendAction.triggered.connect(self.on_line_edit_return_pressed)
        self.lineEdit.addAction(self.sendAction, QLineEdit.TrailingPosition)
        self.layout.addWidget(self.pushButton)
        self.layout.addWidget(self.titleLabel)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.lineEdit)
        self.setLayout(self.layout)
        self.titleText = ''
        # 定时器监控线程状态
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.threadRun)
        self.timer.start(1)
        self.beginTime = None
        # self.setImage('res/bot.png')
        # 设置窗口Icon
        self.setWindowIcon(QIcon('res/icon.png'))

    def show(self) -> None:
        super(ImageChatWidget, self).show()
        self.setFixedSize(self.size())

    def setImage(self, filename):
        img_data = base64.b64decode(filename)

        # 将二进制图像数据转换为QPixmap对象
        pixmap = QPixmap()
        pixmap.loadFromData(img_data)

        self.label.setPixmap(pixmap)

    def save_image(self):
        try:
            # 获取Pixmap
            pixmap = self.label.pixmap()
            if pixmap is not None:
                # 弹出文件保存对话框
                filename, _ = QFileDialog.getSaveFileName(self, '保存图片', '', '图片文件 (*.png)')

                if filename:
                    # 如果用户选择了文件名，则将图片保存到该文件
                    pixmap.save(filename)
                    self.showError.emit(f'{filename}保存成功!')
            else:
                pass
        except Exception as e:
            self.showError.emit(str(e))

    def on_line_edit_return_pressed(self):
        resJson = {
            "prompt": self.lineEdit.text(),
            "n": 1,
            "size": "512x512",
            "response_format": "b64_json"
        }

        # 发送请求
        self.titleLabel.setText(self.lineEdit.text())
        self.lineEdit.clear()
        self.requestThread.setJson(resJson)
        self.requestThread.start()
        self.beginTime = datetime.datetime.now()

    def threadRun(self):
        if self.requestThread.isRunning():
            time = int((datetime.datetime.now() - self.beginTime).total_seconds())
            self.setWindowTitle(f'正在请求:{time}S')
        else:
            self.setWindowTitle("QtChatGpt-Image")


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = ImageChatWidget()
    window.show()
    sys.exit(app.exec_())
