import time
import sqlite3
import threading
from PyQt6 import QtCore, QtGui, QtWidgets, QtSvg
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import pyqtSignal
from .music_list_widget import MusicListWidget
from .round_image_label import RoundImageLabel
from .order_menu import OrderMenu
# from .files_import_music import files_import_music
# from .hover_click_filter import HoverClickFilter

class MusicListScrollArea(QtWidgets.QScrollArea):
    update_music_widget = pyqtSignal(list, int, int)

    def __init__(self, music_library, play_music_control, id, main, parent=None):
        super().__init__(parent)
        self.music_library = music_library
        self.play_music_control = play_music_control
        # self.data = data
        self.main = main
        self.id = id

        self.update_music_widget.connect(self._handle_update_music_widget)

        self.list = {}

        self.search_music_list = []
        self.search_list = {}
        self.text = ''

        # 添加分页加载相关变量
        self.batch_size = 15  # 每批加载的项目数量
        self.loaded_count = 0  # 已加载的项目数量
        self.loaded_count_search = 0
        self.is_loading = False  # 是否正在加载

        self.setupUi()

        # 连接滚动条信号
        self.verticalScrollBar().valueChanged.connect(self.on_scroll)

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
        self.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 764, 410))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget_12 = QtWidgets.QWidget(parent=self.scrollAreaWidgetContents)
        self.widget_12.setMinimumSize(QtCore.QSize(0, 150))
        self.widget_12.setMaximumSize(QtCore.QSize(16777215, 150))
        self.widget_12.setObjectName("widget_12")
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout(self.widget_12)
        self.horizontalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_15.setSpacing(20)
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")

        self.label_playlist_photo_2 = RoundImageLabel(radius=15)
        self.label_playlist_photo_2.setMinimumSize(QtCore.QSize(150, 150))
        self.label_playlist_photo_2.setMaximumSize(QtCore.QSize(150, 150))

        if self.music_library.get_playlist(self.id)['photo'] == "media/app_photo.png":
            self.label_playlist_photo_2.setPixmap(QtGui.QPixmap("media/app_photo.png"))
        else:
            success = self.label_playlist_photo_2.setImageSmart(self.music_library.get_playlist(self.id)['photo'])
            if not success:
                self.label_playlist_photo_2.setPixmap(QtGui.QPixmap("media/app_photo.png"))

        self.label_playlist_photo_2.setScaledContents(True)
        self.label_playlist_photo_2.setObjectName("label_playlist_photo_2")

        self.horizontalLayout_15.addWidget(self.label_playlist_photo_2)
        self.verticalLayout_12 = QtWidgets.QVBoxLayout()
        self.verticalLayout_12.setSpacing(5)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.label_playlist_name_2 = QtWidgets.QLabel(parent=self.widget_12)
        self.label_playlist_name_2.setObjectName("label_playlist_name_2")
        self.verticalLayout_12.addWidget(self.label_playlist_name_2)
        self.label_playlist_num_2 = QtWidgets.QLabel(parent=self.widget_12)
        self.label_playlist_num_2.setObjectName("label_playlist_num_2")
        self.verticalLayout_12.addWidget(self.label_playlist_num_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_12.addItem(spacerItem)
        self.horizontalLayout_16 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_16.setSpacing(5)
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.widget_12)
        self.pushButton_2.setMinimumSize(QtCore.QSize(100, 40))
        self.pushButton_2.setMaximumSize(QtCore.QSize(100, 40))
        self.pushButton_2.setStyleSheet("background-color: rgb(118, 191, 249);\n"
                                        "border: none;\n"
                                        "color: rgb(255, 255, 255);\n"
                                        "border-radius: 10px;")
        icon = QtGui.QIcon()
        icon.addPixmap(self.load_svg_icon("media/play_fill.svg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.pushButton_2.setIcon(icon)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.pushButton_2.clicked.connect(self.play_music)
        self.horizontalLayout_16.addWidget(self.pushButton_2)
        if self.music_library.get_playlist(self.id)['num'] == 0 and self.id != 0:
            self.pushButton_3 = QtWidgets.QPushButton(parent=self.widget_12)
            self.pushButton_3.setMinimumSize(QtCore.QSize(100, 40))
            self.pushButton_3.setMaximumSize(QtCore.QSize(100, 40))
            self.pushButton_3.setStyleSheet("background-color: rgb(118, 191, 249);\n"
                                            "border: none;\n"
                                            "color: rgb(255, 255, 255);\n"
                                            "border-radius: 10px;")
            icon = QtGui.QIcon()
            icon.addPixmap(self.load_svg_icon("media/arrowshape_down_to_line_white_fill.svg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
            self.pushButton_3.setIcon(icon)
            self.pushButton_3.setText('导入音乐')
            self.pushButton_3.setObjectName("pushButton_3")
            self.pushButton_3.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            self.pushButton_3.clicked.connect(self.import_music)
            self.horizontalLayout_16.addWidget(self.pushButton_3)
        else:
            self.pushButton_3 = None

        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_16.addItem(spacerItem1)
        self.widget_13 = QtWidgets.QWidget(parent=self.widget_12)
        self.widget_13.setMinimumSize(QtCore.QSize(175, 30))
        self.widget_13.setMaximumSize(QtCore.QSize(175, 30))
        self.widget_13.setStyleSheet("background-color: rgb(255, 255, 255);\n"
            "border-radius: 15px;")
        self.widget_13.setObjectName("widget_13")
        self.horizontalLayout_17 = QtWidgets.QHBoxLayout(self.widget_13)
        self.horizontalLayout_17.setContentsMargins(10, 0, 10, 0)
        self.horizontalLayout_17.setSpacing(5)
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.horizontalLayout_18 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_18.setSpacing(10)
        self.horizontalLayout_18.setObjectName("horizontalLayout_18")
        self.label_6 = QtWidgets.QLabel(parent=self.widget_13)
        self.label_6.setMinimumSize(QtCore.QSize(20, 20))
        self.label_6.setMaximumSize(QtCore.QSize(20, 20))
        self.label_6.setText("")
        self.label_6.setPixmap(self.load_svg_icon("media/magnifyingglass.svg"))
        self.label_6.setScaledContents(True)
        self.label_6.setObjectName("label_6")
        # self.label_6.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        # self.label_6_filter = HoverClickFilter()
        # self.label_6.installEventFilter(self.label_6_filter)
        # self.label_6_filter.clicked.connect(self.search_music_list)
        self.horizontalLayout_18.addWidget(self.label_6)

        self.pushButton_order = QtWidgets.QPushButton(parent=self.widget_12)
        self.pushButton_order.setMinimumSize(QtCore.QSize(70, 30))
        self.pushButton_order.setMaximumSize(QtCore.QSize(70, 30))
        self.pushButton_order.setStyleSheet("background-color: rgb(255,255,255);\n"
                                            "border: none;\n"
                                            "border-radius: 15px;")
        icon = QtGui.QIcon()
        icon.addPixmap(self.load_svg_icon("media/text_and_arrow_down.svg"), QtGui.QIcon.Mode.Normal,
                       QtGui.QIcon.State.Off)
        self.pushButton_order.setIcon(icon)

        self.pushButton_order.setObjectName("pushButton_3")
        self.pushButton_order.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.pushButton_order.clicked.connect(self.order_music_list)
        self.horizontalLayout_16.addWidget(self.pushButton_order)
        self.update_order()
        # self.orderMenu = OrderMenu(self.playlist['order'], self)
        self.orderMenu = OrderMenu(self.music_library.get_playlist(self.id)['order'], self)
        # self.orderMenu = OrderMenu(self.music_library.playlist[f'{self.id}']['order'], self)
        self.orderMenu.sortChanged.connect(self.update_music_order)

        self.lineEdit_music_list_search = QtWidgets.QLineEdit(parent=self.widget_13)
        self.lineEdit_music_list_search.setMinimumSize(QtCore.QSize(130, 25))
        self.lineEdit_music_list_search.setMaximumSize(QtCore.QSize(130, 25))
        self.lineEdit_music_list_search.setStyleSheet("border: none;")
        self.lineEdit_music_list_search.setText("")
        self.lineEdit_music_list_search.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        self.lineEdit_music_list_search.setObjectName("lineEdit_music_list_search")
        self.lineEdit_music_list_search.textChanged.connect(self.search_music)

        self.horizontalLayout_18.addWidget(self.lineEdit_music_list_search)
        self.horizontalLayout_17.addLayout(self.horizontalLayout_18)
        self.horizontalLayout_16.addWidget(self.widget_13)
        self.verticalLayout_12.addLayout(self.horizontalLayout_16)
        self.horizontalLayout_15.addLayout(self.verticalLayout_12)
        self.verticalLayout.addWidget(self.widget_12)
        self.widget_3 = QtWidgets.QWidget(parent=self.scrollAreaWidgetContents)
        self.widget_3.setMinimumSize(QtCore.QSize(0, 30))
        self.widget_3.setMaximumSize(QtCore.QSize(16777215, 30))
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_7.setSpacing(5)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.widget_6 = QtWidgets.QWidget(parent=self.widget_3)
        self.widget_6.setMinimumSize(QtCore.QSize(240, 0))
        self.widget_6.setMaximumSize(QtCore.QSize(200, 16777215))
        self.widget_6.setObjectName("widget_6")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.widget_6)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setSpacing(10)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_13 = QtWidgets.QLabel(parent=self.widget_6)
        self.label_13.setMinimumSize(QtCore.QSize(30, 30))
        self.label_13.setMaximumSize(QtCore.QSize(30, 30))
        self.label_13.setObjectName("label_13")
        self.horizontalLayout_6.addWidget(self.label_13)
        self.label_15 = QtWidgets.QLabel(parent=self.widget_6)
        self.label_15.setMinimumSize(QtCore.QSize(195, 0))
        self.label_15.setMaximumSize(QtCore.QSize(195, 16777215))
        self.label_15.setObjectName("label_15")
        self.horizontalLayout_6.addWidget(self.label_15)
        self.horizontalLayout_7.addWidget(self.widget_6)
        self.widget_5 = QtWidgets.QWidget(parent=self.widget_3)
        self.widget_5.setObjectName("widget_5")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.widget_5)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(5)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_5 = QtWidgets.QLabel(parent=self.widget_5)
        self.label_5.setMinimumSize(QtCore.QSize(130, 0))
        self.label_5.setMaximumSize(QtCore.QSize(130, 16777215))
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_4.addWidget(self.label_5)
        self.label_10 = QtWidgets.QLabel(parent=self.widget_5)
        self.label_10.setMinimumSize(QtCore.QSize(130, 0))
        self.label_10.setMaximumSize(QtCore.QSize(130, 16777215))
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_4.addWidget(self.label_10)
        self.label_11 = QtWidgets.QLabel(parent=self.widget_5)
        self.label_11.setMinimumSize(QtCore.QSize(30, 20))
        self.label_11.setMaximumSize(QtCore.QSize(30, 20))
        self.label_11.setScaledContents(False)
        self.label_11.setObjectName("label_11")
        self.horizontalLayout_4.addWidget(self.label_11)
        self.label_12 = QtWidgets.QLabel(parent=self.widget_5)
        self.label_12.setMinimumSize(QtCore.QSize(35, 0))
        self.label_12.setMaximumSize(QtCore.QSize(35, 16777215))
        self.label_12.setObjectName("label_12")
        self.horizontalLayout_4.addWidget(self.label_12)
        self.horizontalLayout_7.addWidget(self.widget_5)
        self.verticalLayout.addWidget(self.widget_3)
        self.verticalLayout_list = QtWidgets.QVBoxLayout()
        self.verticalLayout_list.setObjectName("verticalLayout_list")
        self.verticalLayout_list.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_list.setSpacing(5)
        self.verticalLayout.addLayout(self.verticalLayout_list)

        self.verticalLayout_search_list = QtWidgets.QVBoxLayout()
        self.verticalLayout_search_list.setObjectName("verticalLayout_list")
        self.verticalLayout_search_list.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_search_list.setSpacing(5)
        self.verticalLayout.addLayout(self.verticalLayout_search_list)

        # self.add_song_item()
        self.update_music_display= threading.Thread(target=self.load_next_batch, args=())
        self.update_music_display.setDaemon(True)
        self.update_music_display.start()
        # self.load_next_batch()

        self.spacerItem_list_bottom = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(self.spacerItem_list_bottom)
        self.setWidget(self.scrollAreaWidgetContents)

        self.retranslateUi()
        # QtCore.QMetaObject.connectSlotsByName()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "Form"))
        self.label_playlist_name_2.setText(_translate("Form", f"<html><head/><body><p><span style=\" font-size:18pt; font-weight:700;\">{self.music_library.get_playlist(self.id)['name']}</span></p></body></html>"))

        self.label_playlist_num_2.setText(_translate("Form", f"{self.music_library.get_playlist(self.id)['num']}首歌曲"))
        self.pushButton_2.setText(_translate("Form", "播放全部"))
        self.lineEdit_music_list_search.setPlaceholderText(_translate("Form", "搜索"))
        self.label_13.setText(_translate("Form", "<html><head/><body><p align=\"center\"><span style=\" font-size:10pt; color:#787878;\">#</span></p></body></html>"))
        self.label_15.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt; color:#787878;\">歌曲名</span></p></body></html>"))
        self.label_5.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt; color:#787878;\">歌手</span></p></body></html>"))
        self.label_10.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt; color:#787878;\">专辑</span></p></body></html>"))
        self.label_11.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt; color:#787878;\">喜欢</span></p></body></html>"))
        self.label_12.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt; color:#787878;\">时长</span></p></body></html>"))

    def import_music(self):
        directory_path = QFileDialog.getExistingDirectory(
            None,
            "选择歌曲文件夹",
            "",  # 初始目录，可选路径如 "C:/" 或 "/home"
            QFileDialog.Option.ShowDirsOnly  # 可选选项：只显示目录
        )
        if directory_path:
            self.music_library.files_import_music(directory_path,self.id)
            self.update_page()
            # self.add_song_item()

    def update_page(self):
        self.clear_layout(self.verticalLayout_list)
        self.label_playlist_num_2.setText(f"{self.music_library.get_playlist(self.id)['num']}首歌曲")
        if self.music_library.get_playlist(self.id)['num'] > 0:
            self.main.update_playlist_list()
            if self.pushButton_3:
                self.pushButton_3.deleteLater()
                self.pushButton_3 = None
            success = self.label_playlist_photo_2.setImageSmart(self.music_library.get_playlist(self.id)['photo'])
            if not success:
                self.label_playlist_photo_2.setPixmap(QtGui.QPixmap("media/app_photo.png"))

        self.list = {}
        self.loaded_count = 0
        self.update_music_display = threading.Thread(target=self.load_next_batch, args=())
        self.update_music_display.setDaemon(True)
        self.update_music_display.start()
        if self.search_music_list:
            self.loaded_count_search = 0
            self.clear_layout(self.verticalLayout_search_list)
            for i in range(self.verticalLayout_list.count()):
                item = self.verticalLayout_list.itemAt(i)
                widget = item.widget()  # 获取控件
                widget.hide()
            self.update_search_music_display = threading.Thread(target=self.display_search_music, args=())
            self.update_search_music_display.setDaemon(True)
            self.update_search_music_display.start()

        self.verticalScrollBar().valueChanged.connect(self.on_scroll)

    def on_scroll(self, value):
        # 检查是否滚动到了底部附近
        scroll_bar = self.verticalScrollBar()
        if scroll_bar.maximum() - value < 400:  # 距离底部小于100像素时加载更多
            if not self.search_music_list:
                self.update_music_display = threading.Thread(target=self.load_next_batch, args=())
                self.update_music_display.setDaemon(True)
                self.update_music_display.start()

            else:
                self.update_search_music_display = threading.Thread(target=self.display_search_music, args=())
                self.update_search_music_display.setDaemon(True)
                self.update_search_music_display.start()


    def load_next_batch(self):
        if self.is_loading:
            return

        self.is_loading = True
        conn = sqlite3.connect('data/musiclibrary.db')
        self.SQLiteCursor = conn.cursor()

        id_list = self.get_musiclist(self.id)

        # 计算本次要加载的项目范围
        if self.batch_size:
            start_index = self.loaded_count
            end_index = min(start_index + self.batch_size, len(id_list))
        else:
            start_index = self.loaded_count
            end_index = min(start_index + 30, len(id_list))

        for i in range(start_index, end_index):
            try:
                self.update_music_widget.emit(id_list, i, 1)
            except:
                pass
            time.sleep(0.03)

        conn.close()
        # 更新已加载数量
        self.loaded_count = end_index
        self.is_loading = False

        if self.loaded_count >= len(id_list):
            try:
                self.verticalScrollBar().valueChanged.disconnect(self.on_scroll)
            except:
                pass

    def _handle_update_music_widget(self, id_list, num, t):
        widget = QtWidgets.QWidget(parent=self.scrollAreaWidgetContents)
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

        music_widget = MusicListWidget(self.music_library.get_song_by_id(id_list[num]), num, self.id,
                                       self.music_library, self.play_music_control, self.main,
                                       self.scrollAreaWidgetContents)

        verticalLayout.addWidget(music_widget)
        if t == 1:
            self.verticalLayout_list.addWidget(widget)
            self.list[id_list[num]] = music_widget
        else:
            self.verticalLayout_search_list.addWidget(widget)
            self.search_list[id_list[num]] = music_widget

    def update_order(self):
        order = self.music_library.get_playlist(self.id)['order']

        if order == 0:
            self.pushButton_order.setText('排序')
        elif order == 1:
            self.pushButton_order.setText('时间')
        elif order == 2:
            self.pushButton_order.setText('歌曲')
        elif order == 3:
            self.pushButton_order.setText('歌手')
        elif order == 4:
            self.pushButton_order.setText('专辑')

    def order_music_list(self):
        """在按钮下方显示排序菜单"""
        btn = self.sender()
        self.orderMenu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))

    def update_music_order(self, sortType):
        """排序类型变更的槽函数：打印选中的排序类型"""
        order = self.music_library.get_playlist(self.id)['order']

        if sortType == '默认排序' and order != 0:
            self.music_library.SQLiteCursor.execute(f"UPDATE playlist SET sort_order = ? WHERE list_id = ?",
                                                    (0, self.id))
            self.music_library.update_playlist(self.id)
            self.music_library.conn.commit()
            self.update_page()

        if sortType == '添加时间' and order != 1:
            self.music_library.SQLiteCursor.execute(f"UPDATE playlist SET sort_order = ? WHERE list_id = ?",
                                                    (1, self.id))
            self.music_library.update_playlist(self.id)
            self.music_library.conn.commit()
            self.update_page()

        if sortType == '歌曲名' and order != 2:
            self.music_library.SQLiteCursor.execute(f"UPDATE playlist SET sort_order = ? WHERE list_id = ?",
                                                    (2, self.id))
            self.music_library.update_playlist(self.id)
            self.music_library.conn.commit()
            self.update_page()

        if sortType == '歌手' and order != 3:
            self.music_library.SQLiteCursor.execute(f"UPDATE playlist SET sort_order = ? WHERE list_id = ?",
                                                    (3, self.id))
            self.music_library.update_playlist(self.id)
            self.music_library.conn.commit()
            self.update_page()

        if sortType == '专辑' and order != 4:
            self.music_library.SQLiteCursor.execute(f"UPDATE playlist SET sort_order = ? WHERE list_id = ?",
                                                    (4, self.id))
            self.music_library.update_playlist(self.id)
            self.music_library.conn.commit()
            self.update_page()


        self.update_order()

    def play_music(self):
        list = self.music_library.get_musiclist(self.id)
        if len(list) == 0:
            return
        id = list[0]
        self.music_library.update_play_music(id, self.id)
        self.play_music_control.music_play_order = [id]
        self.play_music_control.update_page(id)

    def search_music(self, text):
        if not self.music_library.get_musiclist(self.id):
            return
        text = text.strip()
        if self.text == text:
            return
        else:
            self.text = text
        if text:
            for i in range(self.verticalLayout_list.count()):
                item = self.verticalLayout_list.itemAt(i)
                widget = item.widget()  # 获取控件
                widget.hide()

            search_music_list = self.music_library.list_search(self.id, text)
            if self.search_music_list != search_music_list:
                self.search_music_list = search_music_list
                self.loaded_count_search = 0
                self.clear_layout(self.verticalLayout_search_list)

                self.update_search_music_display = threading.Thread(target=self.display_search_music, args=())
                self.update_search_music_display.setDaemon(True)
                self.update_search_music_display.start()
                # self.display_search_music()

        else:
            self.search_list = {}
            self.search_music_list = []
            for i in range(self.verticalLayout_list.count()):
                item = self.verticalLayout_list.itemAt(i)
                widget = item.widget()  # 获取控件
                widget.show()

            self.clear_layout(self.verticalLayout_search_list)


    def display_search_music(self):
        if self.is_loading:
            return

        self.is_loading = True

        id_list = self.search_music_list

        # 计算本次要加载的项目范围
        if self.batch_size:
            start_index = self.loaded_count_search
            end_index = min(start_index + 10, len(id_list))
        else:
            start_index = self.loaded_count_search
            end_index = min(start_index + 10, len(id_list))
        for i in range(start_index, end_index):
            try:
                self.update_music_widget.emit(id_list, i, 0)
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


    def clear_layout(self, layout):
        """递归清空布局中的所有内容"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())  # 递归清空嵌套布局

    def load_svg_icon(self, svg_path,width=60,height=60):
        renderer = QtSvg.QSvgRenderer(svg_path)
        pixmap = QtGui.QPixmap(width, height)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)  # 设置透明背景
        painter = QtGui.QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return pixmap

    def get_musiclist(self, list_id):
        self.SQLiteCursor.execute("SELECT * FROM playlist WHERE list_id = ?", (list_id,))
        playlist_data = self.SQLiteCursor.fetchone()

        # 修复2：添加空值检查
        if not playlist_data:
            return []

        order = playlist_data[4]  # sort_order 是第5列

        order_mapping = {
            0: "musiclist.time DESC",
            1: "musiclist.time ASC",
            2: "musiclibrary.name_pinyin ASC",
            3: "musiclibrary.singer_pinyin ASC",
            4: "musiclibrary.album_pinyin ASC"
        }

        order_by = order_mapping.get(order, "musiclist.time DESC")  # 默认排序

        query_musiclist = f"""
            SELECT musiclist.*, musiclibrary.* 
            FROM musiclist
            JOIN musiclibrary ON musiclist.id = musiclibrary.id 
            WHERE musiclist.list_id = ? 
            ORDER BY {order_by}
        """

        self.SQLiteCursor.execute(query_musiclist, (list_id,))
        result = self.SQLiteCursor.fetchall()
        data = []
        for i in result:
            data.append(i[1])
        return data

