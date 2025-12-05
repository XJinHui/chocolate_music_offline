from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath
from PyQt6.QtCore import Qt, QRectF
from mutagen import File
from mutagen.id3 import APIC
import os


class RoundImageLabel(QLabel):
    def __init__(self, radius=20, parent=None):
        super().__init__(parent)
        self._radius = radius
        self._src = QPixmap()
        self.setMinimumSize(40, 40)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # 外部调用：智能设置图片 - 自动判断文件类型
    def setImageSmart(self, file_path: str):
        """
        智能设置图片，根据文件扩展名自动判断是图片文件还是音频文件
        并相应地显示图片或从音频文件中提取专辑图片
        """
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return False

        # 获取文件扩展名并转换为小写
        ext = os.path.splitext(file_path)[1].lower()

        # 图片文件扩展名列表
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp', '.svg']

        # 音频文件扩展名列表
        audio_extensions = ['.mp3', '.flac', '.fla', '.m4a', '.mp4', '.ogg', '.oga', '.wma', '.ape', '.wav', '.aiff',
                            '.aif', '.opus', '.mpc']

        if ext in image_extensions:
            # 如果是图片文件，直接加载
            return self.setImage(file_path)
        elif ext in audio_extensions:
            # 如果是音频文件，尝试提取专辑图片
            return self.setImageFromAudio(file_path)
        else:
            print(f"不支持的文件类型: {file_path} (扩展名: {ext})")
            return False

    # 外部调用：从文件路径设置图像
    def setImage(self, path: str):
        try:
            self._src = QPixmap(path)
            self.update()
            return True
        except Exception as e:
            print(f"加载图片失败: {e}")
            return False

    # 外部调用：从QPixmap设置图像
    def setPixmap(self, pixmap: QPixmap):
        self._src = pixmap
        self.update()

    # 外部调用：从音频文件提取专辑图片 (支持多种格式)
    def setImageFromAudio(self, audio_path: str):
        try:
            # 使用mutagen的通用File接口尝试读取文件
            audio = File(audio_path)
            if audio is None:
                print(f"不支持的音频格式: {audio_path}")
                return False

            # 尝试提取图片
            return self._extract_image(audio, audio_path)

        except Exception as e:
            print(f"从音频文件提取图片失败 {audio_path}: {e}")
            return False

    # 通用图片提取方法
    def _extract_image(self, audio, audio_path):
        # 尝试从不同格式提取图片
        if hasattr(audio, 'tags') and audio.tags:
            # MP3格式
            if audio_path.lower().endswith('.mp3'):
                return self._extract_from_mp3(audio)

            # FLAC格式
            elif audio_path.lower().endswith(('.flac', '.fla')):
                return self._extract_from_flac(audio)

            # MP4/AAC格式
            elif audio_path.lower().endswith(('.m4a', '.mp4')):
                return self._extract_from_mp4(audio)

            # OGG Vorbis格式
            elif audio_path.lower().endswith(('.ogg', '.oga')):
                return self._extract_from_ogg(audio)

            # WMA格式
            elif audio_path.lower().endswith('.wma'):
                return self._extract_from_wma(audio)

        # 如果以上都不适用，尝试通用的图片查找
        return self._extract_generic(audio)

    # 从MP3提取图片
    def _extract_from_mp3(self, audio):
        for tag in audio.tags.values():
            if isinstance(tag, APIC):
                return self._load_pixmap_from_data(tag.data)
        return False

    # 从FLAC提取图片
    def _extract_from_flac(self, audio):
        if audio.pictures:
            picture = audio.pictures[0]
            return self._load_pixmap_from_data(picture.data)
        return False

    # 从MP4/AAC提取图片
    def _extract_from_mp4(self, audio):
        if 'covr' in audio.tags:
            cover = audio.tags['covr'][0]
            return self._load_pixmap_from_data(cover)
        return False

    # 从OGG Vorbis提取图片
    def _extract_from_ogg(self, audio):
        if 'metadata_block_picture' in audio.tags:
            picture_data = audio.tags['metadata_block_picture'][0]
            # 这里需要解码base64，但mutagen应该已经处理了
            return self._load_pixmap_from_data(picture_data)
        return False

    # 从WMA提取图片
    def _extract_from_wma(self, audio):
        if 'WM/Picture' in audio.tags:
            picture = audio.tags['WM/Picture'][0]
            return self._load_pixmap_from_data(picture.data)
        return False

    # 通用图片提取方法
    def _extract_generic(self, audio):
        # 尝试查找常见的图片标签
        for tag_name in ['APIC:', 'covr', 'metadata_block_picture', 'WM/Picture']:
            if hasattr(audio, 'tags') and tag_name in audio.tags:
                picture_data = audio.tags[tag_name][0]
                if hasattr(picture_data, 'data'):
                    return self._load_pixmap_from_data(picture_data.data)
                else:
                    return self._load_pixmap_from_data(picture_data)
        return False

    # 从二进制数据加载图片
    def _load_pixmap_from_data(self, data):
        try:
            pixmap = QPixmap()
            if hasattr(data, 'data'):  # 如果数据有.data属性（如MP4Cover）
                success = pixmap.loadFromData(data.data)
            else:
                success = pixmap.loadFromData(data)

            if success and not pixmap.isNull():
                self._src = pixmap
                self.update()
                return True
            return False
        except Exception as e:
            print(f"从数据加载图片失败: {e}")
            return False

    # 为了向后兼容，保留setImageFromMP3方法
    # def setImageFromMP3(self, mp3_path: str):
    #     print("Warning: setImageFromMP3 is deprecated. Use setImageFromAudio instead.")
    #     return self.setImageFromAudio(mp3_path)

    # 外部调用：改圆角
    def setRadius(self, r: int):
        self._radius = r
        self.update()

    # 外部调用：清空图像
    def clearImage(self):
        self._src = QPixmap()
        self.update()

    # 核心：自绘
    def paintEvent(self, ev):
        if self._src.isNull():
            super().paintEvent(ev)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 计算"缩放后仍保持比例"的矩形
        pm_size = self._src.size()
        pm_ratio = pm_size.width() / max(pm_size.height(), 1)
        wg_size = self.size()

        if wg_size.width() / wg_size.height() > pm_ratio:
            h = wg_size.height()
            w = int(h * pm_ratio)
        else:
            w = wg_size.width()
            h = int(w / pm_ratio)

        x = (wg_size.width() - w) // 2
        y = (wg_size.height() - h) // 2
        target_rect = QRectF(x, y, w, h)

        # 生成圆角路径
        path = QPainterPath()
        path.addRoundedRect(target_rect, self._radius, self._radius)

        # 裁剪 + 绘制
        painter.setClipPath(path)
        painter.drawPixmap(target_rect, self._src, QRectF(self._src.rect()))
        painter.end()

    # 检查是否有有效图像
    def hasImage(self):
        return not self._src.isNull()