import time
import threading
from PyQt6 import QtCore, QtGui, QtWidgets, QtSvg
from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import pyqtSignal
from widget.hover_click_filter import HoverClickFilter
from widget.music_list_page import MusicListScrollArea
from widget.round_image_label import RoundImageLabel
from widget.rounded_pixmap import rounded_pixmap
from widget.create_playlist_dialog import CreatePlaylistDialog
from widget.play_music_control import PlayMusicControl
from widget.lyrics_page import LyricsPageWidget
from widget.music_list_widget import MusicListWidget
from widget.recommend_page import RecommendScrollArea
from widget.search_list_page import SearchListScrollArea
from widget.setting_musiclist_menu import SettingMusiclistMenu

class Ui_MainWindow(QtWidgets.QWidget):

    def setupUi(self, MainWindow, music_library):
        self.music_library = music_library
        self.progress_bar = True
        self.lyrics = False

        self.recommend_list = {}

        # self.play_music_control = play_music_control
        self.play_music_control = PlayMusicControl(self.music_library,self)
        # self.playlist = playlist
        self.row = -1
        self.scrollArea_music_list = None
        # self.data = data
        MainWindow.setObjectName("巧克力音乐")
        MainWindow.resize(900, 550)
        MainWindow.setMinimumSize(QtCore.QSize(900, 550))
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        MainWindow.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.horizontalLayout_main = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_main.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_main.setSpacing(0)

        self.lyrics_page_widget = LyricsPageWidget(self.music_library, self.play_music_control, self)
        self.horizontalLayout_main.addWidget(self.lyrics_page_widget)
        self.lyrics_page_widget.hide()

        self.main_page_widget = QtWidgets.QWidget(parent=self.centralwidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.main_page_widget)
        self.horizontalLayout_2.setContentsMargins(7, 7, 7, 7)
        self.horizontalLayout_2.setSpacing(7)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.widget = QtWidgets.QWidget(parent=self.main_page_widget)
        self.widget.setMinimumSize(QtCore.QSize(140, 0))
        self.widget.setMaximumSize(QtCore.QSize(140, 16777215))
        self.widget.setStyleSheet("background-color: rgb(245, 245, 245);\n"
                                  "border-radius: 10px;")
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setSpacing(15)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Policy.Minimum,
                                           QtWidgets.QSizePolicy.Policy.Maximum)
        self.verticalLayout.addItem(spacerItem)
        self.label_title = QtWidgets.QLabel(parent=self.widget)
        self.label_title.setStyleSheet("font: 16pt \"楷体\";")
        self.label_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_title.setObjectName("label_title")
        self.verticalLayout.addWidget(self.label_title)
        spacerItem1 = QtWidgets.QSpacerItem(10, 5, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Maximum)
        self.verticalLayout.addItem(spacerItem1)
        self.listWidget = QtWidgets.QListWidget(parent=self.widget)
        self.listWidget.setMinimumSize(QtCore.QSize(130, 160))
        self.listWidget.setMaximumSize(QtCore.QSize(130, 160))
        self.listWidget.setStyleSheet('''
                QListWidget {
                    border: none;  
                    outline: none;
                }
                
                QListWidget::item {
                    background-color: transparent;
                    height: 40px;
                    border-radius: 8px;
                }
            
                QListWidget::item:hover {
                    background-color: rgb(230, 230, 230);
                }
            
                QListWidget::item:selected {
                    background-color: rgb(149,207,253);
                    color: white;
                    border-radius: 8px;
                }
            
                QListWidget::item:selected:!active {
                    background-color: rgb(149,207,253);
                    color: white;
                }''')
        self.listWidget.setObjectName("listWidget")
        self.listWidget.itemClicked.connect(self.update_music_page)
        item = QtWidgets.QListWidgetItem()
        icon = QtGui.QIcon()
        icon.addPixmap(self.load_svg_icon("media/house_fill.svg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        icon.addPixmap(self.load_svg_icon("media/house_white_fill.svg"), QtGui.QIcon.Mode.Selected, QtGui.QIcon.State.Off)
        item.setIcon(icon)
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        icon1 = QtGui.QIcon()
        icon1.addPixmap(self.load_svg_icon("media/heart_fill.svg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        icon1.addPixmap(self.load_svg_icon("media/heart_white_fill.svg"), QtGui.QIcon.Mode.Selected, QtGui.QIcon.State.Off)
        item.setIcon(icon1)
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        icon2 = QtGui.QIcon()
        icon2.addPixmap(self.load_svg_icon("media/clock_fill.svg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        icon2.addPixmap(self.load_svg_icon("media/clock_white_fill.svg"), QtGui.QIcon.Mode.Selected, QtGui.QIcon.State.Off)
        item.setIcon(icon2)
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        icon3 = QtGui.QIcon()
        icon3.addPixmap(self.load_svg_icon("media/arrowshape_down_to_line_fill.svg"), QtGui.QIcon.Mode.Normal,
                        QtGui.QIcon.State.Off)
        icon3.addPixmap(self.load_svg_icon("media/arrowshape_down_to_line_white_fill.svg"), QtGui.QIcon.Mode.Selected,
                        QtGui.QIcon.State.Off)
        item.setIcon(icon3)
        self.listWidget.addItem(item)
        self.listWidget.setCurrentRow(0)

        self.verticalLayout.addWidget(self.listWidget)
        spacerItem2 = QtWidgets.QSpacerItem(10, 15, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Maximum)
        self.verticalLayout.addItem(spacerItem2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_my_playlist = QtWidgets.QLabel(parent=self.widget)
        self.label_my_playlist.setObjectName("label_my_playlist")
        self.horizontalLayout.addWidget(self.label_my_playlist)

        self.label_add_playlist = QtWidgets.QLabel(parent=self.widget)
        self.label_add_playlist.setMinimumSize(QtCore.QSize(15, 15))
        self.label_add_playlist.setMaximumSize(QtCore.QSize(15, 15))
        self.label_add_playlist.setText("")
        self.label_add_playlist.setPixmap(self.load_svg_icon("media/plus.svg"))
        self.label_add_playlist.setScaledContents(True)
        self.label_add_playlist.setObjectName("label_add_playlist")
        self.label_add_playlist.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.label_add_playlist_filter = HoverClickFilter()
        self.label_add_playlist.installEventFilter(self.label_add_playlist_filter)
        self.label_add_playlist_filter.clicked.connect(self.add_playlist)
        self.horizontalLayout.addWidget(self.label_add_playlist)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.listWidget_2 = QtWidgets.QListWidget(parent=self.widget)
        self.listWidget_2.setMinimumSize(QtCore.QSize(130, 230))
        self.listWidget_2.setMaximumSize(QtCore.QSize(130, 16777215))
        self.listWidget_2.setStyleSheet('''
                QListWidget {
                    border: none;  
                    outline: none;
                }
                
                QListWidget::item {
                    background-color: transparent;
                    height: 40px;
                    border-radius: 8px;
                    padding: 6px;
                }
            
                QListWidget::item:hover {
                    background-color: rgb(230, 230, 230);
                }
            
                QListWidget::item:selected {
                    background-color: rgb(149,207,253);
                    color: white;
                    border-radius: 8px;
                }
            
                QListWidget::item:selected:!active {
                    background-color: rgb(149,207,253);
                    color: white;
                }
                QListWidget QScrollBar:vertical {
                    border: none;
                    background: transparent; /* 滚动条背景透明 */
                    width: 4px; /* 垂直滚动条的宽度 */
                    margin: 0px;
                }
                /* 垂直滚动条的手柄 */
                QListWidget QScrollBar::handle:vertical {
                    background: #e6e6e6; /* 手柄颜色 */
                    border-radius: 2px; /* 圆角半径，设为宽度的一半可得到圆形端点 */
                    min-height: 30px; /* 手柄的最小高度 */
                }
                /* 当鼠标悬停在垂直滚动条手柄上时 */
                QListWidget QScrollBar::handle:vertical:hover {
                    background: #a0a0a0; /* 悬停时手柄颜色 */
                }
                /* 垂直滚动条的顶部和底部箭头按钮（此处设置为隐藏） */
                QListWidget QScrollBar::add-line:vertical, 
                QListWidget QScrollBar::sub-line:vertical {
                    height: 0px; /* 将箭头按钮的高度或宽度设置为0以达到隐藏效果 */
                }
                /* 垂直滚动条的滚动区域（手柄与箭头之间的区域） */
                QListWidget QScrollBar::add-page:vertical, 
                QListWidget QScrollBar::sub-page:vertical {
                    background: transparent; /* 通常设置为透明或与滚动条背景一致 */
                }
                
                /* 设置水平滚动条 - 原理同垂直滚动条，将 width/height 等属性互换 */
                QListWidget QScrollBar:horizontal {
                    border: none;
                    background: transparent;
                    height: 4px; /* 水平滚动条的高度 */
                    margin: 0px;
                }
                QListWidget QScrollBar::handle:horizontal {
                    background: #c0c0c0;
                    border-radius: 2px;
                    min-width: 30px; /* 手柄的最小宽度 */
                }
                QListWidget QScrollBar::handle:horizontal:hover {
                    background: #a0a0a0;
                }
                QListWidget QScrollBar::add-line:horizontal, 
                QListWidget QScrollBar::sub-line:horizontal {
                    width: 0px;
                }
                QListWidget QScrollBar::add-page:horizontal, 
                QListWidget QScrollBar::sub-page:horizontal {
                    background: transparent;
                }''')
        self.listWidget_2.setIconSize(QtCore.QSize(40, 40))
        self.listWidget_2.setObjectName("listWidget_2")
        self.listWidget_2.itemClicked.connect(self.update_my_music_page)
        # pm = rounded_pixmap(QtGui.QPixmap("1794217775.jpg"), 40, 4)
        # pm = rounded_pixmap("1794217775.jpg", 40, 4)
        self.update_playlist_list()
        # pm = rounded_pixmap("E:/XJH/音乐/XJH/周杰伦 - 说好的幸福呢.mp3", 40, 4)
        # if pm:
        #     icon4 = QtGui.QIcon()
        #     icon4.addPixmap(pm, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        #     icon4.addPixmap(pm, QtGui.QIcon.Mode.Selected, QtGui.QIcon.State.Off)
        # else:
        #     icon4 = QtGui.QIcon()
        #     icon4.addPixmap(QtGui.QPixmap("media/app_photo.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        #     icon4.addPixmap(QtGui.QPixmap("media/app_photo.png"), QtGui.QIcon.Mode.Selected, QtGui.QIcon.State.Off)
        # item.setIcon(icon4)
        # self.listWidget_2.addItem(item)
        self.verticalLayout.addWidget(self.listWidget_2)
        # spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
        #                                     QtWidgets.QSizePolicy.Policy.Expanding)
        # self.verticalLayout.addItem(spacerItem3)
        self.horizontalLayout_2.addWidget(self.widget)
        self.widget_2 = QtWidgets.QWidget(parent=self.main_page_widget)
        self.widget_2.setObjectName("widget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(5)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.widget_5 = QtWidgets.QWidget(parent=self.widget_2)
        self.widget_5.setMinimumSize(QtCore.QSize(0, 30))
        self.widget_5.setMaximumSize(QtCore.QSize(16777215, 30))
        self.widget_5.setStyleSheet("")
        self.widget_5.setObjectName("widget_5")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.widget_5)
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_8.setSpacing(5)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")

        self.widget_9 = QtWidgets.QWidget(parent=self.widget_5)
        self.widget_9.setMinimumSize(QtCore.QSize(30, 30))
        self.widget_9.setMaximumSize(QtCore.QSize(30, 30))
        self.widget_9.setStyleSheet("background-color: rgb(245, 245, 245);\n"
                                    "border-radius: 15px;")
        self.widget_9.setObjectName("widget_9")
        self.widget_9.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.widget_9_filter = HoverClickFilter()
        self.widget_9.installEventFilter(self.widget_9_filter)
        self.widget_9_filter.hovered.connect(lambda: self.widget_9.setStyleSheet(
            "background-color: rgb(230, 230, 230);\nborder-radius: 15px;"))
        self.widget_9_filter.left.connect(lambda: self.widget_9.setStyleSheet(
            "background-color: rgb(246, 246, 246);\nborder-radius: 15px;"))
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.widget_9)
        self.verticalLayout_9.setContentsMargins(5, 0, 5, 0)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName("verticalLayout_9")

        self.label_sprevious_page = QtWidgets.QLabel(parent=self.widget_9)
        self.label_sprevious_page.setMinimumSize(QtCore.QSize(20, 25))
        self.label_sprevious_page.setMaximumSize(QtCore.QSize(20, 25))
        self.label_sprevious_page.setStyleSheet("")
        self.label_sprevious_page.setText("")
        self.label_sprevious_page.setPixmap(self.load_svg_icon("media/chevron_left.svg"))
        self.label_sprevious_page.setScaledContents(True)
        self.label_sprevious_page.setObjectName("label_sprevious_page")
        self.label_sprevious_page.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.verticalLayout_9.addWidget(self.label_sprevious_page)
        self.horizontalLayout_8.addWidget(self.widget_9)

        self.widget_10 = QtWidgets.QWidget(parent=self.widget_5)
        self.widget_10.setMinimumSize(QtCore.QSize(30, 30))
        self.widget_10.setMaximumSize(QtCore.QSize(30, 30))
        self.widget_10.setStyleSheet("background-color: rgb(245, 245, 245);\n"
                                     "border-radius: 15px;")
        self.widget_10.setObjectName("widget_10")
        self.widget_10.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.widget_10_filter = HoverClickFilter()
        self.widget_10.installEventFilter(self.widget_10_filter)
        self.widget_10_filter.hovered.connect(lambda: self.widget_10.setStyleSheet(
            "background-color: rgb(230, 230, 230);\nborder-radius: 15px;"))
        self.widget_10_filter.left.connect(lambda: self.widget_10.setStyleSheet(
            "background-color: rgb(246, 246, 246);\nborder-radius: 15px;"))
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.widget_10)
        self.verticalLayout_10.setContentsMargins(5, 0, 5, 0)
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setObjectName("verticalLayout_10")

        self.label_next_page = QtWidgets.QLabel(parent=self.widget_10)
        self.label_next_page.setMinimumSize(QtCore.QSize(20, 25))
        self.label_next_page.setMaximumSize(QtCore.QSize(20, 25))
        self.label_next_page.setStyleSheet("")
        self.label_next_page.setText("")
        self.label_next_page.setPixmap(self.load_svg_icon("media/chevron_right.svg"))
        self.label_next_page.setScaledContents(True)
        self.verticalLayout_10.addWidget(self.label_next_page)
        self.horizontalLayout_8.addWidget(self.widget_10)

        self.widget_3 = QtWidgets.QWidget(parent=self.widget_5)
        self.widget_3.setMinimumSize(QtCore.QSize(0, 30))
        self.widget_3.setMaximumSize(QtCore.QSize(16777215, 30))
        self.widget_3.setStyleSheet("background-color: rgb(245, 245, 245);\n"
                                    "border-radius: 15px;")
        self.widget_3.setObjectName("widget_3")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.widget_3)
        self.verticalLayout_8.setContentsMargins(10, 0, 10, 0)
        self.verticalLayout_8.setSpacing(5)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setSpacing(10)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")

        self.label = QtWidgets.QLabel(parent=self.widget_3)
        self.label.setMinimumSize(QtCore.QSize(20, 20))
        self.label.setMaximumSize(QtCore.QSize(20, 20))
        self.label.setText("")
        self.label.setPixmap(self.load_svg_icon("media/magnifyingglass.svg"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.label.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.label_filter = HoverClickFilter()
        self.label.installEventFilter(self.label_filter)
        self.label_filter.clicked.connect(self.search_music_library_music)
        self.horizontalLayout_10.addWidget(self.label)

        self.lineEdit_search = QtWidgets.QLineEdit(parent=self.widget_3)
        self.lineEdit_search.setMinimumSize(QtCore.QSize(140, 25))
        self.lineEdit_search.setMaximumSize(QtCore.QSize(16777215, 25))
        self.lineEdit_search.setStyleSheet("border: none;")
        self.lineEdit_search.setText("")
        self.lineEdit_search.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        self.lineEdit_search.setObjectName("lineEdit_search")
        self.lineEdit_search.returnPressed.connect(self.search_music_library_music)
        self.horizontalLayout_10.addWidget(self.lineEdit_search)
        self.verticalLayout_8.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_8.addWidget(self.widget_3)

        self.widget_8 = QtWidgets.QWidget(parent=self.widget_5)
        self.widget_8.setMinimumSize(QtCore.QSize(30, 30))
        self.widget_8.setMaximumSize(QtCore.QSize(30, 30))
        self.widget_8.setStyleSheet("background-color: rgb(245, 245, 245);\n"
                                    "border-radius: 15px;")
        self.widget_8_filter = HoverClickFilter()
        self.widget_8.installEventFilter(self.widget_8_filter)
        self.widget_8_filter.hovered.connect(lambda: self.widget_8.setStyleSheet(
            "background-color: rgb(230, 230, 230);\nborder-radius: 15px;"))
        self.widget_8_filter.left.connect(lambda: self.widget_8.setStyleSheet(
            "background-color: rgb(246, 246, 246);\nborder-radius: 15px;"))
        self.widget_8.setObjectName("widget_8")
        self.widget_8.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.widget_8)
        self.verticalLayout_7.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")

        self.label_setting = QtWidgets.QLabel(parent=self.widget_8)
        self.label_setting.setMinimumSize(QtCore.QSize(20, 20))
        self.label_setting.setMaximumSize(QtCore.QSize(20, 20))
        self.label_setting.setStyleSheet("")
        self.label_setting.setText("")
        self.label_setting.setPixmap(self.load_svg_icon("media/gearshape.svg"))
        self.label_setting.setScaledContents(True)
        self.label_setting.setObjectName("label_setting")
        self.verticalLayout_7.addWidget(self.label_setting)
        self.horizontalLayout_8.addWidget(self.widget_8)

        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Fixed,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem4)
        self.widget_7 = QtWidgets.QWidget(parent=self.widget_5)
        self.widget_7.setMinimumSize(QtCore.QSize(100, 30))
        self.widget_7.setMaximumSize(QtCore.QSize(100, 30))
        self.widget_7.setStyleSheet("")
        self.widget_7.setObjectName("widget_7")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.widget_7)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")

        self.label_min = QtWidgets.QLabel(parent=self.widget_7)
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
        self.horizontalLayout_9.addWidget(self.label_min)

        self.label_max_shrink = QtWidgets.QLabel(parent=self.widget_7)
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
        self.horizontalLayout_9.addWidget(self.label_max_shrink)

        self.label_close = QtWidgets.QLabel(parent=self.widget_7)
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
        self.horizontalLayout_9.addWidget(self.label_close)
        self.verticalLayout_6.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_8.addWidget(self.widget_7)
        self.verticalLayout_2.addWidget(self.widget_5)
        self.widget_list_page = QtWidgets.QWidget(parent=self.widget_2)
        self.widget_list_page.setStyleSheet("QWidget {\n"
                                            "    background-color: rgb(245, 245, 245);\n"
                                            "    border-radius: 10px;\n"
                                            "}")
        self.widget_list_page.setObjectName("widget_list_page")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.widget_list_page)
        self.verticalLayout_12.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_12.setSpacing(5)
        self.verticalLayout_12.setObjectName("verticalLayout_12")

        self.verticalLayout_2.addWidget(self.widget_list_page)
        self.widget_play_music = QtWidgets.QWidget(parent=self.widget_2)
        self.widget_play_music.setMinimumSize(QtCore.QSize(0, 80))
        self.widget_play_music.setMaximumSize(QtCore.QSize(16777215, 80))
        self.widget_play_music.setStyleSheet("background-color: rgb(245, 245, 245);\n"
                                             "border-radius: 10px;")
        self.widget_play_music.setObjectName("widget_play_music")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.widget_play_music)
        self.horizontalLayout_7.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")

        # self.label_play_music_photo = QtWidgets.QLabel(parent=self.widget_play_music)
        self.label_play_music_photo = RoundImageLabel(radius=6)
        self.label_play_music_photo.setMinimumSize(QtCore.QSize(60, 60))
        self.label_play_music_photo.setMaximumSize(QtCore.QSize(60, 60))
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
        self.label_play_music_photo_filter.clicked.connect(self.display_lyrics_page)

        self.horizontalLayout_7.addWidget(self.label_play_music_photo)
        self.widget_music_message = QtWidgets.QWidget(parent=self.widget_play_music)
        self.widget_music_message.setObjectName("widget_music_message")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget_music_message)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        self.label_play_music_name = QtWidgets.QLabel(parent=self.widget_music_message)
        self.label_play_music_name.setObjectName("label_play_music_name")
        self.label_play_music_name.setMinimumSize(QtCore.QSize(90, 0))
        self.label_play_music_name.setMaximumSize(QtCore.QSize(90, 16777215))
        self.verticalLayout_3.addWidget(self.label_play_music_name)
        self.label_play_music_signer = QtWidgets.QLabel(parent=self.widget_music_message)
        self.label_play_music_signer.setMinimumSize(QtCore.QSize(90, 0))
        self.label_play_music_signer.setMaximumSize(QtCore.QSize(90, 16777215))
        self.label_play_music_signer.setObjectName("label_play_music_signer")
        self.verticalLayout_3.addWidget(self.label_play_music_signer)
        self.horizontalLayout_7.addWidget(self.widget_music_message)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")

        self.widget_play = QtWidgets.QWidget(parent=self.widget_play_music)
        self.widget_play.setMinimumSize(QtCore.QSize(200, 40))
        self.widget_play.setMaximumSize(QtCore.QSize(16777215, 40))
        self.widget_play.setObjectName("widget_play")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.widget_play)
        self.horizontalLayout_5.setContentsMargins(0, 5, 0, 0)
        self.horizontalLayout_5.setSpacing(10)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem5)

        self.label_play_type = QtWidgets.QLabel(parent=self.widget_play)
        self.label_play_type.setMinimumSize(QtCore.QSize(30, 30))
        self.label_play_type.setMaximumSize(QtCore.QSize(30, 30))
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
        self.label_play_type_filter.clicked.connect(self.update_play_type)
        self.horizontalLayout_5.addWidget(self.label_play_type)

        self.label_previous_music = QtWidgets.QLabel(parent=self.widget_play)
        self.label_previous_music.setMinimumSize(QtCore.QSize(30, 30))
        self.label_previous_music.setMaximumSize(QtCore.QSize(30, 30))
        self.label_previous_music.setText("")
        self.label_previous_music.setPixmap(self.load_svg_icon("media/backward_end_fill.svg"))
        self.label_previous_music.setScaledContents(True)
        self.label_previous_music.setObjectName("label_previous_music")
        self.label_previous_music.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.label_previous_music_filter = HoverClickFilter()
        self.label_previous_music.installEventFilter(self.label_previous_music_filter)
        self.label_previous_music_filter.clicked.connect(self.previous_music)
        self.horizontalLayout_5.addWidget(self.label_previous_music)

        self.label_play_music = QtWidgets.QLabel(parent=self.widget_play)
        self.label_play_music.setMinimumSize(QtCore.QSize(30, 30))
        self.label_play_music.setMaximumSize(QtCore.QSize(30, 30))
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
        self.label_play_music_filter.clicked.connect(self.play_music)
        self.horizontalLayout_5.addWidget(self.label_play_music)

        self.label_next_music = QtWidgets.QLabel(parent=self.widget_play)
        self.label_next_music.setMinimumSize(QtCore.QSize(30, 30))
        self.label_next_music.setMaximumSize(QtCore.QSize(30, 30))
        self.label_next_music.setText("")
        self.label_next_music.setPixmap(self.load_svg_icon("media/forward_end_fill.svg"))
        self.label_next_music.setScaledContents(True)
        self.label_next_music.setObjectName("label_next_music")
        self.label_next_music.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.label_next_music_filter = HoverClickFilter()
        self.label_next_music.installEventFilter(self.label_next_music_filter)
        self.label_next_music_filter.clicked.connect(self.next_music)
        self.horizontalLayout_5.addWidget(self.label_next_music)

        self.label_play_music_list = QtWidgets.QLabel(parent=self.widget_play)
        self.label_play_music_list.setMinimumSize(QtCore.QSize(30, 30))
        self.label_play_music_list.setMaximumSize(QtCore.QSize(30, 30))
        self.label_play_music_list.setText("")
        self.label_play_music_list.setPixmap(self.load_svg_icon("media/music_note_list.svg"))
        self.label_play_music_list.setScaledContents(True)
        self.label_play_music_list.setObjectName("label_play_music_list")
        self.label_play_music_list.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.label_play_music_list_filter = HoverClickFilter()
        self.label_play_music_list.installEventFilter(self.label_play_music_list_filter)
        self.label_play_music_list_filter.clicked.connect(self.display_play_music_list)
        self.horizontalLayout_5.addWidget(self.label_play_music_list)

        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem6)
        self.verticalLayout_4.addWidget(self.widget_play)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(8)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        self.label_music_time = QtWidgets.QLabel(parent=self.widget_play_music)
        self.label_music_time.setMinimumSize(QtCore.QSize(32, 0))
        self.label_music_time.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeading | QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_music_time.setObjectName("label_music_time")
        self.horizontalLayout_3.addWidget(self.label_music_time)

        self.horizontalSlider_music_progress_bar = QtWidgets.QSlider(parent=self.widget_play_music)
        self.horizontalSlider_music_progress_bar.setMinimumSize(QtCore.QSize(300, 20))
        self.horizontalSlider_music_progress_bar.setMaximumSize(QtCore.QSize(16777215, 20))
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
        self.horizontalLayout_3.addWidget(self.horizontalSlider_music_progress_bar)

        self.label_play_music_duration = QtWidgets.QLabel(parent=self.widget_play_music)
        self.label_play_music_duration.setMinimumSize(QtCore.QSize(32, 0))
        self.label_play_music_duration.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_play_music_duration.setObjectName("label_play_music_duration")
        self.horizontalLayout_3.addWidget(self.label_play_music_duration)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_7.addLayout(self.verticalLayout_4)

        self.widget_6 = QtWidgets.QWidget(parent=self.widget_play_music)
        self.widget_6.setMinimumSize(QtCore.QSize(170, 0))
        self.widget_6.setMaximumSize(QtCore.QSize(170, 16777215))
        self.widget_6.setObjectName("widget_6")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.widget_6)
        self.verticalLayout_5.setContentsMargins(5, -1, 5, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        spacerItem7 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_5.addItem(spacerItem7)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setContentsMargins(-1, -1, -1, 1)
        self.horizontalLayout_6.setSpacing(8)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")

        self.label_collection = QtWidgets.QLabel(parent=self.widget_6)
        self.label_collection.setMinimumSize(QtCore.QSize(20, 20))
        self.label_collection.setMaximumSize(QtCore.QSize(20, 20))
        self.label_collection.setAutoFillBackground(False)
        self.label_collection.setText("")
        self.label_collection_white_photo = self.load_svg_icon("media/heart.svg")
        self.label_collection_red_photo = self.load_svg_icon("media/heart_red_fill.svg")
        if self.music_library.setting['like']:
            self.label_collection.setPixmap(self.label_collection_red_photo)
        else:
            self.label_collection.setPixmap(self.label_collection_white_photo)
        self.label_collection.setScaledContents(True)
        self.label_collection.setObjectName("label_collection")
        self.label_collection.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.label_collection_filter = HoverClickFilter()
        self.label_collection.installEventFilter(self.label_collection_filter)
        self.label_collection_filter.clicked.connect(self.update_heart)
        self.horizontalLayout_6.addWidget(self.label_collection)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(5)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")

        self.label_volume = QtWidgets.QLabel(parent=self.widget_6)
        self.label_volume.setMinimumSize(QtCore.QSize(20, 20))
        self.label_volume.setMaximumSize(QtCore.QSize(20, 20))
        self.label_volume.setText("")
        self.label_volume_photo = self.load_svg_icon("media/speaker_wave_3.svg")
        self.label_volume_not_photo = self.load_svg_icon("media/speaker_slash.svg")
        if self.music_library.setting['volume_type']:
            self.label_volume.setPixmap(self.label_volume_photo)
        else:
            self.label_volume.setPixmap(self.label_volume_not_photo)
        self.label_volume.setScaledContents(True)
        self.label_volume.setObjectName("label_volume")
        self.label_volume.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.label_volume_filter = HoverClickFilter()
        self.label_volume.installEventFilter(self.label_volume_filter)
        self.label_volume_filter.clicked.connect(self.update_volume_status)
        self.horizontalLayout_4.addWidget(self.label_volume)

        self.horizontalSlider_volume = QtWidgets.QSlider(parent=self.widget_6)
        self.horizontalSlider_volume.setMinimumSize(QtCore.QSize(80, 20))
        self.horizontalSlider_volume.setMaximumSize(QtCore.QSize(80, 20))
        self.horizontalSlider_volume.setMinimum(0)
        self.horizontalSlider_volume.setMaximum(100)
        if self.music_library.setting['volume_type']:
            self.horizontalSlider_volume.setValue(self.music_library.setting['volume'])
        else:
            self.horizontalSlider_volume.setValue(0)
        self.horizontalSlider_volume.setStyleSheet("QSlider::groove:horizontal {\n"
                                                   "    height: 6px;\n"
                                                   "    background: #ddd;\n"
                                                   "    border-radius: 3px;\n"
                                                   "}\n"
                                                   "QSlider::handle:horizontal {\n"
                                                   "    background: #BBB2FF;\n"
                                                   "    width: 6px;\n"
                                                   "    height: 6px;\n"
                                                   "    border-radius: 3px;\n"
                                                   "}\n"
                                                   "QSlider::sub-page:horizontal {\n"
                                                   "    background: #BBB2FF;\n"
                                                   "    border-radius: 3px;\n"
                                                   "}")
        self.horizontalSlider_volume.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.horizontalSlider_volume.sliderReleased.connect(self.update_volume_storage)
        self.horizontalSlider_volume.valueChanged.connect(self.update_volume_size)
        self.horizontalSlider_volume.setObjectName("horizontalSlider_volume")
        self.horizontalLayout_4.addWidget(self.horizontalSlider_volume)
        self.horizontalLayout_6.addLayout(self.horizontalLayout_4)
        self.verticalLayout_5.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7.addWidget(self.widget_6)
        self.verticalLayout_2.addWidget(self.widget_play_music)
        self.horizontalLayout_2.addWidget(self.widget_2)
        self.horizontalLayout_main.addWidget(self.main_page_widget)

        self.setting_menu = SettingMusiclistMenu(parent=self)
        self.setting_menu.sortChanged.connect(self.update_musiclist)

        # self.main_page_widget.hide()

        self.update_music_page(self.listWidget.item(0))

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_title.setText(_translate("MainWindow",
                                            "<html><head/><body><p align=\"center\"><span style=\" font-size:16pt;\">音乐</span></p></body></html>"))
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        item = self.listWidget.item(0)
        item.setText(_translate("MainWindow", "首页"))
        item = self.listWidget.item(1)
        item.setText(_translate("MainWindow", "我喜欢"))
        item = self.listWidget.item(2)
        item.setText(_translate("MainWindow", "最近播放"))
        item = self.listWidget.item(3)
        item.setText(_translate("MainWindow", "本地下载"))
        self.listWidget.setSortingEnabled(__sortingEnabled)
        self.label_my_playlist.setText(_translate("MainWindow", "我的歌单"))
        __sortingEnabled = self.listWidget_2.isSortingEnabled()
        self.listWidget_2.setSortingEnabled(False)
        self.listWidget_2.setSortingEnabled(__sortingEnabled)
        self.lineEdit_search.setPlaceholderText(_translate("MainWindow", "搜索"))
        self.label_play_music_name.setText(_translate("MainWindow",
                                                      f"<html><head/><body><p><span style=\" font-size:10pt;\">{self.music_library.setting['name']}</span></p></body></html>"))
        self.label_play_music_signer.setText(f"<html><head/><body><p><span style=\" font-size:10pt; color:#787878;\">{self.music_library.setting['singer']}</span></p></body></html>")
        self.label_music_time.setText(_translate("MainWindow", "<html><head/><body><p>00:00</p></body></html>"))
        self.label_play_music_duration.setText(f"<html><head/><body><p>{self.music_library.setting['time']}</p></body></html>")

    def update_music_page(self, item):
        row = self.listWidget.row(item)

        if row == self.row:
            return
        if self.row > 3:
            self.listWidget_2.clearSelection()

        self.clear_layout(self.verticalLayout_12)
        self.scrollArea_music_list = None

        # with open('data/playlist.json', 'r', encoding='utf-8') as f:
        #     self.playlist = json.load(f)

        if row == 0:
            if not self.music_library.get_all_music():
                label = QtWidgets.QLabel()
                label.setText("暂无音乐")
                label.setStyleSheet("font-size: 20px;")
                label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.verticalLayout_12.addWidget(label)
            else:
                self.scrollArea_recommend_page = RecommendScrollArea(self.music_library, self.play_music_control, self)
                self.verticalLayout_12.addWidget(self.scrollArea_recommend_page)
        elif row == 1:
            # data = {'id': 0, 'name': '我喜欢', 'num': 120, 'photo': "media/collection_photo.png"}
            self.scrollArea_music_list = MusicListScrollArea(self.music_library, self.play_music_control, 0, self)
            self.verticalLayout_12.addWidget(self.scrollArea_music_list)
        elif row == 2:
            print("最近播放")
        elif row == 3:
            print("本地下载")
        self.row = row

    def update_my_music_page(self, item):
        row = self.listWidget_2.row(item) + 6
        if row == self.row:
            return
        if self.row <= 5:
            self.listWidget.clearSelection()

        self.clear_layout(self.verticalLayout_12)
        self.scrollArea_music_list = None

        # with open('data/playlist.json', 'r', encoding='utf-8') as f:
        #     self.playlist = json.load(f)

        # data = {'name': item.text(), 'num': 50, 'photo': "media/app_photo.png"}
        # data = {'name': item.text(), 'num': 50, 'photo': "E:/XJH/音乐/XJH/周杰伦 - 说好的幸福呢.flac"}
        # data = self.music_library.playlist[f'{row-3}']

        # id = int(list(self.music_library.playlist.keys())[row-3]
        id = self.music_library.get_playlist_list()[row-3]
        self.scrollArea_music_list = MusicListScrollArea(self.music_library, self.play_music_control, id, self)
        self.verticalLayout_12.addWidget(self.scrollArea_music_list)
        self.row = row

    def update_max_shrink(self, is_maximized):
        if is_maximized:
            self.label_max_shrink.setPixmap(self.label_shrink_to_max_photo)
            self.lyrics_page_widget.label_max_shrink.setPixmap(self.label_shrink_to_max_photo)
        else:
            self.label_max_shrink.setPixmap(self.label_max_to_shrink_photo)
            self.lyrics_page_widget.label_max_shrink.setPixmap(self.label_max_to_shrink_photo)

    def previous_music(self):
        if not self.music_library.setting['id']:
            return
        self.play_music_control.previous_music()

    def next_music(self):
        if not self.music_library.setting['id']:
            return

        self.play_music_control.next_music()

    def play_music(self):
    # 检查音乐库中是否有音乐ID，如果没有则直接返回
        if not self.music_library.setting['id']:
            return

    # 检查当前是否正在播放音乐
        if self.music_library.setting['play']:
        # 如果正在播放，则将播放按钮图标设置为暂停图标
            self.label_play_music.setPixmap(self.label_play_music_pause_photo)
            self.lyrics_page_widget.label_play_music.setPixmap(self.label_play_music_pause_photo)
        # 调用暂停音乐的方法
        #     self.play_music_control.pause_music()
        else:
        # 如果没有播放，则将播放按钮图标设置为播放图标
            self.label_play_music.setPixmap(self.label_play_music_play_photo)
            self.lyrics_page_widget.label_play_music.setPixmap(self.label_play_music_play_photo)
        # 调用恢复播放音乐的方法
        #     self.play_music_control.unpause_music()

        self.play_music_control.pause_or_play_music()

        self.music_library.setting['play'] = not self.music_library.setting['play']

    def display_play_music_list(self):
        if not self.music_library.setting['id']:
            return
        print("显示播放列表")

    def update_heart(self):
        if not self.music_library.setting['id']:
            return

        if self.music_library.setting['like']:
            self.label_collection.setPixmap(self.label_collection_white_photo)
        else:
            self.label_collection.setPixmap(self.label_collection_red_photo)
        self.music_library.setting['like'] = not self.music_library.get_song_by_id(self.music_library.setting['id'])['like']
        # self.music_library.get_song_by_id(self.music_library.setting['id'])['like'] = self.music_library.setting['like']
        self.music_library.update_like(self.music_library.setting['id'], self.music_library.setting['like'])
        self.music_library.is_or_no_like(self.music_library.setting['id'])

        if self.row == 0:
            music_list_widget = self.scrollArea_recommend_page.list.get(self.music_library.setting['id'], 0)

            if music_list_widget:
                if self.music_library.setting['like']:
                    music_list_widget.label_heart.setPixmap(music_list_widget.label_heart_red_photo)
                else:
                    music_list_widget.label_heart.setPixmap(music_list_widget.label_heart_white_photo)

        elif self.scrollArea_music_list:
            music_list_widget = self.scrollArea_music_list.list.get(self.music_library.setting['id'], 0)

            if music_list_widget:
                if self.music_library.setting['like']:
                    music_list_widget.label_heart.setPixmap(music_list_widget.label_heart_red_photo)
                else:
                    music_list_widget.label_heart.setPixmap(music_list_widget.label_heart_white_photo)
                # music_list_widget.data = self.music_library.get_song_by_id(self.music_library.setting['id'])\

            search_music_list_widget = self.scrollArea_music_list.search_list.get(self.music_library.setting['id'], 0)
            if search_music_list_widget:
                if self.music_library.setting['like']:
                    search_music_list_widget.label_heart.setPixmap(search_music_list_widget.label_heart_red_photo)
                else:
                    search_music_list_widget.label_heart.setPixmap(search_music_list_widget.label_heart_white_photo)

            if self.scrollArea_music_list.id == 0:
                self.scrollArea_music_list.update_page()
        if self.row == -1:
            music_list_widget = self.scrollArea_search_music_list.search_list.get(self.music_library.setting['id'], 0)

            if music_list_widget:

                if self.music_library.setting['like']:
                    music_list_widget.label_heart.setPixmap(music_list_widget.label_heart_red_photo)
                else:
                    music_list_widget.label_heart.setPixmap(music_list_widget.label_heart_white_photo)


    def update_play_type(self):
        if self.music_library.setting['play_type'] == 0:
            self.label_play_type.setPixmap(self.label_play_type_repeat_photo)
            self.lyrics_page_widget.label_play_type.setPixmap(self.label_play_type_repeat_photo)
            self.music_library.setting['play_type'] = 1
        elif self.music_library.setting['play_type'] == 1:
            self.label_play_type.setPixmap(self.label_play_type_random_photo)
            self.lyrics_page_widget.label_play_type.setPixmap(self.label_play_type_random_photo)
            self.music_library.setting['play_type'] = 2
        elif self.music_library.setting['play_type'] == 2:
            self.label_play_type.setPixmap(self.label_play_type_sequence_photo)
            self.lyrics_page_widget.label_play_type.setPixmap(self.label_play_type_sequence_photo)
            self.music_library.setting['play_type'] = 0
        self.music_library.update()

    def update_volume_status(self):
        if self.music_library.setting['volume_type']:
            self.label_volume.setPixmap(self.label_volume_not_photo)
            self.horizontalSlider_volume.setValue(0)
            self.play_music_control.set_volume(0)
        else:
            self.label_volume.setPixmap(self.label_volume_photo)
            self.horizontalSlider_volume.setValue(self.music_library.setting['volume'])
            self.play_music_control.set_volume(self.music_library.setting['volume'])
        # self.music_library.setting['volume_type'] = not self.music_library.setting['volume_type']
        self.music_library.update()

    def update_volume_size(self,value):
        if value == 0:
            self.label_volume.setPixmap(self.label_volume_not_photo)
            self.music_library.setting['volume_type'] = False
            self.play_music_control.set_volume(0)
        else:
            self.label_volume.setPixmap(self.label_volume_photo)
            self.music_library.setting['volume_type'] = True
            self.play_music_control.set_volume(value)

    def update_volume_storage(self):
        value = self.horizontalSlider_volume.value()
        if value != 0:
            self.music_library.setting['volume'] = value
        self.music_library.update()

    def add_playlist(self):
        dlg = CreatePlaylistDialog()
        if dlg.exec() == QDialog.DialogCode.Accepted:
            title = dlg.get_result()
            # playlist = {'name': title, 'photo': "media/app_photo.png", 'num': 0, 'order': 0}

            # self.music_library.playlist[f'{len(self.music_library.musiclist)}'] = playlist
            self.music_library.SQLiteCursor.execute(self.music_library.insert_playlist_sql,
                                  (title, 0, "media/app_photo.png", 0))

            # self.music_library.musiclist[f'{len(self.music_library.musiclist)}'] = []

            self.music_library.update()

            self.update_playlist_list()

    def update_playlist_list(self):
        self.listWidget_2.clear()
        # 设置上下文菜单策略，允许右键菜单
        self.listWidget_2.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        # 连接右键点击信号到自定义处理函数
        self.listWidget_2.customContextMenuRequested.connect(self.on_playlist_right_click)

        # for k in self.music_library.playlist.keys():
        playlist = self.music_library.get_playlist_list()
        for k in range(len(playlist)):
            if k > 2:
                # i = self.music_library.p[k]
                i = self.music_library.get_playlist(playlist[k])
                item = QtWidgets.QListWidgetItem()
                pm = rounded_pixmap(i['photo'], 40, 4)
                item.setText(i['name'])

                if pm:
                    icon4 = QtGui.QIcon()
                    icon4.addPixmap(pm, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
                    icon4.addPixmap(pm, QtGui.QIcon.Mode.Selected, QtGui.QIcon.State.Off)
                else:
                    icon4 = QtGui.QIcon()
                    icon4.addPixmap(QtGui.QPixmap("media/app_photo.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
                    icon4.addPixmap(QtGui.QPixmap("media/app_photo.png"), QtGui.QIcon.Mode.Selected, QtGui.QIcon.State.Off)
                item.setIcon(icon4)
                self.listWidget_2.addItem(item)
        if self.row > 5:
            self.listWidget_2.setCurrentRow(self.row-6)

    def update_progress_bar(self,value):
        duration_seconds = int(value / 100)
        minutes, seconds = divmod(duration_seconds, 60)
        if minutes < 10:
            minutes = f"0{minutes}"
        time = f"{minutes}:{seconds:02d}"
        self.label_music_time.setText(f"<html><head/><body><p>{time}</p></body></html>")

    def update_progress_bar_play(self):
        self.play_music_control.change_progress(self.horizontalSlider_music_progress_bar.value())
        self.progress_bar = True

    def pause_progress_bar(self):
        self.progress_bar = False

    def display_lyrics_page(self):
        if not self.music_library.setting['id']:
            return

        if not self.lyrics:
            self.lyrics = not self.lyrics
            self.main_page_widget.hide()
            self.lyrics_page_widget.show()
            # self.lyrics_page_widget.display_lyrics()
        else:
            self.lyrics = not self.lyrics
            self.main_page_widget.show()
            self.lyrics_page_widget.hide()

    def search_music_library_music(self):
        text = self.lineEdit_search.text().strip()
        if text:
            search_music_list = self.music_library.music_library_search(text)
            self.listWidget.clearSelection()
            self.listWidget_2.clearSelection()
            self.row = -1
            self.clear_layout(self.verticalLayout_12)
            self.scrollArea_search_music_list = SearchListScrollArea(self.music_library, self.play_music_control, search_music_list, self)
            self.verticalLayout_12.addWidget(self.scrollArea_search_music_list)
            self.scrollArea_music_list = None

    def on_playlist_right_click(self, pos):
        item = self.listWidget_2.itemAt(pos)

        self.delete_row = self.listWidget_2.row(item) + 3

        if item is not None:
            # 将局部坐标转换为全局坐标
            global_pos = self.listWidget_2.mapToGlobal(pos)

            # 添加一点偏移，使菜单不会完全覆盖点击位置
            global_pos.setX(global_pos.x() + 5)
            global_pos.setY(global_pos.y() + 5)

            # 在正确的位置显示菜单
            self.setting_menu.exec(global_pos)

    def update_musiclist(self, sortType):
        if sortType == '删除歌单':
            # self.delete_row
            list_id = self.music_library.get_playlist_list()[self.delete_row]
            # print(self.music_library.get_playlist(list_id))
            self.music_library.delete_list(list_id)
            self.update_playlist_list()
            if self.row-3 == self.delete_row:
                self.update_music_page(self.listWidget.item(0))


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

    def update_play_music(self):
        success = self.label_play_music_photo.setImageSmart(self.music_library.setting['photo'])
        if not success:
            self.label_play_music_photo.setPixmap(QtGui.QPixmap("media/app_photo.png"))

        success = self.lyrics_page_widget.label_play_music_photo.setImageSmart(self.music_library.setting['photo'])
        if not success:
            self.lyrics_page_widget.label_play_music_photo.setPixmap(QtGui.QPixmap("media/app_photo.png"))

        self.label_play_music_name.setText(self.music_library.setting['name'])
        self.lyrics_page_widget.label_play_music_name.setText(
            f"<html><head/><body><p><span style=\" font-size:12pt; font-weight:700;\">{self.music_library.setting['name']}</span></p></body></html>"
        )

        self.label_play_music_signer.setText(
            f"<html><head/><body><p><span style=\" font-size:10pt; color:#787878;\">{self.music_library.setting['singer']}</span></p></body></html>"
        )
        self.lyrics_page_widget.label_play_music_signer.setText(
            f"<html><head/><body><p><span style=\" font-size:12pt; color:#787878;\">{self.music_library.setting['singer']}</span></p></body></html>"
        )

        self.label_play_music_duration.setText(
            f"<html><head/><body><p>{self.music_library.setting['time']}</p></body></html>")
        self.lyrics_page_widget.label_play_music_duration.setText(
            f"<html><head/><body><p>{self.music_library.setting['time']}</p></body></html>")

        if self.music_library.setting['play']:
            self.label_play_music.setPixmap(self.label_play_music_play_photo)
            self.lyrics_page_widget.label_play_music.setPixmap(self.label_play_music_play_photo)
        else:
            self.label_play_music.setPixmap(self.label_play_music_pause_photo)
            self.lyrics_page_widget.label_play_music.setPixmap(self.label_play_music_pause_photo)

        if self.music_library.setting['like']:
            self.label_collection.setPixmap(self.label_collection_red_photo)
        else:
            self.label_collection.setPixmap(self.label_collection_white_photo)

        id = self.music_library.setting['id']
        self.horizontalSlider_music_progress_bar.setMaximum(self.music_library.get_song_by_id(id)['time'])
        self.lyrics_page_widget.horizontalSlider_music_progress_bar.setMaximum(self.music_library.get_song_by_id(id)['time'])