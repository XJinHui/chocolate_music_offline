import hashlib
import os
import re
import imghdr
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.wave import WAVE
from mutagen.mp4 import MP4
from mutagen.aac import AAC
from mutagen.easyid3 import EasyID3

album_path = "album"
if not os.path.exists(album_path):
    os.makedirs(album_path)

def calculate_file_hash(file_path, algorithm='sha256'):
    # 创建哈希对象
    hash_func = hashlib.new(algorithm)
    # 以二进制模式打开文件
    with open(file_path, 'rb') as f:
        # 分块读取文件（处理大文件）
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    # 返回哈希值
    return hash_func.hexdigest()


def extract_and_save_cover(audio, file_path, file_name, musiclibrary):
    """从音频文件中提取封面图片并保存到本地"""
    query_photo = "SELECT 1 FROM musiclibrary WHERE photo = ?"
    cover_path = None
    file_ext = os.path.splitext(file_path)[1].lower()

    try:
        if file_ext == '.mp3':
            # MP3文件处理
            if hasattr(audio, 'tags') and audio.tags:
                for tag in audio.tags.values():
                    if isinstance(tag, APIC):
                        cover_data = tag.data
                        # 确定图片格式
                        img_format = imghdr.what(None, h=cover_data)
                        if not img_format:
                            # 如果无法自动检测，尝试使用APIC中的类型描述
                            img_format = tag.mime.split('/')[-1] if tag.mime else 'jpg'

                        cover_path = os.path.join(album_path, f"{file_name}.{img_format}")

                        musiclibrary.execute(query_photo, (cover_path,))
                        if not musiclibrary.fetchone():
                            with open(cover_path, 'wb') as f:
                                f.write(cover_data)
                        return cover_path

        elif file_ext == '.flac':
            # FLAC文件处理
            if audio.pictures:
                picture = audio.pictures[0]
                cover_data = picture.data
                img_format = picture.mime.split('/')[-1] if picture.mime else 'jpg'
                cover_path = os.path.join(album_path, f"{file_name}.{img_format}")

                musiclibrary.execute(query_photo, (cover_path,))
                if not musiclibrary.fetchone():
                    with open(cover_path, 'wb') as f:
                        f.write(cover_data)
                return cover_path

        elif file_ext in ['.m4a', '.mp4']:
            # MP4/AAC文件处理
            if 'covr' in audio.tags:
                cover = audio.tags['covr'][0]
                cover_data = cover
                # MP4封面通常是JPEG或PNG
                img_format = 'jpg'  # 默认
                if len(cover_data) > 4:
                    # 尝试检测图片格式
                    if cover_data[0:4] == b'\x89PNG':
                        img_format = 'png'
                    elif cover_data[0:2] == b'\xff\xd8':
                        img_format = 'jpg'

                cover_path = os.path.join(album_path, f"{file_name}.{img_format}")

                musiclibrary.execute(query_photo, (cover_path,))
                if not musiclibrary.fetchone():
                    with open(cover_path, 'wb') as f:
                        f.write(cover_data)
                return cover_path

        # 其他格式可以类似处理...

    except Exception as e:
        print(f"提取封面图片失败 {file_path}: {e}")

    return cover_path


# def files_import_music(directory_path,list_id):
#     with open('data/musiclist.json', 'r', encoding='utf-8') as f:
#         musiclist = json.load(f)
#
#     list = musiclist[f'{list_id}']
#
#     all_items = os.listdir(directory_path)
#     for item in all_items:
#         extension = os.path.splitext(item)[1].lower()
#         if extension in ['.mp3', '.flac', '.wav', '.aac', '.m4a']:
#             file_path = os.path.join(directory_path, item)
#             metadata = get_audio_metadata(file_path)
#
#             file_hash = calculate_file_hash(file_path)
#
#             cover_path = None
#             try:
#                 # 重新打开文件以提取封面
#                 if extension == '.mp3':
#                     audio = MP3(file_path, ID3=ID3)
#                 elif extension == '.flac':
#                     audio = FLAC(file_path)
#                 elif extension in ['.m4a', '.mp4']:
#                     audio = MP4(file_path)
#                 else:
#                     audio = None
#
#                 if audio:
#                     cover_path = extract_and_save_cover(audio, file_path, file_hash)
#             except Exception as e:
#                 print(f"处理封面图片时出错 {file_path}: {e}")
#
#             data = {
#                 'name': metadata['title'],
#                 'singer': metadata['artist'],
#                 'album': metadata['album'],
#                 'time': int(metadata['duration'] * 100),  # 10毫秒
#                 'photo': cover_path if cover_path else file_path,  # 使用封面图片路径，如果没有则使用文件路径
#                 'like': False,
#                 'id': file_hash,
#                 'path': file_path
#             }
#             list.append(data)
#
#     musiclist[f'{list_id}'] = list
#     # print(musiclist)
#     with open('data/musiclist.json', 'w', encoding='utf-8') as f:
#         f.write(json.dumps(musiclist, ensure_ascii=False, indent=4))
#     num = len(list)
#
#     with open('data/playlist.json', 'r', encoding='utf-8') as f:
#         playlist = json.load(f)
#
#     playlist[f'{list_id}']['num'] = num
#     if list:  # 确保列表不为空
#         playlist[f'{list_id}']['photo'] = list[0]['photo']
#
#     with open('data/playlist.json', 'w', encoding='utf-8') as f:
#         f.write(json.dumps(playlist, ensure_ascii=False, indent=4))



