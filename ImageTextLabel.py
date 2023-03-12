from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy


class ImageTextLabel(QWidget):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        # 当前用户名
        self.name = name
        # 创建左侧QLabel，用于显示图片
        self.image_label = QLabel(self)
        self.image_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.image_label.setFixedSize(30, 30)

        # 创建右侧QLabel，用于显示文本
        self.text_label = QLabel(self)
        self.text_label.setWordWrap(True)
        self.text_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.text_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 创建一个水平布局，并将左侧QLabel和右侧QLabel添加进去
        layout = QHBoxLayout(self)
        layout.addWidget(self.image_label)
        layout.addWidget(self.text_label)

        # 设置布局的边距和间距
        layout.setContentsMargins(0, 0, 20, 0)
        layout.setSpacing(10)

    def set_image(self, image_path):
        # 根据图片路径加载图片，并将其显示在左侧QLabel中
        pixmap = QPixmap(image_path).scaled(self.image_label.width(), self.image_label.height(),
                                            Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(pixmap)

    def set_text(self, text):
        # 设置右侧QLabel中的文本，并根据文本内容自动调整高度
        self.text_label.setText(text)
        self.text_label.adjustSize()
        self.adjustSize()

    def mousePressEvent(self, event):
        # 鼠标点击事件，用于设置QLabel可选中，以及鼠标选中文本
        if event.button() == Qt.LeftButton:
            self.text_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

    def focusOutEvent(self, event):
        # 失去焦点事件，用于设置QLabel不可选中
        self.text_label.setTextInteractionFlags(Qt.NoTextInteraction)

    def setStyleSheet(self, styleSheet: str) -> None:
        super(ImageTextLabel, self).setStyleSheet(styleSheet)
