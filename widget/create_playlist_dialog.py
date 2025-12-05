from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QFont, QPainter, QPen, QColor, QBrush


class CreatePlaylistDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("创建歌单")
        self.setFixedSize(350, 250)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # # 关键：启用输入法支持
        # self.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)
        #
        # # 确保输入框也启用输入法
        # self.edit.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)

        # 主布局
        main = QVBoxLayout()
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # ---------- 顶部标题栏 ----------
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(20, 12, 12, 12)
        lbl_title = QLabel("创建歌单")
        lbl_title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color:#333;")
        top_bar.addWidget(lbl_title)
        top_bar.addStretch()

        # 关闭按钮
        self.btn_close = QPushButton("×")
        self.btn_close.setFixedSize(28, 28)
        self.btn_close.setStyleSheet("""
            QPushButton{
                border:none;
                font-size:18px;
                color:#666;
            }
            QPushButton:hover{
                background-color:#ff4e4e;
                color:white;
                border-radius:4px;
            }
        """)
        self.btn_close.clicked.connect(self.reject)
        top_bar.addWidget(self.btn_close)

        main.addLayout(top_bar)
        # ---------------------------------

        # 内容区
        content = QVBoxLayout()
        content.setContentsMargins(24, 0, 24, 24)
        content.setSpacing(14)

        # 输入框
        self.edit = QLineEdit()
        self.edit.setPlaceholderText("输入歌单标题")
        self.edit.setMaxLength(40)
        self.edit.setStyleSheet("""
            QLineEdit{
                border:1px solid #ddd;
                border-radius:6px;
                padding:10px 12px;
                font-size:14px;
                color:#222;
            }
            QLineEdit:focus{
                border-color:rgb(118,191,249);
            }
        """)
        content.addWidget(self.edit)

        # 创建按钮
        self.btn_create = QPushButton("创建")
        self.btn_create.setFixedHeight(38)
        self.btn_create.setEnabled(False)
        self.btn_create.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_create.setStyleSheet("""
            QPushButton{
                background-color:rgb(118,191,249);
                color:white;
                border-radius:6px;
                font-size:14px;
                font-weight:bold;
            }
            QPushButton:disabled{
                background-color:rgb(160,220,255);
            }
        """)
        content.addWidget(self.btn_create)

        self.edit.textChanged.connect(lambda: self.btn_create.setEnabled(bool(self.edit.text().strip())))
        self.btn_create.clicked.connect(self.accept)

        main.addLayout(content)
        self.setLayout(main)

    # 圆角+阴影
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRect(0, 0, self.width(), self.height())
        painter.setBrush(QBrush(QColor("white")))
        painter.setPen(QPen(QColor("#ddd"), 1))
        painter.drawRoundedRect(rect, 10, 10)

    # 可拖动（标题栏区域）
    def mousePressEvent(self, event):
        if event.position().y() <= 50:   # 标题栏高度
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if hasattr(self, "oldPos"):
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

    # 返回值
    def get_result(self):
        return self.edit.text().strip()
