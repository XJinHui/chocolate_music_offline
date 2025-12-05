from PyQt6.QtCore import QObject, QEvent, pyqtSignal, Qt

class HoverClickFilter(QObject):
    hovered = pyqtSignal()          # 悬浮
    left    = pyqtSignal()          # 离开
    clicked = pyqtSignal()          # 左键按下

    def eventFilter(self, obj: QObject, ev: QEvent) -> bool:
        et = ev.type()
        if et == QEvent.Type.Enter:
            self.hovered.emit()
            return True
        if et == QEvent.Type.Leave:
            self.left.emit()
            return True
        if et == QEvent.Type.MouseButtonPress and ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
            return True
        return False