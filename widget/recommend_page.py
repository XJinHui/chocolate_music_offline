import random
import threading
import time
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import pyqtSignal
from .album_widget import AlbumWidget
from .author_widget import AuthorWidget
from .recommend_music_widget import RecommendMusicWidget
#
# from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
# from PyQt6.QtCore import Qt


class RecommendScrollArea(QtWidgets.QScrollArea):
    display_album = pyqtSignal(int)
    display_author = pyqtSignal(int)
    display_music = pyqtSignal(int)

    def __init__(self, music_library, play_music_control, main, parent=None):
        super().__init__(parent)
        self.music_library = music_library
        self.play_music_control = play_music_control
        # self.data = data
        self.main = main
        self.id = -1

        self.display_album.connect(self._handle_display_album)
        self.display_author.connect(self._handle_display_author)
        self.display_music.connect(self._handle_display_music)

        self.list = {}

        if not self.main.recommend_list:
            self.random_recommend_list()
        else:
            self.album_num = len(self.main.recommend_list['album'])
            self.singer_num = len(self.main.recommend_list['singer'])
            self.music_num = len(self.main.recommend_list['music'])

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
        self.setObjectName("scrollArea")

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, -481, 735, 900))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        self.verticalLayout_main = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_main.setContentsMargins(20, 10, 20, 0)
        self.verticalLayout_main.setSpacing(5)
        self.verticalLayout_main.setObjectName("verticalLayout_main")

        self.label_album = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents)
        self.label_album.setMinimumSize(QtCore.QSize(0, 40))
        self.label_album.setMaximumSize(QtCore.QSize(16777215, 40))
        self.label_album.setObjectName("label_album")
        self.verticalLayout_main.addWidget(self.label_album)

        self.widget_album = QtWidgets.QWidget(parent=self.scrollAreaWidgetContents)
        self.widget_album.setMinimumSize(QtCore.QSize(0, 180))
        self.widget_album.setMaximumSize(QtCore.QSize(16777215, 180))
        self.widget_album.setObjectName("widget_album")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget_album)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.verticalLayout_main.addWidget(self.widget_album)

        spacerItem7 = QtWidgets.QSpacerItem(20, 15, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        self.verticalLayout_main.addItem(spacerItem7)
        self.label_author = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents)
        self.label_author.setMinimumSize(QtCore.QSize(0, 40))
        self.label_author.setMaximumSize(QtCore.QSize(16777215, 40))
        self.label_author.setObjectName("label_author")
        self.verticalLayout_main.addWidget(self.label_author)
        self.widget_author = QtWidgets.QWidget(parent=self.scrollAreaWidgetContents)
        self.widget_author.setMinimumSize(QtCore.QSize(0, 105))
        self.widget_author.setMaximumSize(QtCore.QSize(16777215, 105))
        self.widget_author.setObjectName("widget_author")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget_author)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.verticalLayout_main.addWidget(self.widget_author)

        spacerItem17 = QtWidgets.QSpacerItem(20, 15, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        self.verticalLayout_main.addItem(spacerItem17)
        self.label_music = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents)
        self.label_music.setMinimumSize(QtCore.QSize(0, 40))
        self.label_music.setMaximumSize(QtCore.QSize(16777215, 40))
        self.label_music.setObjectName("label_music")
        self.verticalLayout_main.addWidget(self.label_music)

        self.widget_music = QtWidgets.QWidget(parent=self.scrollAreaWidgetContents)
        self.widget_music.setObjectName("widget_music")
        self.verticalLayout_16 = QtWidgets.QVBoxLayout(self.widget_music)
        self.verticalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_16.setSpacing(5)
        self.verticalLayout_16.setObjectName("verticalLayout_16")

        self.verticalLayout_main.addWidget(self.widget_music)
        self.setWidget(self.scrollAreaWidgetContents)
        # self.verticalLayout_10.addWidget(self.scrollArea)

        # 显示推荐专辑
        self.display_recommend_album_threading = threading.Thread(target=self.display_recommend_album, args=())
        self.display_recommend_album_threading.setDaemon(True)
        self.display_recommend_album_threading.start()
        # self.self.display_recommend_album()

        #显示推荐歌手
        self.display_recommend_author_threading = threading.Thread(target=self.display_recommend_author, args=())
        self.display_recommend_author_threading.setDaemon(True)
        self.display_recommend_author_threading.start()
        # self.display_recommend_author()

        #显示推荐歌曲
        self.display_recommend_music_threading = threading.Thread(target=self.display_recommend_music, args=())
        self.display_recommend_music_threading.setDaemon(True)
        self.display_recommend_music_threading.start()
        # self.display_recommend_music()

        self.retranslateUi()
        # QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        # Form.setWindowTitle(_translate("Form", "Form"))
        self.label_album.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:14pt;\">推荐专辑</span></p></body></html>"))

        self.label_author.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:14pt;\">推荐歌手</span></p></body></html>"))

        self.label_music.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:14pt;\">推荐歌曲</span></p></body></html>"))

    def display_recommend_album(self):
        for i in range(self.album_num):
            try:
                self.display_album.emit(i)
            except:
                pass
            time.sleep(0.05)

    def _handle_display_album(self, num):
        data = self.main.recommend_list['album'][num]
        widget = AlbumWidget(data, self.music_library, self.play_music_control, self.main, size=150)
        self.horizontalLayout.addWidget(widget)
        if num < 3 or num < self.album_num - 1:
            spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                               QtWidgets.QSizePolicy.Policy.Minimum)
            self.horizontalLayout.addItem(spacerItem)


    def display_recommend_author(self):
        for i in range(self.singer_num):
            try:
                self.display_author.emit(i)
            except:
                pass
            time.sleep(0.05)

    def _handle_display_author(self, num):
        data = self.main.recommend_list['singer'][num]
        widget = AuthorWidget(data, self.music_library, self.play_music_control, self.main, size=80)
        self.horizontalLayout_2.addWidget(widget)
        if num < 4 or num < self.singer_num - 1:
            spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                               QtWidgets.QSizePolicy.Policy.Minimum)
            self.horizontalLayout_2.addItem(spacerItem)

    def display_recommend_music(self):
        self.list = {}
        if self.music_num % 2 == 0:
            num = int(self.music_num / 2)
        else:
            num = int(self.music_num / 2) + 1
        for i in range(num):
            try:
                self.display_music.emit(i)
            except:
                pass
            time.sleep(0.05)

    def _handle_display_music(self, num):
        data_1 = self.main.recommend_list['music'][num * 2]

        widget_framework = QtWidgets.QWidget(parent=self.widget_music)
        widget_framework.setObjectName("widget_framework")
        horizontalLayout_5 = QtWidgets.QHBoxLayout(widget_framework)
        horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        horizontalLayout_5.setSpacing(20)
        horizontalLayout_5.setObjectName("horizontalLayout_5")

        widget_1 = QtWidgets.QWidget(parent=widget_framework)
        widget_1.setStyleSheet("""
                                    QWidget {
                                        background-color: transparent;
                                        border-radius: 10px;
                                    }
                                    QWidget:hover {
                                        background-color: rgb(230, 230, 230);
                                    }
                                """)
        verticalLayout_1 = QtWidgets.QVBoxLayout(widget_1)
        verticalLayout_1.setObjectName("verticalLayout")
        verticalLayout_1.setContentsMargins(0, 0, 0, 0)
        verticalLayout_1.setSpacing(0)

        widget_music_1 = RecommendMusicWidget(data_1, self.music_library, self.play_music_control, self.main)
        verticalLayout_1.addWidget(widget_music_1)
        horizontalLayout_5.addWidget(widget_1)

        self.list[data_1['id']] = widget_music_1

        if (num * 2 + 1) <= self.music_num - 1:
            data_2 = self.main.recommend_list['music'][num * 2 + 1]

            widget_2 = QtWidgets.QWidget(parent=widget_framework)
            widget_2.setStyleSheet("""
                                                QWidget {
                                                    background-color: transparent;
                                                    border-radius: 10px;
                                                }
                                                QWidget:hover {
                                                    background-color: rgb(230, 230, 230);
                                                }
                                            """)
            verticalLayout_2 = QtWidgets.QVBoxLayout(widget_2)
            verticalLayout_2.setObjectName("verticalLayout")
            verticalLayout_2.setContentsMargins(0, 0, 0, 0)
            verticalLayout_2.setSpacing(0)
            widget_music_2 = RecommendMusicWidget(data_2, self.music_library, self.play_music_control, self.main)
            verticalLayout_2.addWidget(widget_music_2)
            horizontalLayout_5.addWidget(widget_2)

            self.list[data_2['id']] = widget_music_2

        self.verticalLayout_16.addWidget(widget_framework)

    def random_recommend_list(self):
        album_list = []
        singer_list = []
        music_list = []

        self.music_library.SQLiteCursor.execute("SELECT COUNT(*) FROM musiclibrary")
        song_count = self.music_library.SQLiteCursor.fetchone()[0]

        self.music_library.SQLiteCursor.execute("SELECT COUNT(DISTINCT album) FROM musiclibrary WHERE album IS NOT NULL AND album != ''")
        album_count = self.music_library.SQLiteCursor.fetchone()[0]

        # 歌手数（去重）
        self.music_library.SQLiteCursor.execute("SELECT COUNT(DISTINCT singer) FROM musiclibrary WHERE singer IS NOT NULL AND singer != ''")
        singer_count = self.music_library.SQLiteCursor.fetchone()[0]

        self.album_num = min(4, album_count)
        self.singer_num = min(5, singer_count)
        self.music_num = min(20, song_count)

        albums = random.sample(self.music_library.get_all_albums(), self.album_num)
        singers = random.sample(self.music_library.get_all_singers(), self.singer_num)
        music_list = random.sample(self.music_library.get_all_music(), self.music_num)

        for i in albums:
            album = self.music_library.get_songs_by_album(i)
            album_data = {'album': i, 'albumartist': album[0]['albumartist'],
                          'photo': album[0]['photo'], 'num': len(album), 'album_data': album[0]['album_data']}
            album_list.append(album_data)

        for i in singers:
            singer = self.music_library.get_songs_by_singer(i)
            singer_data = {'singer': singer[0]['singer'], 'photo': singer[0]['photo'], 'num': len(singer)}
            singer_list.append(singer_data)

        # for i in range(self.album_num):
        #     while True:
        #         l = self.music_library.music_indexes['by_album']
        #         random_album = random.choice(list(l.keys()))
        #         if random_album == '未知专辑':
        #             continue
        #         album = self.music_library.get_songs_by_album(random_album)
        #         album_data = {'album': random_album, 'albumartist': album[0]['albumartist'],
        #                       'photo': album[0]['photo'], 'num': len(album), 'album_data': album[0]['album_data']}
        #         if album_data not in album_list:
        #             album_list.append(album_data)
        #             break
        #
        # for i in range(self.singer_num):
        #     while True:
        #         l = self.music_library.music_indexes['by_singer']
        #         random_singer = random.choice(list(l.keys()))
        #         if random_singer == '未知歌手':
        #             continue
        #         singer = self.music_library.get_songs_by_singer(random_singer)
        #         singer_data = {'singer': singer[0]['singer'], 'photo': singer[0]['photo'], 'num': len(singer)}
        #         if singer_data not in album_list:
        #             singer_list.append(singer_data)
        #             break
        #
        # for i in range(self.music_num):
        #     while True:
        #         random_singer = random.choice(self.music_library.musiclibrary)
        #         if random_singer not in music_list:
        #             music_list.append(random_singer)
        #             break

        self.main.recommend_list = {'album': album_list, 'singer': singer_list, 'music': music_list}