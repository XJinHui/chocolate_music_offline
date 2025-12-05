import time
import threading
from PyQt6 import QtCore, QtGui, QtWidgets, QtSvg
from PyQt6.QtCore import pyqtSignal
from .hover_click_filter import HoverClickFilter
from .round_image_label import RoundImageLabel


class LyricsPageWidget(QtWidgets.QWidget):

    update_lyrics_color = pyqtSignal(QtWidgets.QLabel, str, int)
    update_lyrics_positioning = pyqtSignal(int)

    def __init__(self, music_library, play_music_control, main, parent=None):
        super().__init__(parent)
        self.music_library = music_library
        self.play_music_control = play_music_control
        self.main = main
        self.lyrics_list = {}
        self.setupUi()

        # 连接信号
        self.update_lyrics_color.connect(self._handle_update_lyrics_color)
        self.update_lyrics_positioning.connect(self._handle_update_lyrics_positioning)

        self.update_lyrics_threading = threading.Thread(target=self.update_lyrics, args=())
        self.update_lyrics_threading.setDaemon(True)
        self.update_lyrics_threading.start()


    def setupUi(self):
        self.setObjectName("lyrcs_page")
        self.resize(900, 550)
        self.setMinimumSize(QtCore.QSize(900, 550))

        self.verticalLayout_main = QtWidgets.QVBoxLayout(self)
        self.verticalLayout_main.setContentsMargins(7, 7, 7, 7)
        self.verticalLayout_main.setSpacing(0)

        self.widget_top = QtWidgets.QWidget(parent=self)
        self.horizontalLayout_top = QtWidgets.QHBoxLayout(self.widget_top)
        self.horizontalLayout_top.setContentsMargins(10, 0, 0, 0)
        self.horizontalLayout_top.setSpacing(0)

        self.label_close_lyrics = QtWidgets.QLabel(parent=self.widget_top)
        self.label_close_lyrics.setMinimumSize(QtCore.QSize(30, 30))
        self.label_close_lyrics.setMaximumSize(QtCore.QSize(30, 30))
        # self.label_close_lyrics.setStyleSheet("background-color: rgb(246, 246, 246);\n"
        #                              "border-radius: 15px;")
        self.label_close_lyrics.setText("")
        self.label_close_lyrics.setPixmap(self.load_svg_icon("media/chevron_down.svg"))
        self.label_close_lyrics.setScaledContents(True)
        self.label_close_lyrics.setObjectName("label_min")
        self.label_close_lyrics_filter = HoverClickFilter()
        self.label_close_lyrics.installEventFilter(self.label_close_lyrics_filter)
        self.label_close_lyrics_filter.clicked.connect(self.main.display_lyrics_page)
        self.horizontalLayout_top.addWidget(self.label_close_lyrics)

        spacerItem_top = QtWidgets.QSpacerItem(20, 100, QtWidgets.QSizePolicy.Policy.Expanding,
                                               QtWidgets.QSizePolicy.Policy.Maximum)
        self.horizontalLayout_top.addItem(spacerItem_top)

        self.widget_operation = QtWidgets.QWidget(parent=self.widget_top)
        self.widget_operation.setMinimumSize(QtCore.QSize(100, 30))
        self.widget_operation.setMaximumSize(QtCore.QSize(100, 30))
        self.widget_operation.setStyleSheet("")
        self.widget_operation.setObjectName("widget_top")
        self.verticalLayout_operation = QtWidgets.QVBoxLayout(self.widget_operation)
        self.verticalLayout_operation.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_operation.setSpacing(0)
        self.verticalLayout_operation.setObjectName("verticalLayout_operation")

        self.horizontalLayout_operation = QtWidgets.QHBoxLayout()
        self.horizontalLayout_operation.setObjectName("horizontalLayout_operation")

        self.label_min = QtWidgets.QLabel(parent=self.widget_operation)
        self.label_min.setMinimumSize(QtCore.QSize(30, 30))
        self.label_min.setMaximumSize(QtCore.QSize(30, 30))
        self.label_min.setStyleSheet("background-color: rgb(246, 246, 246);\n"
                                     "border-radius: 15px;")
        self.label_min.setText("")
        self.label_min.setPixmap(self.load_svg_icon("media/min.svg"))
        self.label_min.setScaledContents(True)
        self.label_min.setObjectName("label_min")
        self.label_min_filter = HoverClickFilter()
        self.label_min.installEventFilter(self.label_min_filter)
        self.label_min_filter.hovered.connect(lambda: self.label_min.setStyleSheet(
            "background-color: rgb(220, 220, 220);\nborder-radius: 15px;"))
        self.label_min_filter.left.connect(lambda: self.label_min.setStyleSheet(
            "background-color: rgb(246, 246, 246);\nborder-radius: 15px;"))
        self.horizontalLayout_operation.addWidget(self.label_min)

        self.label_max_shrink = QtWidgets.QLabel(parent=self.widget_operation)
        self.label_max_shrink.setMinimumSize(QtCore.QSize(30, 30))
        self.label_max_shrink.setMaximumSize(QtCore.QSize(30, 30))
        self.label_max_shrink.setStyleSheet("background-color: rgb(245, 245, 245);\n"
                                            "border-radius: 15px;")
        self.label_max_shrink.setText("")
        self.label_shrink_to_max_photo = self.load_svg_icon("media/max.svg")
        self.label_max_to_shrink_photo = self.load_svg_icon("media/shrink.svg")
        self.label_max_shrink.setPixmap(self.label_shrink_to_max_photo)
        self.label_max_shrink.setScaledContents(True)
        self.label_max_shrink.setObjectName("label_max_shrink")
        self.label_max_shrink_filter = HoverClickFilter()
        self.label_max_shrink.installEventFilter(self.label_max_shrink_filter)
        self.label_max_shrink_filter.hovered.connect(lambda: self.label_max_shrink.setStyleSheet(
            "background-color: rgb(220, 220, 220);\nborder-radius: 15px;"))
        self.label_max_shrink_filter.left.connect(lambda: self.label_max_shrink.setStyleSheet(
            "background-color: rgb(246, 246, 246);\nborder-radius: 15px;"))
        self.horizontalLayout_operation.addWidget(self.label_max_shrink)

        self.label_close = QtWidgets.QLabel(parent=self.widget_operation)
        self.label_close.setMinimumSize(QtCore.QSize(30, 30))
        self.label_close.setMaximumSize(QtCore.QSize(30, 30))
        self.label_close.setStyleSheet("background-color: rgb(245, 245, 245);\n"
                                       "border-radius: 15px;")
        self.label_close.setText("")
        self.label_close_black_photo = self.load_svg_icon("media/close_black.svg")
        self.label_close_white_photo = self.load_svg_icon("media/close_white.svg")
        self.label_close.setPixmap(self.label_close_black_photo)
        self.label_close.setScaledContents(True)
        self.label_close.setObjectName("label_close")
        self.label_close_filter = HoverClickFilter()
        self.label_close.installEventFilter(self.label_close_filter)
        self.label_close_filter.hovered.connect(lambda: (self.label_close.setStyleSheet(
            "background-color: rgb(232, 17, 35);\nborder-radius: 15px;"),
                                                         self.label_close.setPixmap(self.label_close_white_photo)))
        self.label_close_filter.left.connect(lambda: (self.label_close.setStyleSheet(
            "background-color: rgb(246, 246, 246);\nborder-radius: 15px;"),
                                                      self.label_close.setPixmap(self.label_close_black_photo)))
        self.horizontalLayout_operation.addWidget(self.label_close)
        self.verticalLayout_operation.addLayout(self.horizontalLayout_operation)

        self.horizontalLayout_top.addWidget(self.widget_operation)

        self.verticalLayout_main.addWidget(self.widget_top)

        self.widget_main = QtWidgets.QWidget(parent=self)

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_main)
        self.horizontalLayout_3.setContentsMargins(0, -1, 0, 0)
        self.horizontalLayout_3.setSpacing(40)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        # spacerItem = QtWidgets.QSpacerItem(50, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        # self.horizontalLayout_3.addItem(spacerItem)
        self.widget = QtWidgets.QWidget(parent=self.widget_main)
        self.widget.setMinimumSize(QtCore.QSize(400, 0))
        self.widget.setMaximumSize(QtCore.QSize(400, 16777215))
        self.widget.setObjectName("widget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        spacerItem1 = QtWidgets.QSpacerItem(20, 60, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Maximum)
        self.verticalLayout_4.addItem(spacerItem1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        # self.label_play_music_photo = QtWidgets.QLabel(parent=self.widget_play_music)
        self.label_play_music_photo = RoundImageLabel(radius=30)
        self.label_play_music_photo.setMinimumSize(QtCore.QSize(300, 300))
        self.label_play_music_photo.setMaximumSize(QtCore.QSize(300, 300))
        # self.label_play_music_photo.setText("")
        # self.label_play_music_photo.setPixmap(QtGui.QPixmap("1794217775.jpg"))
        # self.label_play_music_photo.setImage(QtGui.QPixmap("1794217775.jpg"))
        success = self.label_play_music_photo.setImageSmart(self.music_library.setting['photo'])
        if not success:
            self.label_play_music_photo.setPixmap(QtGui.QPixmap("media/app_photo.png"))

        self.label_play_music_photo.setScaledContents(True)
        self.label_play_music_photo.setObjectName("label_play_music_photo")
        self.label_play_music_photo_filter = HoverClickFilter()
        self.label_play_music_photo.installEventFilter(self.label_play_music_photo_filter)
        self.label_play_music_photo_filter.clicked.connect(self.main.display_lyrics_page)

        self.horizontalLayout_2.addWidget(self.label_play_music_photo)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        spacerItem4 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.verticalLayout_4.addItem(spacerItem4)
        self.widget_3 = QtWidgets.QWidget(parent=self.widget)
        self.widget_3.setMinimumSize(QtCore.QSize(0, 40))
        self.widget_3.setMaximumSize(QtCore.QSize(16777215, 40))
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem5 = QtWidgets.QSpacerItem(21, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem5)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalSlider_music_progress_bar = QtWidgets.QSlider(parent=self.widget_3)
        self.horizontalSlider_music_progress_bar.setMinimumSize(QtCore.QSize(350, 20))
        self.horizontalSlider_music_progress_bar.setMaximumSize(QtCore.QSize(350, 20))
        self.horizontalSlider_music_progress_bar.setMinimum(0)
        id = self.music_library.setting['id']
        if id:
            self.horizontalSlider_music_progress_bar.setMaximum(self.music_library.get_song_by_id(id)['time'])
        self.horizontalSlider_music_progress_bar.setStyleSheet("QSlider::groove:horizontal {\n"
            "    height: 6px;\n"
            "    background: #ddd;\n"
            "    border-radius: 3px;\n"
            "}\n"
            "QSlider::handle:horizontal {\n"
            "    background: #8FCAFE;\n"
            "    width: 6px;\n"
            "    height: 6px;\n"
            "    border-radius: 3px;\n"
            "}\n"
            "QSlider::sub-page:horizontal {\n"
            "    background: #8FCAFE;\n"
            "    border-radius: 3px;\n"
            "}")
        self.horizontalSlider_music_progress_bar.sliderPressed.connect(self.pause_progress_bar)
        self.horizontalSlider_music_progress_bar.sliderReleased.connect(self.update_progress_bar_play)
        self.horizontalSlider_music_progress_bar.valueChanged.connect(self.update_progress_bar)
        self.horizontalSlider_music_progress_bar.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.horizontalSlider_music_progress_bar.setObjectName("horizontalSlider_music_progress_bar")
        self.verticalLayout.addWidget(self.horizontalSlider_music_progress_bar)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.label_music_time = QtWidgets.QLabel(parent=self.widget_3)
        self.label_music_time.setMinimumSize(QtCore.QSize(30, 0))
        self.label_music_time.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_music_time.setObjectName("label_music_time")
        self.horizontalLayout.addWidget(self.label_music_time)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem6)

        self.label_play_music_duration = QtWidgets.QLabel(parent=self.widget_3)
        self.label_play_music_duration.setMinimumSize(QtCore.QSize(30, 0))
        self.label_play_music_duration.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_play_music_duration.setObjectName("label_play_music_duration")
        self.horizontalLayout.addWidget(self.label_play_music_duration)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_4.addLayout(self.verticalLayout)
        spacerItem7 = QtWidgets.QSpacerItem(21, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem7)
        self.verticalLayout_4.addWidget(self.widget_3)
        self.widget_play = QtWidgets.QWidget(parent=self.widget)
        self.widget_play.setMinimumSize(QtCore.QSize(200, 70))
        self.widget_play.setMaximumSize(QtCore.QSize(16777215, 70))
        self.widget_play.setObjectName("widget_play")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.widget_play)
        self.horizontalLayout_5.setContentsMargins(0, 5, 0, 0)
        self.horizontalLayout_5.setSpacing(10)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")

        self.label_play_type = QtWidgets.QLabel(parent=self.widget_play)
        self.label_play_type.setMinimumSize(QtCore.QSize(25, 25))
        self.label_play_type.setMaximumSize(QtCore.QSize(25, 25))
        self.label_play_type.setText("")
        self.label_play_type_repeat_photo = self.load_svg_icon("media/repeat_1.svg")
        self.label_play_type_sequence_photo = self.load_svg_icon("media/repeat.svg")
        self.label_play_type_random_photo = self.load_svg_icon("media/shuffle.svg")
        if self.music_library.setting['play_type'] == 0:
            self.label_play_type.setPixmap(self.label_play_type_sequence_photo)
        elif self.music_library.setting['play_type'] == 1:
            self.label_play_type.setPixmap(self.label_play_type_repeat_photo)
        else:
            self.label_play_type.setPixmap(self.label_play_type_random_photo)
        self.label_play_type.setScaledContents(True)
        self.label_play_type.setObjectName("label_play_type")
        self.label_play_type.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.label_play_type_filter = HoverClickFilter()
        self.label_play_type.installEventFilter(self.label_play_type_filter)
        self.label_play_type_filter.clicked.connect(self.main.update_play_type)
        self.horizontalLayout_5.addWidget(self.label_play_type)

        self.label_previous_music = QtWidgets.QLabel(parent=self.widget_play)
        self.label_previous_music.setMinimumSize(QtCore.QSize(45, 45))
        self.label_previous_music.setMaximumSize(QtCore.QSize(45, 45))
        self.label_previous_music.setText("")
        self.label_previous_music.setPixmap(self.load_svg_icon("media/backward_end_fill.svg"))
        self.label_previous_music.setScaledContents(True)
        self.label_previous_music.setObjectName("label_previous_music")
        self.label_previous_music.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.label_previous_music_filter = HoverClickFilter()
        self.label_previous_music.installEventFilter(self.label_previous_music_filter)
        self.label_previous_music_filter.clicked.connect(self.main.previous_music)
        self.horizontalLayout_5.addWidget(self.label_previous_music)

        self.label_play_music = QtWidgets.QLabel(parent=self.widget_play)
        self.label_play_music.setMinimumSize(QtCore.QSize(45, 45))
        self.label_play_music.setMaximumSize(QtCore.QSize(45, 45))
        self.label_play_music.setText("")
        self.label_play_music_play_photo = self.load_svg_icon("media/play_circle_fill.svg")
        self.label_play_music_pause_photo = self.load_svg_icon("media/pause_circle_fill.svg")
        if self.music_library.setting['play']:
            self.label_play_music.setPixmap(self.label_play_music_play_photo)
        else:
            self.label_play_music.setPixmap(self.label_play_music_pause_photo)
        self.label_play_music.setScaledContents(True)
        self.label_play_music.setObjectName("label_play_music")
        self.label_play_music.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.label_play_music_filter = HoverClickFilter()
        self.label_play_music.installEventFilter(self.label_play_music_filter)
        self.label_play_music_filter.clicked.connect(self.main.play_music)
        self.horizontalLayout_5.addWidget(self.label_play_music)

        self.label_next_music = QtWidgets.QLabel(parent=self.widget_play)
        self.label_next_music.setMinimumSize(QtCore.QSize(45, 45))
        self.label_next_music.setMaximumSize(QtCore.QSize(45, 45))
        self.label_next_music.setText("")
        self.label_next_music.setPixmap(self.load_svg_icon("media/forward_end_fill.svg"))
        self.label_next_music.setScaledContents(True)
        self.label_next_music.setObjectName("label_next_music")
        self.label_next_music.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.label_next_music_filter = HoverClickFilter()
        self.label_next_music.installEventFilter(self.label_next_music_filter)
        self.label_next_music_filter.clicked.connect(self.main.next_music)
        self.horizontalLayout_5.addWidget(self.label_next_music)

        self.label_play_music_list = QtWidgets.QLabel(parent=self.widget_play)
        self.label_play_music_list.setMinimumSize(QtCore.QSize(25, 25))
        self.label_play_music_list.setMaximumSize(QtCore.QSize(25, 25))
        self.label_play_music_list.setText("")
        self.label_play_music_list.setPixmap(self.load_svg_icon("media/music_note_list.svg"))
        self.label_play_music_list.setScaledContents(True)
        self.label_play_music_list.setObjectName("label_play_music_list")
        self.label_play_music_list.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.label_play_music_list_filter = HoverClickFilter()
        self.label_play_music_list.installEventFilter(self.label_play_music_list_filter)
        self.label_play_music_list_filter.clicked.connect(self.main.display_play_music_list)
        self.horizontalLayout_5.addWidget(self.label_play_music_list)

        self.verticalLayout_4.addWidget(self.widget_play)
        spacerItem8 = QtWidgets.QSpacerItem(20, 100, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Maximum)
        self.verticalLayout_4.addItem(spacerItem8)
        self.horizontalLayout_3.addWidget(self.widget)

        self.widget_2 = QtWidgets.QWidget(parent=self.widget_main)
        self.widget_2.setMinimumSize(QtCore.QSize(400, 0))
        self.widget_2.setMaximumSize(QtCore.QSize(400, 16777215))
        self.widget_2.setObjectName("widget_2")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.widget_2)
        self.verticalLayout_5.setContentsMargins(20, 0, 0, 20)
        self.verticalLayout_5.setSpacing(10)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.widget_music_message = QtWidgets.QWidget(parent=self.widget_2)
        self.widget_music_message.setObjectName("widget_music_message")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget_music_message)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_play_music_name = QtWidgets.QLabel(parent=self.widget_music_message)
        self.label_play_music_name.setMinimumSize(QtCore.QSize(0, 0))
        self.label_play_music_name.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_play_music_name.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_play_music_name.setObjectName("label_play_music_name")
        self.verticalLayout_3.addWidget(self.label_play_music_name)
        self.label_play_music_signer = QtWidgets.QLabel(parent=self.widget_music_message)
        self.label_play_music_signer.setMinimumSize(QtCore.QSize(0, 0))
        self.label_play_music_signer.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_play_music_signer.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_play_music_signer.setObjectName("label_play_music_signer")
        self.verticalLayout_3.addWidget(self.label_play_music_signer)
        self.verticalLayout_5.addWidget(self.widget_music_message)
        self.scrollArea = QtWidgets.QScrollArea(parent=self.widget_2)
        self.scrollArea.setMinimumSize(QtCore.QSize(0, 40))
        self.scrollArea.setStyleSheet("background-color: transparent;\n"
"border: none;")
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 380, 425))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(10)

        # self.display_lyrics()

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_5.addWidget(self.scrollArea)
        self.horizontalLayout_3.addWidget(self.widget_2)
        # spacerItem10 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        # self.horizontalLayout_3.addItem(spacerItem10)
        self.verticalLayout_main.addWidget(self.widget_main)
        # self.verticalLayout_main.addLayout(self.horizontalLayout_3)

        self.retranslateUi()
        # QtCore.QMetaObject.connectSlotsByName()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "Form"))
        self.label_music_time.setText(_translate("Form", "<html><head/><body><p>00:00</p></body></html>"))
        self.label_play_music_duration.setText(_translate("Form", f"<html><head/><body><p>{self.music_library.setting['time']}</p></body></html>"))
        self.label_play_music_name.setText(_translate("Form", f"<html><head/><body><p><span style=\" font-size:12pt; font-weight:700;\">{self.music_library.setting['name']}</span></p></body></html>"))
        self.label_play_music_signer.setText(_translate("Form", f"<html><head/><body><p><span style=\" font-size:12pt; color:#787878;\">{self.music_library.setting['singer']}</span></p></body></html>"))

    def display_lyrics(self):
        self.clear_layout(self.verticalLayout_2)
        self.lyrics_list = {}
        if not self.play_music_control.lyrics:
            label_lyrics = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents)
            label_lyrics.setMinimumSize(QtCore.QSize(0, 40))
            label_lyrics.setMaximumSize(QtCore.QSize(16777215, 16777215))
            label_lyrics.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            label_lyrics.setWordWrap(True)
            label_lyrics.setObjectName("label_lyrics")
            label_lyrics.setText(
                "<html><head/><body><p><span style=\" font-size:14pt; font-weight:700;\">暂无歌词</span></p></body></html>")
            self.verticalLayout_2.addWidget(label_lyrics)
            return

        for i in self.play_music_control.lyrics.keys():
            label_lyrics = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents)
            label_lyrics.setMinimumSize(QtCore.QSize(0, 40))
            label_lyrics.setMaximumSize(QtCore.QSize(16777215, 16777215))
            label_lyrics.setAlignment(
                QtCore.Qt.AlignmentFlag.AlignLeading | QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
            label_lyrics.setWordWrap(True)
            label_lyrics.setObjectName("label_lyrics")

            label_lyrics.setText(self.play_music_control.lyrics[i])
            label_lyrics.setStyleSheet('color: #787878; font-size: 20px; font-weight: 700;')
            self.verticalLayout_2.addWidget(label_lyrics)
            self.lyrics_list[i] = [label_lyrics, False]

        spacerItem9 = QtWidgets.QSpacerItem(20, 122, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_2.addItem(spacerItem9)
        self.scrollArea.verticalScrollBar().setValue(0)
        if self.lyrics_list:
            k = list(self.lyrics_list.keys())[0]
            self.lyrics_list[k][1] = True
            self.lyrics_list[k][0].setStyleSheet('color: #000000; font-size: 25px; font-weight: 700;')

    def update_lyrics(self):
        while True:
            if self.play_music_control.play_status and self.main.lyrics:
                center_index = None
                # current_time = self.play_music_control.player.get_pts()
                current_time = self.play_music_control.player.get_time()/1000
                keys = list(self.lyrics_list.keys())
                if keys[-1] < current_time:
                    if not self.lyrics_list[keys[-1]][1]:
                        self.lyrics_list[keys[len(keys)-1]][1] = True
                        self.update_lyrics_color.emit(self.lyrics_list[keys[len(keys)-1]][0], '#000000', 25)
                        # self.lyrics_list[keys[i]][0].setStyleSheet('color: #000000')
                        center_index = len(keys)-1
                for i in range(len(keys)-1):

                    if keys[i] <= current_time and keys[i+1] > current_time:
                        if not self.lyrics_list[keys[i]][1]:
                            self.lyrics_list[keys[i]][1] = True
                            self.update_lyrics_color.emit(self.lyrics_list[keys[i]][0], '#000000', 25)
                            # self.lyrics_list[keys[i]][0].setStyleSheet('color: #000000')
                            center_index = i
                    else:
                        if self.lyrics_list[keys[i]][1]:
                            self.lyrics_list[keys[i]][1] = False
                            self.update_lyrics_color.emit(self.lyrics_list[keys[i]][0], '#787878',20)
                            # self.lyrics_list[keys[i]][0].setStyleSheet('color: #787878')

                if center_index is not None:
                    label = self.lyrics_list[keys[center_index]][0]
                    label_up = self.lyrics_list[keys[center_index-1]][0]
                    # self.update_lyrics_positioning.emit(label)
                    self.lyrics_positioning(label_up, label)

            time.sleep(0.1)

    def _handle_update_lyrics_color(self, label, color, size):
        try:
            label.setStyleSheet(f'color: {color}; font-size: {size}px; font-weight: 700;')
        except Exception as e:
            pass
            print(e)

    def _handle_update_lyrics_positioning(self, num):
        self.scrollArea.verticalScrollBar().setValue(num)
    def lyrics_positioning(self, label_up , label):
    # def lyrics_positioning(self, num, label):
        target_geometry = label.geometry()
        relative_position = target_geometry.topLeft()
        y = relative_position.y()
        # num += 1
        # size = self.scrollArea.viewport().size()
        # height = size.height()
        # location = int(height/2 + 20)
        location = 150

        # if num * 50 < location:
        if y < location:
            # for i in range(25):
            #     try:
            #         if y:
            #             self.update_lyrics_color.emit(label_up, '#787878', 25 - int((i + 1) / 5))
            #         self.update_lyrics_color.emit(label, '#000000', 20 + int((i + 1) / 5))
            #     except Exception as e:
            #         pass
            #         print(e)
            #     time.sleep(0.01)
            pass
        else:
            for i in range(25):
                self.update_lyrics_positioning.emit(y - location - 50 + i * 2)
                # try:
                #     self.update_lyrics_color.emit(label_up, '#787878', 25 - int((i+1) / 5))
                #     self.update_lyrics_color.emit(label, '#000000', 20 + int((i+1) / 5))
                # except Exception as e:
                #     pass
                #     print(e)

                time.sleep(0.01)

    def update_progress_bar(self,value):
        duration_seconds = int(value / 100)
        minutes, seconds = divmod(duration_seconds, 60)
        if minutes < 10:
            minutes = f"0{minutes}"
        time = f"{minutes}:{seconds:02d}"
        self.label_music_time.setText(f"<html><head/><body><p>{time}</p></body></html>")

    def update_progress_bar_play(self):
        self.play_music_control.change_progress(self.horizontalSlider_music_progress_bar.value())
        self.main.progress_bar = True

    def pause_progress_bar(self):
        self.main.progress_bar = False

    def clear_layout(self, layout):
        """递归清空布局中的所有内容"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())  # 递归清空嵌套布局

    def load_svg_icon(self, svg_path, width=60, height=60):
        renderer = QtSvg.QSvgRenderer(svg_path)
        pixmap = QtGui.QPixmap(width, height)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)  # 设置透明背景
        painter = QtGui.QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return pixmap
