from PyQt6.QtWidgets import QMenu
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction

class OrderMenu(QMenu):
    sortChanged = pyqtSignal(str)

    def __init__(self, order, parent=None):
        super().__init__(parent)
        self.order = order
        self.initActions()  # 初始化菜单项

    def initActions(self):
        self.setStyleSheet("""
            /* 菜单整体样式 */
            QMenu {
                background-color: #ffffff;  /* 菜单背景色 */
                border: 1px solid #ddd;     /* 边框 */
                border-radius: 10px;         /* 圆角 */
                padding: 6px 0;             /* 内边距（上下0，左右4） */
            }

            /* 菜单项样式 */
            QMenu::item {
                padding: 6px 24px;  /* 内边距（上下6，左右24） */
                color: #333;        /* 文字颜色 */
                background-color: transparent;  /* 默认背景透明 */
                margin: 0 6px;
            }

            /* 菜单项悬停状态 */
            QMenu::item:selected {
                background-color: #f5f5f5;  /* 悬停背景色 */
                border-radius: 8px;
                color: rgb(53,193,255);
            }

            /* 菜单项选中（勾选）状态 */
            QMenu::item:checked {
                color: rgb(53,193,255);             /* 选中文字色 */
            }

            /* 勾选标记样式（可选） */
            QMenu::indicator {
                width: 6px;   /* 勾选框宽度 */
                height: 16px;  /* 勾选框高度 */
            }
            QMenu::indicator:checked {
                image: url();  /* 可替换为自定义勾选图标 */
            }
        """)

        # 1. 创建所有排序选项的QAction（设置为“可检查”，实现单选效果）
        self.defaultAction = QAction("默认排序", self, checkable=True)
        self.addTimeAction = QAction("添加时间", self, checkable=True)
        self.songNameAction = QAction("歌曲名", self, checkable=True)
        self.singerAction = QAction("歌手", self, checkable=True)
        self.albumAction = QAction("专辑", self, checkable=True)
        # self.durationAction = QAction("时长", self, checkable=True)
        # self.playCountAction = QAction("播放次数", self, checkable=True)
        # self.randomAction = QAction("随机排序", self, checkable=True)

        # 2. 将所有Action添加到菜单中
        self.addAction(self.defaultAction)
        self.addAction(self.addTimeAction)
        self.addAction(self.songNameAction)
        self.addAction(self.singerAction)
        self.addAction(self.albumAction)
        # self.addAction(self.durationAction)
        # self.addAction(self.playCountAction)
        # self.addAction(self.randomAction)

        # 3. 设置“默认排序”为初始选中状态
        if self.order == 0:
            self.defaultAction.setChecked(True)
        elif self.order == 1:
            self.addTimeAction.setChecked(True)
        elif self.order == 2:
            self.songNameAction.setChecked(True)
        elif self.order == 3:
            self.singerAction.setChecked(True)
        elif self.order == 4:
            self.albumAction.setChecked(True)

        # 4. 为每个Action连接触发事件（统一处理单选和信号发射）
        self.defaultAction.triggered.connect(self._onActionTriggered)
        self.addTimeAction.triggered.connect(self._onActionTriggered)
        self.songNameAction.triggered.connect(self._onActionTriggered)
        self.singerAction.triggered.connect(self._onActionTriggered)
        self.albumAction.triggered.connect(self._onActionTriggered)
        # self.durationAction.triggered.connect(self._onActionTriggered)
        # self.playCountAction.triggered.connect(self._onActionTriggered)
        # self.randomAction.triggered.connect(self._onActionTriggered)

    def _onActionTriggered(self):
        """处理Action触发：取消其他选项的选中状态，发射当前排序类型"""
        sender_action = self.sender()  # 获取触发的Action
        for action in self.actions():
            if action.isCheckable():
                # 仅保留当前触发的Action为选中，其余取消
                action.setChecked(action == sender_action)

        # 发射信号，传递当前选中的排序类型（Action的文本）
        self.sortChanged.emit(sender_action.text())