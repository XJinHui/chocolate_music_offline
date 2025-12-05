from PyQt6.QtGui import QPixmap, QPainter, QPainterPath
from PyQt6.QtCore import Qt, QRect, QRectF
import os
from mutagen import File
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
import base64


def rounded_pixmap(file_path: str, size: int, radius: int) -> QPixmap:
    """返回 size×size 的圆角 pixmap（4 角都是圆的），支持音频文件和图片文件"""
    src = QPixmap()
    if os.path.exists(file_path):
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
            src.load(file_path)
        elif file_path.lower().endswith(('.mp3', '.flac', '.wav', '.aiff', '.ogg', '.m4a', '.mp4', '.opus')):
            cover_data = None
            try:
                if file_path.lower().endswith('.flac'):
                    audio = FLAC(file_path)
                    if audio.pictures:
                        cover_data = audio.pictures[0].data
                elif file_path.lower().endswith('.mp3'):
                    audio = MP3(file_path, ID3=ID3)
                    if audio.tags:
                        for tag in audio.tags.values():
                            if isinstance(tag, APIC):
                                cover_data = tag.data
                                break
                elif file_path.lower().endswith(('.m4a', '.mp4')):
                    audio = MP4(file_path)
                    if 'covr' in audio.tags:
                        cover_data = audio.tags['covr'][0]
                elif file_path.lower().endswith(('.ogg', '.opus')):
                    if file_path.lower().endswith('.opus'):
                        audio = OggOpus(file_path)
                    else:
                        audio = OggVorbis(file_path)

                    # 尝试从metadata_block_picture获取
                    if 'metadata_block_picture' in audio.tags:
                        block_data = audio.tags['metadata_block_picture'][0]
                        from mutagen.flac import Picture
                        picture = Picture(base64.b64decode(block_data))
                        cover_data = picture.data
                    # 尝试从封面艺术标签获取
                    elif 'coverart' in audio.tags:
                        cover_data = base64.b64decode(audio.tags['coverart'][0])
                else:
                    # 通用处理
                    audio = File(file_path)
                    if hasattr(audio, 'tags') and audio.tags:
                        # 尝试常见封面标签
                        for cover_tag in ['covr', 'APIC', 'coverart', 'metadata_block_picture']:
                            if cover_tag in audio.tags:
                                if cover_tag == 'metadata_block_picture':
                                    block_data = audio.tags[cover_tag][0]
                                    from mutagen.flac import Picture
                                    picture = Picture(base64.b64decode(block_data))
                                    cover_data = picture.data
                                else:
                                    cover_data = audio.tags[cover_tag][0]
                                break

                if cover_data:
                    src.loadFromData(cover_data)
            except Exception as e:
                print(f"Error extracting cover from {file_path}: {e}")
                return False

    if src.isNull():
        return False

    # 裁剪为正方形
    src_sz = src.size()
    side = min(src_sz.width(), src_sz.height())
    rect = QRect((src_sz.width() - side) // 2,
                 (src_sz.height() - side) // 2,
                 side, side)
    src = src.copy(rect)

    # 缩放到目标尺寸
    src = src.scaled(size, size,
                     Qt.AspectRatioMode.IgnoreAspectRatio,
                     Qt.TransformationMode.FastTransformation)

    # 创建圆角效果
    dst = QPixmap(size, size)
    dst.fill(Qt.GlobalColor.transparent)
    painter = QPainter(dst)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(QRectF(dst.rect()), radius, radius)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, src)
    painter.end()
    return dst


# def load_default_pixmap(size: int) -> QPixmap:
#     """从默认路径加载图片，不进行圆角处理"""
#     default_path = "media/app_photo.png"
#
#     # 尝试加载默认图片
#     default_pixmap = QPixmap(default_path)
#
#     # 如果默认图片不存在，创建一个简单的灰色方形图片
#     if default_pixmap.isNull():
#         dst = QPixmap(size, size)
#         dst.fill(Qt.GlobalColor.darkGray)
#         return dst
#
#     # 如果默认图片存在，直接缩放并返回（不进行圆角处理）
#     return default_pixmap.scaled(size, size,
#                                  Qt.AspectRatioMode.IgnoreAspectRatio,
#                                  Qt.TransformationMode.SmoothTransformation)