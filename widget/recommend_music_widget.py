from PyQt6 import QtCore, QtGui, QtWidgets, QtSvg
from PyQt6.QtGui import QContextMenuEvent, QEnterEvent
from .round_image_label import RoundImageLabel
from .hover_click_filter import HoverClickFilter
from .music_setting_menu import MusicSettingMenu
from .add_music_dialog import AddMusicDialog


class RecommendMusicWidget(QtWidgets.QWidget):
    def __init__(self, data, music_library, play_music_control, main, parent=None):
        super().__init__(parent)
        # self.data = {'name': '魔杰座', 'signer': '周杰伦', 'photo': 'album/魔杰座-周杰伦-2008.jpeg', 'like': False}
        self.data = data
        self.music_library = music_library
        self.play_music_control = play_music_control
        self.main = main
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Form")
        self.resize(400, 80)
        self.setStyleSheet("background-color: transparent;")
        self.setMinimumSize(QtCore.QSize(300, 80))
        self.setMaximumSize(QtCore.QSize(16777215, 80))
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(10, 10, 20, 10)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.label_photo = RoundImageLabel(radius=6)
        self.label_photo.setMinimumSize(QtCore.QSize(60, 60))
        self.label_photo.setMaximumSize(QtCore.QSize(60, 60))

        success = self.label_photo.setImageSmart(self.data['photo'])
        if not success:
            self.label_photo.setPixmap(QtGui.QPixmap("media/app_photo.png"))

        self.label_photo.setScaledContents(True)
        self.label_photo.setObjectName("label_play_music_photo")

        self.horizontalLayout.addWidget(self.label_photo)
        self.widget_music_message = QtWidgets.QWidget(parent=self)
        self.widget_music_message.setObjectName("widget_music_message")
        self.widget_music_message.setStyleSheet("background-color: transparent;")
        self.verticalLayout_17 = QtWidgets.QVBoxLayout(self.widget_music_message)
        self.verticalLayout_17.setObjectName("verticalLayout_17")

        self.label_music_name = QtWidgets.QLabel(parent=self.widget_music_message)
        self.label_music_name.setMinimumSize(QtCore.QSize(160, 0))
        self.label_music_name.setMaximumSize(QtCore.QSize(160, 16777215))
        self.label_music_name.setObjectName("label_music_name")
        self.verticalLayout_17.addWidget(self.label_music_name)

        self.label_music_signer = QtWidgets.QLabel(parent=self.widget_music_message)
        self.label_music_signer.setMinimumSize(QtCore.QSize(160, 0))
        self.label_music_signer.setMaximumSize(QtCore.QSize(160, 16777215))
        self.label_music_signer.setObjectName("label_music_signer")
        self.verticalLayout_17.addWidget(self.label_music_signer)
        self.horizontalLayout.addWidget(self.widget_music_message)

        self.label_heart = QtWidgets.QLabel(parent=self)
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
        self.label_heart.hide()
        self.horizontalLayout.addWidget(self.label_heart)

        self.setting_menu = MusicSettingMenu(-1, parent=self)
        self.setting_menu.sortChanged.connect(self.update_music_list)

        self.retranslateUi()
        # QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, ):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "Form"))
        self.label_music_name.setText(_translate("Form", f"<html><head/><body><p><span style=\" font-size:10pt;\">{self.data['name']}</span></p></body></html>"))
        self.label_music_signer.setText(_translate("Form", f"<html><head/><body><p><span style=\" font-size:10pt; color:#787878;\">{self.data['singer']}</span></p></body></html>"))

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

    def update_music_list(self, sortType):
        # if sortType == '添加到歌单':
        dialog = AddMusicDialog(self.music_library)
        # dialog.playlist_selected.connect(self.on_playlist_selected)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            playlist_id = dialog._result
            self.music_library.add_music(self.data['id'], playlist_id)
            if playlist_id == 0:
                self.label_heart.setPixmap(self.label_heart_red_photo)
                if self.music_library.setting['id'] == self.data['id']:
                    self.music_library.setting['like'] = True
                    self.main.label_collection.setPixmap(self.main.label_collection_red_photo)
                    self.music_library.update()
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
        # 显示菜单前，强制显示label_heart
        self.label_heart.show()
        # 记录当前是否需要隐藏（避免菜单关闭后状态异常）
        self._should_hide_heart = False
        # 显示菜单，并等待菜单关闭
        self.setting_menu.exec(event.globalPos())
        # 菜单关闭后，检查鼠标是否仍在控件上，不在则隐藏
        if not self.underMouse():
            self.label_heart.hide()

    def on_clicked(self):
        self.music_library.update_play_music(self.data['id'], -1)
        self.play_music_control.music_play_order = [self.data['id']]
        self.main.update_play_music()
        self.play_music_control.play_music()
        # 你可以在这里调用 main 或其他对象的方法
        # self.main.play_music(self.data)  # 示例

    def enterEvent(self, event: QEnterEvent):
        self.on_mouse_hover()  # 调用悬浮处理函数
        super().enterEvent(event)  # 保留父类事件处理

    # 新增：鼠标离开时触发
    def leaveEvent(self, event: QtCore.QEvent):
        if not self.setting_menu.isVisible():
            self.on_mouse_leave()
        super().leaveEvent(event)  # 保留父类事件处理

    # 自定义：鼠标悬浮时的操作（示例：改变背景色）
    def on_mouse_hover(self):
        self.label_heart.show()
        # self.setStyleSheet("background-color: rgba(255, 255, 255, 0.1);")  # 半透明白色背景
        # 可添加其他逻辑，如显示提示信息等

    # 自定义：鼠标离开时的操作（示例：恢复原样式）
    def on_mouse_leave(self):
        self.label_heart.hide()
        # self.setStyleSheet("background-color: transparent;")  # 恢复透明背景
        # 可添加其他逻辑，如隐藏提示信息等