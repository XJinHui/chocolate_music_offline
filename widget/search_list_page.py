import time
import threading
from PyQt6 import QtCore, QtGui, QtWidgets, QtSvg
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import pyqtSignal
from .music_list_widget import MusicListWidget
from .round_image_label import RoundImageLabel
from .order_menu import OrderMenu

class SearchListScrollArea(QtWidgets.QScrollArea):
    update_music_widget = pyqtSignal(int)

    def __init__(self, music_library, play_music_control, search_music_list, main, parent=None):
        super().__init__(parent)
        self.music_library = music_library
        self.play_music_control = play_music_control
        # self.data = data
        self.main = main
        self.update_music_widget.connect(self._handle_update_music_widget)

        # 添加分页加载相关变量
        self.batch_size = 30  # 每批加载的项目数量
        self.loaded_count_search = 0  # 已加载的项目数量
        self.is_loading = False  # 是否正在加载

        self.search_music_list = search_music_list  # 音乐库全局搜索歌曲列表
        self.search_list = {}  # 搜索结果列表

        self.setupUi()


    def setupUi(self):
        self.setStyleSheet("QScrollArea QScrollBar:vertical {\n"
                    "    border: none;\n"
                    "    background: transparent; /* 滚动条背景透明 */\n"
                    "    width: 4px; /* 垂直滚动条的宽度 */\n"
                    "    margin: 0px;\n"
                    "}\n"
                    "/* 垂直滚动条的手柄 */\n"
                    "QScrollArea QScrollBar::handle:vertical {\n"
                    "    background: #e6e6e6; /* 手柄颜色 */\n"
                    "    border-radius: 2px; /* 圆角半径，设为宽度的一半可得到圆形端点 */\n"
                    "    min-height: 30px; /* 手柄的最小高度 */\n"
                    "}\n"
                    "/* 当鼠标悬停在垂直滚动条手柄上时 */\n"
                    "QScrollArea QScrollBar::handle:vertical:hover {\n"
                    "    background: #a0a0a0; /* 悬停时手柄颜色 */\n"
                    "}\n"
                    "/* 垂直滚动条的顶部和底部箭头按钮（此处设置为隐藏） */\n"
                    "QScrollArea QScrollBar::add-line:vertical, QScrollArea QScrollBar::sub-line:vertical {\n"
                    "    height: 0px; /* 将箭头按钮的高度或宽度设置为0以达到隐藏效果 */\n"
                    "}\n"
                    "/* 垂直滚动条的滚动区域（手柄与箭头之间的区域） */\n"
                    "QScrollArea QScrollBar::add-page:vertical, QScrollArea QScrollBar::sub-page:vertical {\n"
                    "    background: transparent; /* 通常设置为透明或与滚动条背景一致 */\n"
                    "}\n"
                    "\n"
                    "/* 设置水平滚动条 - 原理同垂直滚动条，将 width/height 等属性互换 */\n"
                    "QScrollArea QScrollBar:horizontal {\n"
                    "    border: none;\n"
                    "    background: transparent;\n"
                    "    height: 4px; /* 水平滚动条的高度 */\n"
                    "    margin: 0px;\n"
                    "}\n"
                    "QScrollArea QScrollBar::handle:horizontal {\n"
                    "    background: #c0c0c0;\n"
                    "    border-radius: 2px;\n"
                    "    min-width: 30px; /* 手柄的最小宽度 */\n"
                    "}\n"
                    "QScrollArea QScrollBar::handle:horizontal:hover {\n"
                    "    background: #a0a0a0;\n"
                    "}\n"
                    "QScrollArea QScrollBar::add-line:horizontal, QScrollArea QScrollBar::sub-line:horizontal {\n"
                    "    width: 0px;\n"
                    "}\n"
                    "QScrollArea QScrollBar::add-page:horizontal, QScrollArea QScrollBar::sub-page:horizontal {\n"
                    "    background: transparent;\n"
                    "}")
        self.setWidgetResizable(True)
        self.setObjectName("scrollArea_search_music_list")
        self.verticalScrollBar().valueChanged.connect(self.on_scroll)

        self.scrollWidget = QtWidgets.QWidget()
        self.scrollWidget.setObjectName("scrollWidget")

        self.verticalLayout_search_main = QtWidgets.QVBoxLayout(self.scrollWidget)
        self.verticalLayout_search_main.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_search_main.setSpacing(0)

        self.verticalLayout_search_list = QtWidgets.QVBoxLayout()
        self.verticalLayout_search_list.setObjectName("verticalLayout_search_list")
        self.verticalLayout_search_list.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_search_list.setSpacing(5)
        self.verticalLayout_search_main.addLayout(self.verticalLayout_search_list)
        # self.verticalLayout.addLayout(self.verticalLayout_list)

        self.spacerItem_list_bottom = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                                            QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_search_main.addItem(self.spacerItem_list_bottom)

        self.setWidget(self.scrollWidget)

        #self.verticalLayout_12.addWidget(self)

        self.search_list = {}
        self.loaded_count_search = 0
        self.scrollArea_music_list = None

        self.update_search_music_display = threading.Thread(target=self.display_search_music, args=())
        self.update_search_music_display.setDaemon(True)
        self.update_search_music_display.start()
        # self.display_search_music()


    def on_scroll(self, value):
        # 检查是否滚动到了底部附近
        scroll_bar = self.verticalScrollBar()
        if scroll_bar.maximum() - value < 400:  # 距离底部小于100像素时加载更多
            self.update_search_music_display = threading.Thread(target=self.display_search_music, args=())
            self.update_search_music_display.setDaemon(True)
            self.update_search_music_display.start()
            # self.display_search_music()


    def display_search_music(self):
        if self.is_loading:
            return

        self.is_loading = True

        id_list = self.search_music_list

        # 计算本次要加载的项目范围
        if self.batch_size:
            start_index = self.loaded_count_search
            end_index = min(start_index + 10, len(self.search_music_list))
        else:
            start_index = self.loaded_count_search
            end_index = min(start_index + 10, len(id_list))

        for i in range(start_index, end_index):
            try:
                self.update_music_widget.emit(i)
            except:
                pass
            time.sleep(0.03)

        # 更新已加载数量
        self.loaded_count_search = end_index
        self.is_loading = False

        if self.loaded_count_search >= len(id_list):
            try:
                self.verticalScrollBar().valueChanged.disconnect(self.on_scroll)
            except:
                pass


    def _handle_update_music_widget(self, num):
        widget = QtWidgets.QWidget(parent=self)
        widget.setStyleSheet("""
                                    QWidget {
                                        background-color: rgb(255, 255, 255);
                                        border-radius: 10px;
                                    }
                                    QWidget:hover {
                                        background-color: rgb(230, 230, 230);
                                    }
                                """)
        widget.setMinimumSize(QtCore.QSize(0, 50))
        widget.setMaximumSize(QtCore.QSize(16777215, 50))

        verticalLayout = QtWidgets.QVBoxLayout(widget)
        verticalLayout.setObjectName("verticalLayout")
        verticalLayout.setContentsMargins(0, 0, 0, 0)
        verticalLayout.setSpacing(0)

        music_widget = MusicListWidget(self.music_library.get_song_by_id(self.search_music_list[num]), num, -1,
                                       self.music_library, self.play_music_control, self.main,
                                       self)

        verticalLayout.addWidget(music_widget)
        self.verticalLayout_search_list.addWidget(widget)
        self.search_list[self.search_music_list[num]] = music_widget