def get_audio_metadata(file_path):
    """
    获取音频文件的元数据信息

    Args:
        file_path (str): 音频文件路径

    Returns:
        dict: 包含音频元数据的字典，包含以下字段：
            - title: 歌曲名称
            - artist: 艺术家
            - album: 专辑名称
            - albumartist: 专辑艺术家
            - album_data: 专辑发行时间
            - duration: 时长（秒）
            - duration_formatted: 格式化后的时长（分:秒）
            - bitrate: 比特率（kbps）
            - sample_rate: 采样率（Hz）
            - channels: 声道数
            - file_size: 文件大小（字节）
            - file_size_formatted: 格式化后的文件大小
            - file_type: 文件类型
            - error: 错误信息（如果有）
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return {"error": f"文件不存在: {file_path}"}

    # 获取文件基本信息
    file_size = os.path.getsize(file_path)
    file_ext = os.path.splitext(file_path)[1].lower()

    # 格式化文件大小
    def format_file_size(size_bytes):
        if size_bytes == 0:
            return "0B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.2f} {size_names[i]}"

    # 初始化元数据字典
    metadata = {
        "title": "未知标题",
        "artist": "未知艺术家",
        "album": "未知专辑",
        "albumartist": '未知专辑艺术家',
        "album_data": "未知发行时间",
        "duration": 0,
        "duration_formatted": "0:00",
        "bitrate": 0,
        "sample_rate": 0,
        "channels": 0,
        "file_size": file_size,
        "file_size_formatted": format_file_size(file_size),
        "file_type": file_ext.upper().replace('.', ''),
        "error": None
    }

    try:
        # 根据文件类型处理
        if file_ext == '.mp3':
            try:
                audio = MP3(file_path, ID3=EasyID3)
                metadata.update({
                    "title": audio.get("title", ["未知标题"])[0],
                    "artist": re.sub(r'[&、]', '/', audio.get("artist", ["未知艺术家"])[0]),
                    "album": audio.get("album", ["未知专辑"])[0],
                    'albumartist': re.sub(r'[&、]', '/', audio.get("albumartist", audio.get("artist", ["未知专辑艺术家"]))[0]),
                    "album_data": audio.get("date", ["未知发行时间"])[0],
                })
            except:
                # 如果EasyID3失败，尝试使用普通ID3
                audio = MP3(file_path)
                if "TIT2" in audio:
                    metadata["title"] = audio["TIT2"].text[0]
                if "TPE1" in audio:
                    metadata["artist"] = re.sub(r'[&、]', '/', audio["TPE1"].text[0])
                if "TALB" in audio:
                    metadata["album"] = audio["TALB"].text[0]
                if "TPE2" in audio:
                    metadata["albumartist"] = re.sub(r'[&、]', '/', audio["TPE2"].text[0])
                if "TDRC" in audio:
                    metadata["album_data"] = audio["TDRC"].text[0]

            metadata.update({
                "duration": audio.info.length,
                "bitrate": audio.info.bitrate // 1000,
                "sample_rate": audio.info.sample_rate,
                "channels": 2  # MP3通常是立体声
            })

        elif file_ext == '.flac':
            audio = FLAC(file_path)
            metadata.update({
                "title": audio.get("title", ["未知标题"])[0],
                "artist": re.sub(r'[&、]', '/', audio.get("artist", ["未知艺术家"])[0]),
                "album": audio.get("album", ["未知专辑"])[0],
                'albumartist': re.sub(r'[&、]', '/', audio.get("albumartist", audio.get("artist", ["未知专辑艺术家"]))[0]),
                "album_data": audio.get("date", ["未知发行时间"])[0],
                "duration": audio.info.length,
                "bitrate": audio.info.bitrate // 1000,
                "sample_rate": audio.info.sample_rate,
                "channels": audio.info.channels
            })

        elif file_ext in ['.wav', '.wave']:
            audio = WAVE(file_path)
            metadata.update({
                "duration": audio.info.length,
                "bitrate": audio.info.bitrate // 1000,
                "sample_rate": audio.info.sample_rate,
                "channels": audio.info.channels
            })

        elif file_ext in ['.m4a', '.mp4']:
            audio = MP4(file_path)
            metadata.update({
                "title": audio.get("\xa9nam", ["未知标题"])[0],
                "artist": re.sub(r'[&、]', '/',audio.get("\xa9ART", ["未知艺术家"])[0]),
                "album": audio.get("\xa9alb", ["未知专辑"])[0],
                'albumartist': re.sub(r'[&、]', '/',audio.get("\xa9aab", audio.get("\xa9ART", ["未知专辑艺术家"]))[0]),
                "album_data": audio.get("\xa9day", ["未知发行时间"])[0],
                "duration": audio.info.length,
                "bitrate": audio.info.bitrate // 1000,
                "sample_rate": audio.info.sample_rate,
                "channels": 2  # M4A通常是立体声
            })

        elif file_ext == '.aac':
            audio = AAC(file_path)
            metadata.update({
                "duration": audio.info.length,
                "bitrate": audio.info.bitrate // 1000,
                "sample_rate": audio.info.sample_rate,
                "channels": 2  # AAC通常是立体声
            })

        else:
            return {"error": f"不支持的文件类型: {file_ext}"}

        # 格式化时长
        duration_seconds = int(metadata["duration"])
        minutes, seconds = divmod(duration_seconds, 60)
        metadata["duration_formatted"] = f"{minutes}:{seconds:02d}"

    except Exception as e:
        metadata["error"] = f"读取元数据时出错: {str(e)}"

    return metadata

if __name__ == '__main__':
    directory_path = 'E:\XJH\音乐\XJH'
    all_items = os.listdir(directory_path)
    for item in all_items:
        extension = os.path.splitext(item)[1].lower()
        if extension in ['.mp3', '.flac', '.wav', '.aac', '.m4a']:
            file_path = os.path.join(directory_path, item)
            data = get_audio_metadata(file_path)
            print(data['albumartist'], data['album_data'])