import time
from PyQt6 import QtCore, QtGui, QtWidgets
from .hover_click_filter import HoverClickFilter
from .round_image_label import RoundImageLabel
from .music_list_page import MusicListScrollArea

class AlbumWidget(QtWidgets.QWidget):
    def __init__(self, data, music_library, play_music_control, main, size = 150, parent=None):
        super().__init__(parent)
        self.data = data
        #data = {'album': 'album', 'albumartist': 'albumartist', 'photo': 'photo', 'num': 'num'}
        #self.list = list
        self.music_library = music_library
        self.play_music_control = play_music_control
        self.main = main
        self.size = size
        self.setupUi()

    def setupUi(self):
        self.setObjectName("AlbumWidget")
        self.resize(self.size, self.size + 30)
        self.setMinimumSize(QtCore.QSize(self.size, self.size + 30))
        self.setMaximumSize(QtCore.QSize(self.size, self.size + 30))
        self.setStyleSheet("background-color: transparent;")
        # self.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.album_photo = RoundImageLabel(self.size / 10)
        self.album_photo.setMinimumSize(QtCore.QSize(self.size, self.size))
        self.album_photo.setMaximumSize(QtCore.QSize(self.size, self.size))
        success = self.album_photo.setImageSmart(self.data['photo'])
        if not success:
            self.album_photo.setPixmap(QtGui.QPixmap("media/app_photo.png"))
        self.album_photo.setScaledContents(True)
        self.album_photo.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.album_photo_filter = HoverClickFilter()
        self.album_photo.installEventFilter(self.album_photo_filter)
        self.album_photo_filter.clicked.connect(self.display_album_list)
        self.verticalLayout.addWidget(self.album_photo)

        self.spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                                            QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(self.spacerItem)

        self.album_name = QtWidgets.QLabel(self)
        self.album_name.setStyleSheet("color: rgb(0, 0, 0); font-size: 14px;")
        # self.album_name.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.album_name.setText(self.data['album'])
        self.verticalLayout.addWidget(self.album_name)

    def display_album_list(self):
        self.main.listWidget.clearSelection()
        self.main.listWidget_2.clearSelection()
        self.main.row = 5

        data = self.music_library.get_songs_by_album(self.data['album'])
        datas = []

        for i in data:
            if i['albumartist'] == self.data['albumartist'] and i['album_data'] == self.data['album_data']:
                datas.append(i['id'])

        delete_musiclist_sql = "DELETE FROM musiclist WHERE list_id = ?"
        self.music_library.SQLiteCursor.execute(delete_musiclist_sql, (1,))

        for i in datas:
            self.music_library.SQLiteCursor.execute(self.music_library.insert_musiclist_sql, (1, i, time.time()))
        # self.music_library.musiclist['1'] = datas

        self.music_library.SQLiteCursor.execute(f"UPDATE playlist SET name = ? WHERE list_id = ?", (self.data['album'], 1))
        self.music_library.update_playlist(1)
        # self.music_library.playlist['1']['num'] = len(datas)
        # self.music_library.playlist['1']['name'] = self.data['album']
        # self.music_library.playlist['1']['photo'] = self.data['photo']
        # self.music_library.playlist['1']['order'] = 0
        # self.music_library.update_music_order(1)

        self.music_library.update()

        self.main.clear_layout(self.main.verticalLayout_12)
        self.main.scrollArea_music_list = MusicListScrollArea(self.music_library, self.play_music_control, 1, self.main)
        self.main.verticalLayout_12.addWidget(self.main.scrollArea_music_list)