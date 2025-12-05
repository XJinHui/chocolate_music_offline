import sys
import threading
from PyQt6.QtGui import QShortcut, QKeySequence, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt
from MainWindow import Ui_MainWindow
from widget.playlist_management import PlaylistManagement
from pynput import keyboard
# from widget.play_music_control import PlayMusicControl

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        app_icon = QIcon('media/app_icon.ico')
        self.setWindowIcon(app_icon)
        self.ui = Ui_MainWindow()  # 创建UI对象
        self.ui.setupUi(self, music_library)      # 设置UI到主窗口
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.dragging = False
        self.offset = None

        self.is_maximized = False  # 状态标记，默认为非最大化
        self.ui.label_min_filter.clicked.connect(self.showMinimized)
        self.ui.lyrics_page_widget.label_min_filter.clicked.connect(self.showMinimized)

        self.ui.label_close_filter.clicked.connect(self.close)
        self.ui.lyrics_page_widget.label_close_filter.clicked.connect(self.close)

        self.ui.label_max_shrink_filter.clicked.connect(self.toggle_maximize)
        self.ui.lyrics_page_widget.label_max_shrink_filter.clicked.connect(self.toggle_maximize)

        # 创建快捷键，绑定空格键:cite[7]
        self.space_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        self.space_shortcut.activated.connect(self.on_space_pressed)

        # 启动监听
        self.listener = None
        self.start_listener()

    def start_listener(self):
        def on_press(key):
            try:
                # 尝试获取按键名称
                key_name = key.char if hasattr(key, 'char') else str(key)
                # print(f"按键: {key_name}")

                # 检测媒体键
                if key == keyboard.Key.media_play_pause:
                    self.ui.play_music()
                    # print("媒体键: 播放/暂停")
                elif key == keyboard.Key.media_next:
                    self.ui.next_music()
                    # print("媒体键: 下一曲")
                elif key == keyboard.Key.media_previous:
                    self.ui.next_music()
                    # print("媒体键: 上一曲")

            except Exception as e:
                print(f"错误: {str(e)}")

        def on_release(key):
            if key == keyboard.Key.esc:
                # 停止监听
                return False

        # 启动监听线程
        def start_listening():
            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                self.listener = listener
                listener.join()

        thread = threading.Thread(target=start_listening, daemon=True)
        thread.start()

    def toggle_maximize(self):
        """切换窗口的最大化和正常状态"""
        self.ui.update_max_shrink(self.is_maximized)
        if self.is_maximized:
            self.showNormal()  # 恢复窗口
        else:
            self.showMaximized()  # 最大化窗口
        self.is_maximized = not self.is_maximized  # 切换状态标记

    def on_space_pressed(self):
        """空格键按下时执行的操作"""
        self.ui.play_music()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            if self.isMaximized() :
                self.ui.update_max_shrink(self.is_maximized)
                # 从最大化状态恢复
                self.showNormal()
                # self.ui.update_max_button_icon()
                # 强制更新窗口的布局和大小信息
                QApplication.processEvents()

                # 计算新窗口位置：使窗口上半部分中心位于鼠标位置
                cursor_pos = event.globalPosition().toPoint()
                window_rect = self.frameGeometry()
                new_x = cursor_pos.x() - window_rect.width() // 2
                new_y = cursor_pos.y() - window_rect.height() // 16  # 上半部分中心

                window_width = self.width()
                window_height = self.height()
                screen = QApplication.primaryScreen().geometry()

                if new_y < 0:
                    new_y = 0
                elif new_y + window_height > screen.height():
                    new_y = screen.height() - window_height
                if new_x < 0:
                    new_x = 0
                elif new_x + window_width > screen.width():
                    new_x = screen.width() - window_width

                self.move(new_x, new_y)

                # 更新偏移量，确保后续拖动正常
                self.offset = event.globalPosition().toPoint() - self.pos()
                # self.was_maximized = False  # 重置状态
                self.is_maximized = False
            else:
                # 正常拖动逻辑
                self.move(event.globalPosition().toPoint() - self.offset)

    def mouseReleaseEvent(self, event):
        self.dragging = False

    # def keyPressEvent(self, event: QKeyEvent):
    #     """
    #     重写按键按下事件的处理函数。
    #     """
    #     # 检查按下的键是否为媒体播放暂停键
    #     if event.key() == Qt.Key.Key_MediaTogglePlayPause:
    #         self.ui.play_music()
    #         print("播放/暂停")
    #     elif event.key() == Qt.Key.Key_MediaNext:
    #         self.ui.next_music()
    #         print("下一曲")
    #     elif event.key() == Qt.Key.Key_MediaPrevious:
    #         self.ui.previous_music()
    #         print("上一曲")
    #     else:
    #         # 如果不是我们感兴趣的媒体键，调用父类的方法进行默认处理
    #         super().keyPressEvent(event)


if __name__ == "__main__":
    # playlist = [{'id': 1, 'name': '周杰伦', 'photo': "E:/XJH/音乐/XJH/周杰伦 - 说好的幸福呢.flac", 'num': 50}]

    music_library = PlaylistManagement()
    # play_music_control = PlayMusicControl(music_library)

    app = QApplication(sys.argv)
    window = MainWindow()
    # window = MainWindow()
    window.show()
    sys.exit(app.exec())

