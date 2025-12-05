from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import (QDialog,QVBoxLayout, QHBoxLayout, QPushButton,
                             QListWidget, QListWidgetItem,QLabel, QWidget)
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QFont, QPainter, QPen, QColor, QBrush
from .round_image_label import RoundImageLabel


class PlaylistItemWidget(QWidget):
    """自定义歌单项部件"""

    def __init__(self, id, name, count, photo, parent=None):
        super().__init__(parent)
        self.id = id
        self.name = name
        self.count = count
        self.photo = photo

        # 创建主布局（水平布局）
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(10)  # 设置组件间距

        # 创建图片标签
        self.photo_label = RoundImageLabel(radius=5)
        # 设置图片显示大小（可根据需要调整）
        self.photo_label.setMinimumSize(QtCore.QSize(50, 50))
        self.photo_label.setMaximumSize(QtCore.QSize(50, 50))

        success = self.photo_label.setImageSmart(self.photo)
        if not success:
            self.photo_label.setPixmap(QtGui.QPixmap("media/app_photo.png"))

        # 创建右侧文本布局（垂直布局）
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)  # 设置文本间距

        # 歌单名称标签
        self.name_label = QLabel(name)
        self.name_label.setFont(QFont("Microsoft YaHei", 10))

        # 歌曲数量标签
        self.count_label = QLabel(f"{count}首")
        self.count_label.setFont(QFont("Microsoft YaHei", 9))
        self.count_label.setStyleSheet("color: #666;")

        text_layout.addWidget(self.name_label)
        text_layout.addWidget(self.count_label)

        # 将图片和文本布局添加到主布局
        main_layout.addWidget(self.photo_label)
        main_layout.addLayout(text_layout)
        main_layout.addStretch(1)  # 添加弹性空间使内容左对齐

        self.setLayout(main_layout)



class AddMusicDialog(QDialog):
    """歌单选择弹窗"""
    # playlist_selected = pyqtSignal(str)  # 选择歌单的信号

    def __init__(self, music_library, parent=None):
        super().__init__(parent)
        self.music_library = music_library

        self.setWindowTitle("收藏到歌单")
        self.setFixedSize(400, 500)
        self.setStyleSheet('QDialog { background-color: #ffffff; }')
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setup_ui()

        self.populate_playlists()

    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # ---------- 顶部标题栏 ----------
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(20, 12, 12, 12)
        lbl_title = QLabel("添加到歌单")
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

        layout.addLayout(top_bar)

        # 歌单列表
        self.playlist_list = QListWidget()
        self.playlist_list.setAlternatingRowColors(True)
        self.playlist_list.setStyleSheet("""
                            QListWidget {
                                border: none;
                            }
                            QListWidget::item {
                                background-color: rgb(255, 255, 255);
                                border-radius: 10px;
                            }
                            QListWidget::item:hover {
                                background-color: rgb(230, 230, 230);
                            }
                        """)
        self.playlist_list.itemClicked.connect(self.on_playlist_selected)
        layout.addWidget(self.playlist_list)

        self.setLayout(layout)

    def populate_playlists(self):
        """填充歌单数据"""
        self.playlist_list.clear()

        for i in self.music_library.get_playlist_list():
            if i == 1 or i == 2:
                continue
            # 创建自定义部件
            item_widget = PlaylistItemWidget(i,
                                             self.music_library.get_playlist(i)['name'],
                                             self.music_library.get_playlist(i)['num'],
                                             self.music_library.get_playlist(i)['photo'])

            # 创建列表项
            item = QListWidgetItem(self.playlist_list)
            item.setSizeHint(item_widget.sizeHint())

            # 将部件添加到列表项
            self.playlist_list.addItem(item)
            self.playlist_list.setItemWidget(item, item_widget)

    def on_playlist_selected(self, item):
        """处理歌单选择"""
        widget = self.playlist_list.itemWidget(item)
        if widget:
            self._result = widget.id
            self.accept()

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

