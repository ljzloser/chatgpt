import datetime
import json
import os
import re

# import requests
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl, QEventLoop, QTimer, QCoreApplication
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager, QNetworkReply
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QLineEdit, QMainWindow, \
    QAction, QHBoxLayout, QListWidget, QMessageBox, QListWidgetItem, QSystemTrayIcon, QMenu

from ImageTextLabel import ImageTextLabel
from configXml import Config
from labelPushButtonItem import LabelPushButtonItem
from set import Set
from writeTxt import Log, ChatLog


def get_max_chat_number():
    # 获取Chat目录下所有文件名
    files = os.listdir('Chat')
    # 提取所有文件名中的数字部分
    numbers = [int(re.findall('\d+', f)[0]) + 1 for f in files if re.findall('\d+', f)]
    # 如果没有数字部分，则返回0
    if not numbers:
        return 0
    # 找到最大的数字并返回
    return max(numbers)


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
                self.result = resultJson['choices'][0]['message']['content']
                self.returnResult.emit(self.result)
            else:
                resultJson = json.loads(reply.readAll().data().decode('utf-8'))
                if 'error' in resultJson:
                    if 'message' in resultJson['error']:
                        self.showError.emit(reply.errorString() + resultJson['error']['message'])
                    else:
                        self.showError.emit(reply.errorString() + str(resultJson['error']))

            reply.deleteLater()
        except Exception as e:
            self.showError.emit(str(e))
        # try:
        #     response = requests.post(url=self.url, json=self.json_Data, headers=self.headers)
        #     print('ssss')
        #     if response.status_code == 200:
        #         resultJson: json = response.json()
        #         if 'error' in resultJson:
        #             if 'message' in resultJson['error']:
        #                 self.showError.emit(resultJson['error']['message'])
        #             else:
        #                 self.showError.emit(str(resultJson['error']))
        #         else:
        #             self.result = resultJson['choices'][0]['message']['content']
        #             self.returnResult.emit(self.result)
        #     else:
        #         self.showError.emit(f'响应状态码为{response.content}。')
        # except Exception as e:
        #     self.showError.emit(str(e))
        # self.returnResult.emit('你好阿')


