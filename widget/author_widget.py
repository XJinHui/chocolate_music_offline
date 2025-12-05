import time
from PyQt6 import QtCore, QtGui, QtWidgets
from .hover_click_filter import HoverClickFilter
from .round_image_label import RoundImageLabel
from .music_list_page import MusicListScrollArea

class AuthorWidget(QtWidgets.QWidget):
    def __init__(self, data, music_library, play_music_control, main, size = 80, parent=None):
        super().__init__(parent)
        self.data = data
        # data = {'singer': 'singer', 'photo': 'photo', 'num': 'num'}
        #self.list = list
        self.music_library = music_library
        self.play_music_control = play_music_control
        self.main = main
        self.size = size
        self.setupUi()

    def setupUi(self):
        self.setObjectName("AuthorWidget")
        self.resize(self.size, self.size + 25)
        self.setMinimumSize(QtCore.QSize(self.size, self.size + 25))
        self.setMaximumSize(QtCore.QSize(self.size, self.size + 25))
        self.setStyleSheet("background-color: transparent;")
        # self.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.author_photo = RoundImageLabel(self.size / 2)
        self.author_photo.setMinimumSize(QtCore.QSize(self.size, self.size))
        self.author_photo.setMaximumSize(QtCore.QSize(self.size, self.size))
        success = self.author_photo.setImageSmart(self.data['photo'])
        if not success:
            self.author_photo.setPixmap(QtGui.QPixmap("media/app_photo.png"))
        self.author_photo.setScaledContents(True)
        self.author_photo.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.author_photo_filter = HoverClickFilter()
        self.author_photo.installEventFilter(self.author_photo_filter)
        self.author_photo_filter.clicked.connect(self.display_author_list)
        self.verticalLayout.addWidget(self.author_photo)

        self.spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                                QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(self.spacerItem)

        self.author_name = QtWidgets.QLabel(self)
        self.author_name.setStyleSheet("color: rgb(0, 0, 0); font-size: 14px;")
        self.author_name.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.author_name.setText(self.data['singer'])
        self.verticalLayout.addWidget(self.author_name)

    def display_author_list(self):
        self.main.listWidget.clearSelection()
        self.main.listWidget_2.clearSelection()
        self.main.row = 4

        data = self.music_library.get_songs_by_singer(self.data['singer'])
        datas = []
        for i in data:
            datas.append(i['id'])

        delete_musiclist_sql = "DELETE FROM musiclist WHERE list_id = ?"
        self.music_library.SQLiteCursor.execute(delete_musiclist_sql, (2,))

        for i in datas:
            self.music_library.SQLiteCursor.execute(self.music_library.insert_musiclist_sql, (2, i, time.time()))
        # self.music_library.musiclist['2'] = datas

        self.music_library.SQLiteCursor.execute(f"UPDATE playlist SET name = ? WHERE list_id = ?",
                                                (self.data['singer'], 2))
        self.music_library.update_playlist(2)
        # self.music_library.playlist['2']['num'] = len(datas)
        # self.music_library.playlist['2']['name'] = self.data['singer']
        # self.music_library.playlist['2']['photo'] = self.data['photo']
        # self.music_library.playlist['2']['order'] = 0
        # self.music_library.update_music_order(2)

        self.music_library.update()

        self.main.clear_layout(self.main.verticalLayout_12)
        self.main.scrollArea_music_list = MusicListScrollArea(self.music_library, self.play_music_control, 2, self.main)
        self.main.verticalLayout_12.addWidget(self.main.scrollArea_music_list)