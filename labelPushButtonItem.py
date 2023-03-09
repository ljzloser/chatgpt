from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QWidget, QPushButton


class LabelPushButtonItem(QWidget):
    itemButtonClicked = pyqtSignal(QWidget)

    def __init__(self, labelText, pushButtonText, parent=None):
        super().__init__(parent)
        self.labelText = labelText
        self.pushButtonText = pushButtonText

        self.label = QLabel(self.labelText, parent=self)
        self.pushButton = QPushButton(parent=self)
        icon = QIcon(pushButtonText)
        self.pushButton.setIcon(icon)
        self.pushButton.setFixedSize(30, 30)
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.pushButton)
        self.setLayout(self.layout)
        self.pushButton.clicked.connect(self.buttonClicked)

    def buttonClicked(self):
        self.itemButtonClicked.emit(self)
