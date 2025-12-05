from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal
from PyQt6 import QtCore, QtGui, QtSvg


class SettingMusiclistMenu(QMenu):
    sortChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initActions()  # 初始化菜单项

    def initActions(self):
        self.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 10px;
                padding: 8px 0;
                font-size: 12px;
            }

            QMenu::item {
                padding: 8px 10px 8px 10px;
                color: #222222;
                background-color: transparent;
                border-radius: 8px;
                margin: 0 8px;
            }

            QMenu::item:selected {
                background-color: #f0f0f0;
            }

            QMenu::icon {
                padding-right: 12px;
            }

            QMenu::separator {
                height: 1px;
                background: #e0e0e0;
                margin: 3px 6px;
            }
        """)

        self.delete_list = QAction(self.load_svg_icon("media/trash.svg"), "删除歌单")
        self.addAction(self.delete_list)
        self.delete_list.triggered.connect(self._onActionTriggered)

    def _onActionTriggered(self):
        """处理Action触发：取消其他选项的选中状态，发射当前排序类型"""
        sender_action = self.sender()
        self.sortChanged.emit(sender_action.text())

    def load_svg_icon(self, svg_path, width=60, height=60):
        renderer = QtSvg.QSvgRenderer(svg_path)
        pixmap = QtGui.QPixmap(width, height)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)  # 设置透明背景
        painter = QtGui.QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return QtGui.QIcon(pixmap)