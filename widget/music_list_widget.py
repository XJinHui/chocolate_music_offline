from PyQt6 import QtCore, QtGui, QtWidgets, QtSvg
from PyQt6.QtGui import QContextMenuEvent
from .hover_click_filter import HoverClickFilter
from .round_image_label import RoundImageLabel
from .music_setting_menu import MusicSettingMenu
from .add_music_dialog import AddMusicDialog

class MusicListWidget(QtWidgets.QPushButton):
    def __init__(self, data, num, list_id, music_library, play_music_control, main, parent=None):
        super().__init__(parent)
        self.data = data
        self.music_library = music_library
        self.play_music_control = play_music_control
        self.main = main
        self.num = num
        self.list_id = list_id
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Form")
        self.setMouseTracking(True)
        # self.resize(708, 50)
        self.setMinimumSize(QtCore.QSize(0, 50))
        self.setMaximumSize(QtCore.QSize(16777215, 50))
        self.setStyleSheet("background-color: transparent;")
        # self.setStyleSheet("background-color: rgb(255, 255, 255);\n"
        #         "border-radius: 10px;")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(0, 5, 0, 5)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.widget_4 = QtWidgets.QWidget(parent=self)
        self.widget_4.setMinimumSize(QtCore.QSize(240, 0))
        self.widget_4.setMaximumSize(QtCore.QSize(200, 16777215))
        self.widget_4.setObjectName("widget_4")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.widget_4)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setSpacing(10)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label = QtWidgets.QLabel(parent=self.widget_4)
        self.label.setMinimumSize(QtCore.QSize(30, 30))
        self.label.setMaximumSize(QtCore.QSize(30, 30))
        self.label.setObjectName("label")
        self.horizontalLayout_5.addWidget(self.label)

        # self.label_2 = QtWidgets.QLabel(parent=self.widget_4)
        self.label_2 = RoundImageLabel(radius=4)
        self.label_2.setMinimumSize(QtCore.QSize(40, 40))
        self.label_2.setMaximumSize(QtCore.QSize(40, 40))
        # self.label_2.setText("")
        # self.label_2.setPixmap(QtGui.QPixmap(self.data['photo']))
        success = self.label_2.setImageSmart(self.data['photo'])
        if not success:
            self.label_2.setPixmap(QtGui.QPixmap("media/app_photo.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")

        self.horizontalLayout_5.addWidget(self.label_2)
        self.label_3 = QtWidgets.QLabel(parent=self.widget_4)
        self.label_3.setMinimumSize(QtCore.QSize(150, 0))
        self.label_3.setMaximumSize(QtCore.QSize(150, 16777215))
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_5.addWidget(self.label_3)
        self.horizontalLayout.addWidget(self.widget_4)
        self.widget_2 = QtWidgets.QWidget(parent=self)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(5)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_4 = QtWidgets.QLabel(parent=self.widget_2)
        self.label_4.setMinimumSize(QtCore.QSize(130, 0))
        self.label_4.setMaximumSize(QtCore.QSize(130, 16777215))
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.label_7 = QtWidgets.QLabel(parent=self.widget_2)
        self.label_7.setMinimumSize(QtCore.QSize(130, 0))
        self.label_7.setMaximumSize(QtCore.QSize(130, 16777215))
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_3.addWidget(self.label_7)

        self.label_heart = QtWidgets.QLabel(parent=self.widget_2)
        self.label_heart.setMinimumSize(QtCore.QSize(20, 20))
        self.label_heart.setMaximumSize(QtCore.QSize(20, 20))
        self.label_heart.setText("")
        self.label_heart_white_photo = self.load_svg_icon("media/heart.svg")
        self.label_heart_red_photo = self.load_svg_icon("media/heart_red_fill.svg")
        if self.data['like']:
            self.label_heart.setPixmap(self.label_heart_red_photo)
        else:
            self.label_heart.setPixmap(self.label_heart_white_photo)
        self.label_heart.setScaledContents(True)
        self.label_heart.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.label_heart.setObjectName("label_heart")
        self.label_heart_filter = HoverClickFilter()
        self.label_heart.installEventFilter(self.label_heart_filter)
        self.label_heart_filter.clicked.connect(self.update_heart)
        self.horizontalLayout_3.addWidget(self.label_heart)

        self.label_9 = QtWidgets.QLabel(parent=self.widget_2)
        self.label_9.setMinimumSize(QtCore.QSize(35, 0))
        self.label_9.setMaximumSize(QtCore.QSize(35, 16777215))
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_3.addWidget(self.label_9)
        self.horizontalLayout.addWidget(self.widget_2)

        self.setting_menu = MusicSettingMenu(self.list_id, parent=self)
        self.setting_menu.sortChanged.connect(self.update_music_list)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        # self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    def retranslateUi(self):
        duration_seconds = int(self.data["time"]/100)
        minutes, seconds = divmod(duration_seconds, 60)
        if minutes < 10:
            minutes = f"0{minutes}"
        time = f"{minutes}:{seconds:02d}"

        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", f"<html><head/><body><p align=\"center\"><span style=\" font-size:10pt; color:#787878;\">{self.num+1}</span></p></body></html>"))
        self.label_3.setText(_translate("Form", f"<html><head/><body><p><span style=\" font-size:10pt;\">{self.data['name']}</span></p></body></html>"))
        self.label_4.setText(_translate("Form", f"<html><head/><body><p><span style=\" font-size:10pt; color:#787878;\">{self.data['singer']}</span></p></body></html>"))
        self.label_7.setText(_translate("Form", f"<html><head/><body><p><span style=\" font-size:10pt; color:#787878;\">{self.data['album']}</span></p></body></html>"))
        self.label_9.setText(_translate("Form", f"<html><head/><body><p><span style=\" font-size:10pt; color:#787878;\">{time}</span></p></body></html>"))

    # def update_photo(self):
    #     success = self.label_2.setImageSmart(self.data['photo'])
    #     if not success:
    #         self.label_2.setPixmap(QtGui.QPixmap("media/app_photo.png"))

    def update_heart(self):
        if self.data['like']:
            self.label_heart.setPixmap(self.label_heart_white_photo)
        else:
            self.label_heart.setPixmap(self.label_heart_red_photo)
        self.data['like'] = not self.data['like']

        self.music_library.update_like(self.data['id'], self.data['like'])

        if self.music_library.setting['id'] == self.data['id']:
            self.music_library.setting['like'] = self.data['like']
            if self.music_library.setting['like']:
                self.main.label_collection.setPixmap(self.main.label_collection_red_photo)
            else:
                self.main.label_collection.setPixmap(self.main.label_collection_white_photo)

        self.music_library.is_or_no_like(self.data['id'])

        if self.main.row == -1:
            return

        if self.main.scrollArea_music_list.id == 0:
            self.main.scrollArea_music_list.update_page()

    def update_music_list(self, sortType):
        if sortType == '添加到歌单':
            dialog = AddMusicDialog(self.music_library)
            # dialog.playlist_selected.connect(self.on_playlist_selected)
            if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                playlist_id = dialog._result
                if playlist_id == self.list_id:
                    print("不能添加到自身")
                else:
                    self.music_library.add_music(self.data['id'], playlist_id)
                if playlist_id == 0:
                    self.label_heart.setPixmap(self.label_heart_red_photo)
                    if self.music_library.setting['id'] == self.data['id']:
                        self.music_library.setting['like'] = True
                        self.main.label_collection.setPixmap(self.main.label_collection_red_photo)
                        self.music_library.update()
                self.main.update_playlist_list()

        elif sortType == '从歌单中删除':
            if self.list_id == 0:
                self.data['like'] = False
                self.music_library.update_like(self.data['id'], self.data['like'])
                if self.music_library.setting['id'] == self.data['id']:
                    self.music_library.setting['like'] = self.data['like']
                    if self.music_library.setting['like']:
                        self.main.label_collection.setPixmap(self.main.label_collection_red_photo)
                    else:
                        self.main.label_collection.setPixmap(self.main.label_collection_white_photo)
                self.music_library.is_or_no_like(self.data['id'])
            else:
                self.music_library.delete_music(self.data['id'], self.list_id)
            # if self.main.scrollArea_music_list.id == 0:
            self.main.scrollArea_music_list.update_page()
            self.main.update_playlist_list()

    def load_svg_icon(self, svg_path,width=60,height=60):
        renderer = QtSvg.QSvgRenderer(svg_path)
        pixmap = QtGui.QPixmap(width, height)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)  # 设置透明背景
        painter = QtGui.QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return pixmap

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.on_clicked()

    def contextMenuEvent(self, event: QContextMenuEvent):
        # 在鼠标右键位置显示菜单
        self.setting_menu.exec(event.globalPos())

    def on_clicked(self):
        self.music_library.update_play_music(self.data['id'], self.list_id)
        self.play_music_control.music_play_order = [self.data['id']]
        self.main.update_play_music()
        self.play_music_control.play_music()
        # 你可以在这里调用 main 或其他对象的方法
        # self.main.play_music(self.data)  # 示例

