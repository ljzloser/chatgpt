import datetime

from PyQt5.QtCore import Qt, QTranslator
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QScrollArea, QLineEdit, QMainWindow, \
    QAction, QHBoxLayout, QListWidget, QListWidgetItem, QMessageBox

from ImageTextLabel import ImageTextLabel
from labelPushButtonItem import LabelPushButtonItem
from writeLog import WriteLog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建日志类
        self.log = WriteLog()

        # 设置窗口标志
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        # 设置窗口属性
        self.setAttribute(Qt.WA_DeleteOnClose)

        # 设置窗口标题
        self.setWindowTitle("QtChatGpt")
        # 设置窗口Icon
        self.setWindowIcon(QIcon('res/bot.png'))
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
        self.layout.setContentsMargins(1, 1, 1, 1)

        # 常见一个QWidget,并设置大小
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
        self.labelPushButtonItem = LabelPushButtonItem("新增聊天", 'res/insert.png')
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
        for i in range(20):
            path = 'res/delete.png'
            labelPushButtonItem = LabelPushButtonItem(str(i), path)
            item = QListWidgetItem(self.listWidget)
            item.setSizeHint(labelPushButtonItem.sizeHint())
            self.listWidget.setItemWidget(item, labelPushButtonItem)

        self.setCentralWidget(self.hWidget)
        self.setGeometry(100, 100, 600, 600)
        self.setFixedWidth(600)

        for i in range(20):
            imagePath = ''
            style = ''
            if i % 2 == 0:
                imagePath = 'res/user.png'
                style = self.style1
            else:
                imagePath = 'res/bot.png'
                style = self.style2

            self.insert_image_text_label(imagePath,
                                         '这是一段很长的文本---------------------------------------------------------------'
                                         '这是一段很长的文本---------------------------------------------------------------'
                                         '这是一段很长的文本---------------------------------------------------------------'
                                         '这是一段很长的文本---------------------------------------------------------------'
                                         , style)

    def insert_image_text_label(self, image_path, text, styleSheet):
        # 创建一个ImageTextLabel，并设置图片和文本
        image_text_label = ImageTextLabel()
        image_text_label.set_image(image_path)
        image_text_label.set_text(text)
        image_text_label.setStyleSheet(styleSheet)

        # 将ImageTextLabel添加到QVBoxLayout中
        self.layout.insertWidget(self.layout.count(), image_text_label)
        # 滚动到底部
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setMaximum(99999)
        scrollbar.setValue(scrollbar.maximum() + 99999)

    def on_line_edit_return_pressed(self):
        text = self.line_edit.text()
        self.line_edit.clear()
        self.insert_image_text_label('res/user.png', text, self.style1)

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


if __name__ == '__main__':
    import sys
    import os

    app = QApplication(sys.argv)
    window = MainWindow()
    # 加载中文翻译
    if os.path.exists('res/qt_zh_CN.qm'):
        translator = QTranslator()
        translator.load('res/qt_zh_CN.qm')
        app.installTranslator(translator)
        window.setDebug(debug=f'加载 qt_zh_CN.qm 翻译文件加载成功！', isShow=False, isLog=True)
    else:
        window.setDebug(debug='加载qt_zh_CN.qm 翻译文件加载失败！', isShow=True, isLog=True)

    # 加载样式表
    if os.path.exists('res/style.qss'):
        with open('res/style.qss', 'r', encoding='UTF-8') as f:
            app.setStyleSheet(f.read())
            window.setDebug(debug=f'加载 style.qss 样式表加载成功！', isShow=False, isLog=True)
    else:
        window.setDebug(debug='加载 style.qss 样式表加载失败！', isShow=True, isLog=True)
    try:
        window.show()
        window.setDebug(debug='程序启动成功！', isShow=False, isLog=True)
    except Exception as e:
        window.setDebug(debug='程序启动失败！' + str(e), isShow=True, isLog=True)
    sys.exit(app.exec_())
