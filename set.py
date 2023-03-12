import json

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QComboBox, QPushButton, QHBoxLayout, QVBoxLayout

from configXml import Config


class Set(QDialog):
    sign = pyqtSignal(str)

    def __init__(self, parent=None):
        super(Set, self).__init__(parent)
        self.setWindowTitle('设置')

        # 创建控件
        self.openai_key_label = QLabel('OpenAI key:')
        self.openai_key_edit = QLineEdit()
        self.is_stick_label = QLabel('是否置顶:')
        self.is_stick_combo = QComboBox()
        self.is_stick_combo.addItems(['是', '否'])
        self.save_button = QPushButton('保存')
        self.save_button.clicked.connect(self.save)
        self.cancel_button = QPushButton('取消')
        self.cancel_button.clicked.connect(self.hide)
        openai_key = Config().read(name='key')
        top = Config().read(name='top')
        self.openai_key_edit.setText(openai_key)
        self.is_stick_combo.setCurrentText(top)
        # 创建布局
        self.openai_key_layout = QHBoxLayout()
        self.openai_key_layout.addWidget(self.openai_key_label)
        self.openai_key_layout.addWidget(self.openai_key_edit)

        self.is_stick_layout = QHBoxLayout()
        self.is_stick_layout.addWidget(self.is_stick_label)
        self.is_stick_layout.addWidget(self.is_stick_combo)

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.cancel_button)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.openai_key_layout)
        self.main_layout.addLayout(self.is_stick_layout)
        self.main_layout.addLayout(self.button_layout)

        # 设置窗口布局
        self.setLayout(self.main_layout)

    def save(self):
        Config().write('key', self.openai_key_edit.text())
        Config().write('top', self.is_stick_combo.currentText())
        self.hide()
        self.sign.emit(
            '设置保存成功' + json.dumps({'key': self.openai_key_edit.text(), 'top': self.is_stick_combo.currentText()}))