class MainWindow(QMainWindow):
    list_delete = pyqtSignal()

    def __init__(self):
        super().__init__()
        if not os.path.exists('Chat'):
            os.mkdir('Chat')
        # 托盘图标
        self.trayIcon = QSystemTrayIcon(QIcon("res/icon.png"))
        self.trayIcon.show()
        self.trayIcon.activated.connect(self.onActivated)
        self.set = Set(self)
        self.set.sign.connect(lambda x: self.setDebug(debug=x, isShow=False, isLog=True))
        # 增加托盘菜单
        self.menu = QMenu(self)
        setAction = QAction("设置", self)
        quitAction = QAction("退出", self)
        self.menu.addAction(setAction)
        self.menu.addAction(quitAction)

        setAction.triggered.connect(lambda: (self.hide(), self.set.exec()))
        quitAction.triggered.connect(QCoreApplication.quit)

        # 当前聊天的filename
        self.chatFilename = f'Chat{get_max_chat_number()}'
        # 请求线程及对应的引号
        self.requestThread = RequestThread()
        self.requestThread.returnResult.connect(
            lambda x: (self.insert_image_text_label(text=x, image_path='res/bot.png', styleSheet=self.style2,
                                                    name='assistant'),
                       self.writeChat()))
        self.requestThread.showError.connect(
            lambda x: self.setDebug(debug=x, isShow=True, isLog=True))
        # 当前Json
        self.chatJson = {}
        self.initChatJson()
        # 创建日志类
        self.log = Log()

        # 设置窗口属性
        self.setAttribute(Qt.WA_DeleteOnClose)

        # 设置窗口标题
        self.setWindowTitle("QtChatGpt")
        # 设置窗口Icon
        self.setWindowIcon(QIcon('res/icon.png'))
        # 创建两个样式表
        self.style1 = """
            QWidget{background-color: #ffa500;
            color: #2980b9;
            border: 1px solid #2980b9};
        """

        self.style2 = """
            QWidget{background-color: #2980b9;
            color: #ffa500;
            border: 1px solid #ffa500};
        """
        # 创建一个垂直布局，并将其放入一个QWidget中
        self.widget = QWidget(self)
        self.widget.setMinimumSize(400, 300)  # 设置最小大小
        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(1, 1, 1, 10)

        # 创建一个QWidget,并设置大小
        self.titleWidget = QLabel(self.widget)
        self.titleWidget.setText("Debug:")
        self.titleWidget.setStyleSheet(' color: yellow;border: 1px solid red')
        self.titleWidget.setFixedHeight(30)

        # 创建一个QLineEdit，并设置其位置和大小
        self.line_edit = QLineEdit(self.widget)
        self.line_edit.setMinimumSize(400, 30)
        self.line_edit.returnPressed.connect(self.on_line_edit_return_pressed)
        self.sendAction = QAction("发送")
        icon = QIcon("res/send (2).png")
        self.sendAction.setIcon(icon)
        self.sendAction.triggered.connect(self.on_line_edit_return_pressed)
        self.line_edit.addAction(self.sendAction, QLineEdit.TrailingPosition)
        # 创建一个QScrollArea，并将QWidget放入其中
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 创建一个垂直布局，并将QVBoxLayout和QLineEdit放入其中
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.titleWidget)
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.line_edit)
        self.main_layout.setContentsMargins(5, 5, 0, 0)
        self.textWidget = QWidget(self)
        self.textWidget.setLayout(self.main_layout)

        # 创建一个水平布局，并将widgetList和textWidget放入其中
        self.main_layout2 = QHBoxLayout()
        self.listWidget = QListWidget(self)
        self.listWidget.setFixedWidth(120)
        self.listWidget.itemSelectionChanged.connect(self.on_item_selected)
        self.labelPushButtonItem = LabelPushButtonItem("新增聊天", 'res/insert.png')
        self.labelPushButtonItem.itemButtonClicked.connect(
            lambda: (self.setDebug(debug='点击新增聊天', isShow=False, isLog=True),
                     self.vboxClear()))
        self.widgetList = QWidget(self)
        self.main_layout2.addWidget(self.widgetList)
        self.main_layout2.addWidget(self.textWidget)
        self.hWidget = QWidget(self)
        self.hWidget.setLayout(self.main_layout2)

        # 创建一个垂直布局，并将labelPushButtonItem和listWidget放入其中
        self.layoutList = QVBoxLayout()
        self.layoutList.addWidget(self.labelPushButtonItem)
        self.layoutList.addWidget(self.listWidget)
        self.widgetList.setLayout(self.layoutList)

        self.setCentralWidget(self.hWidget)
        self.setGeometry(100, 100, 600, 600)
        self.setFixedWidth(600)
        self.loadListWidget()
        self.list_delete.connect(self.loadListWidget)
        self.timer = QTimer()
        self.timer.timeout.connect(self.threadStats)
        self.timer.start(1)

    def insert_image_text_label(self, image_path, text, styleSheet, name):
        # 创建一个ImageTextLabel，并设置图片和文本
        image_text_label = ImageTextLabel(name)
        image_text_label.set_image(image_path)
        image_text_label.set_text(text)
        image_text_label.setStyleSheet(styleSheet)
        self.chatJson['messages'].append({"role": name, "content": text})
        # 将ImageTextLabel添加到QVBoxLayout中
        self.layout.insertWidget(self.layout.count(), image_text_label)
        # 滚动到底部
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setMaximum(99999)
        scrollbar.setValue(scrollbar.maximum() + 99999)

    def on_line_edit_return_pressed(self):
        text = self.line_edit.text()
        self.line_edit.clear()
        self.insert_image_text_label('res/user.png', text, self.style1, 'user')
        # 发送请求

        self.requestThread.setJson(self.chatJson)
        self.requestThread.start()

    def show(self) -> None:
        super(MainWindow, self).show()
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def setDebug(self, debug: str, isShow: bool, isLog: bool):
        self.titleWidget.setText(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} : {debug}')
        if isShow:
            self.showMessageBox(debug)
        if isLog:
            self.log.write(debug=debug)

    def showMessageBox(self, debug):
        QMessageBox.warning(self, 'Debug', f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} : \n{debug}')

    def initChatJson(self):
        self.chatJson = {"messages": [], "model": "gpt-3.5-turbo"}

    def on_item_selected(self):
        # 获取选中的 Item
        items = self.listWidget.selectedItems()

        if items:
            # 通过 item 获取到自定义类对象
            selected_item = items[0]
            labelPushButtonItem = selected_item.data(Qt.UserRole)
            if isinstance(labelPushButtonItem, LabelPushButtonItem):
                self.initChatJson()
                self.vboxClear()
                self.chatFilename = labelPushButtonItem.labelText
                chat_list = ChatLog(self.chatFilename).read()
                for chat in chat_list:
                    role = chat['role']
                    content = chat['content']
                    image_path = ''
                    style = ''
                    if role == 'user':
                        image_path = 'res/user.png'
                        style = self.style1
                    else:
                        image_path = 'res/bot.png'
                        style = self.style2
                    self.insert_image_text_label(image_path=image_path, text=content, styleSheet=style, name=role)

    def writeChat(self):
        if len(self.chatJson['messages']) > 1:
            for i in self.chatJson['messages'][-2:]:
                ChatLog(self.chatFilename).write(role=i['role'], content=i['content'])

        self.loadListWidget()

    def loadListWidget(self):
        files = os.listdir('Chat')
        self.listWidget.clear()
        for file in files:
            item = QListWidgetItem(self.listWidget)
            labelPushButtonItem = LabelPushButtonItem(file.split('.')[0], 'res/delete.png')
            labelPushButtonItem.itemButtonClicked.connect(
                lambda x: (self.setDebug(debug=x, isShow=False, isLog=True),
                           self.vboxClear(),
                           self.list_delete.emit()))
            item.setSizeHint(labelPushButtonItem.size())
            item.setData(Qt.UserRole, labelPushButtonItem)
            self.listWidget.setItemWidget(item, labelPushButtonItem)

    def vboxClear(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.chatFilename = f'Chat{get_max_chat_number()}'

    def threadStats(self):
        stats = self.requestThread.isRunning()
        self.listWidget.setDisabled(stats)
        self.line_edit.setDisabled(stats)
        self.sendAction.setDisabled(stats)
        self.labelPushButtonItem.setDisabled(stats)

    def onActivated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            # 点击托盘图标时，显示窗口
            if self.isVisible():
                self.hide()
            else:
                self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)

                # 获取托盘图标的矩形区域
                rect = self.trayIcon.geometry()

                # 计算窗口的位置，使其显示在托盘图标的正上方
                x = rect.x() - self.width() + rect.width()
                y = rect.y() - self.height() - 30

                # 将窗口移动到指定位置
                self.move(x, y)
                self.show()
                self.raise_()
        elif reason == QSystemTrayIcon.Context:
            # 在鼠标右键单击时显示托盘菜单
            self.menu.exec_(QCursor.pos())

    def leaveEvent(self, event):
        # 鼠标当前位置
        cursorPos = QCursor.pos()
        # 窗口的位置和大小
        widgetGeometry = self.geometry()
        # 判断鼠标是否在窗口内
        if not widgetGeometry.contains(cursorPos) and not Config().read('top') == '是':
            # 隐藏窗口
            self.hide()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
