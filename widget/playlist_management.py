import json
import re
import sqlite3
import time
from pypinyin import lazy_pinyin
from .files_import_music import *
from .music_search_engine import *

class PlaylistManagement():

    insert_music_sql = """
        INSERT OR IGNORE INTO musiclibrary (
            id, name, singer, album, albumartist, album_data,
            time, photo, like, path, storage_time, name_pinyin,
            singer_pinyin, album_pinyin
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    insert_playlist_sql = """
        INSERT OR IGNORE INTO playlist (
            name, num, photo, sort_order
        ) VALUES (?, ?, ?, ?)
        """
    insert_musiclist_sql = """
        INSERT OR IGNORE INTO musiclist (
            list_id, id, time
        ) VALUES (?, ?, ?)
        """
    delete_playlist_sql = "DELETE FROM playlist WHERE list_id = ?"
    delete_musiclist_sql = "DELETE FROM musiclist WHERE list_id = ? AND id = ?"

    def __init__(self):
        if not os.path.exists('album'):
            os.makedirs("album")
        if not os.path.exists('author'):
            os.makedirs("author")
        if not os.path.exists('data'):
            os.makedirs('data')

        if not os.path.exists('data/setting.json'):
            self.setting = {'name': '', 'singer': '',
                       'time': '00:00', 'like': False, 'photo': "media/app_photo.png", 'id': 0,
                       'play_type': 0, 'volume': 100, 'volume_type': True, 'play': False,
                       'play_list_id': -1}
            with open('data/setting.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.setting, ensure_ascii=False, indent=4))
        else:
            with open('data/setting.json', 'r', encoding='utf-8') as f:
                self.setting = json.load(f)
                self.setting['play'] = True

        self.open_SQLite()

        self.search_engine = MusicSearchEngine(self.SQLiteCursor)

    def open_SQLite(self):
        self.conn = sqlite3.connect('data/musiclibrary.db')
        self.SQLiteCursor = self.conn.cursor()

        tables_exist = all([
            self.check_table_exists('musiclibrary'),
            self.check_table_exists('playlist'),
            self.check_table_exists('musiclist')
        ])

        if tables_exist:
            # print("所有表已存在，跳过创建过程")
            return

        self.SQLiteCursor.execute("""
                    CREATE TABLE IF NOT EXISTS musiclibrary (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        singer TEXT NOT NULL,
                        album TEXT,
                        albumartist TEXT,
                        album_data TEXT,
                        time INTEGER,
                        photo TEXT,
                        like INTEGER,
                        path TEXT NOT NULL,
                        storage_time REAL,
                        name_pinyin TEXT,
                        singer_pinyin TEXT,
                        album_pinyin TEXT
                    )
                """)

        self.SQLiteCursor.execute("""
                        CREATE TABLE IF NOT EXISTS playlist (
                            list_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            num INTEGER,
                            photo TEXT,
                            sort_order  INTEGER
                        )
                    """)

        self.SQLiteCursor.execute("""
                            CREATE TABLE IF NOT EXISTS musiclist (
                                list_id INTEGER NOT NULL,
                                id TEXT NOT NULL,
                                time INTEGER,
                                FOREIGN KEY (list_id) REFERENCES playlist(list_id) ON DELETE CASCADE,
                                FOREIGN KEY (id) REFERENCES musiclibrary(id) ON DELETE CASCADE,
                                UNIQUE(list_id, id)
                            )
                        """)

        insert_playlist_sql = """
                INSERT OR IGNORE INTO playlist (
                    list_id, name, num, photo, sort_order
                ) VALUES (?, ?, ?, ?, ?)
                """

        self.SQLiteCursor.execute(insert_playlist_sql,
                                  (0, '我喜欢', 0, "media/collection_photo.png", 0))
        self.SQLiteCursor.execute(insert_playlist_sql,
                                  (1, '专辑', 0, "media/app_photo.png", 0))
        self.SQLiteCursor.execute(insert_playlist_sql,
                                  (2, '歌手', 0, "media/app_photo.png", 0))

        self.conn.commit()

    def check_table_exists(self, table_name):
        """检查表是否存在"""
        self.SQLiteCursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return self.SQLiteCursor.fetchone() is not None

    def update(self):
        with open('data/setting.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.setting, ensure_ascii=False, indent=4))

        self.conn.commit()

    def files_import_music(self, directory_path, list_id):
        query_id = "SELECT 1 FROM musiclibrary WHERE id = ?"

        playlist_photo = ''
        all_items = os.listdir(directory_path)
        for item in all_items:
            extension = os.path.splitext(item)[1].lower()
            if extension in ['.mp3', '.flac', '.wav', '.aac', '.m4a']:

                r = re.match('(.*)(\..*)', item)
                name_r = re.match('(.*)-(.*)', r.group(1))
                if name_r:
                    singer = name_r.group(1).strip()
                    name = name_r.group(2).strip()
                else:
                    name = r.group(1)
                    singer = '未知艺术家'

                file_path = os.path.join(directory_path, item)
                metadata = get_audio_metadata(file_path)

                album_naming = f'{metadata['album']}-{metadata['albumartist']}-{metadata['album_data']}'
                album_naming = re.sub(r'[<>:\"/\\|?*]', '', album_naming)
                file_hash = calculate_file_hash(file_path)

                cover_path = None
                try:
                    # 重新打开文件以提取封面
                    if extension == '.mp3':
                        audio = MP3(file_path, ID3=ID3)
                    elif extension == '.flac':
                        audio = FLAC(file_path)
                    elif extension in ['.m4a', '.mp4']:
                        audio = MP4(file_path)
                    else:
                        audio = None

                    if audio:
                        cover_path = extract_and_save_cover(audio, file_path, album_naming, self.SQLiteCursor)
                except Exception as e:
                    print(f"处理封面图片时出错 {file_path}: {e}")

                if not playlist_photo:
                    playlist_photo = cover_path if cover_path else 'media/app_photo.png'

                data = {
                    'name': metadata['title'] if metadata['title'] != '未知标题' else name,
                    'singer': metadata['artist'] if metadata['artist'] != "未知艺术家" else singer,
                    'album': metadata['album'],
                    'albumartist': metadata['albumartist'],
                    'album_data': metadata['album_data'],
                    'time': int(metadata['duration'] * 100),  # 10毫秒
                    'photo': cover_path if cover_path else 'media/app_photo.png',  # 使用封面图片路径，如果没有则使用文件路径
                    'like': 0,
                    'id': file_hash,
                    'path': file_path,
                    'storage_time': os.path.getmtime(file_path)
                }

                self.SQLiteCursor.execute(query_id, (file_hash,))
                name_pinyin = ''.join(lazy_pinyin(data['name']))
                singer_pinyin = ''.join(lazy_pinyin(data['singer']))
                album_pinyin = ''.join(lazy_pinyin(data['album']))
                if not self.SQLiteCursor.fetchone():
                    self.SQLiteCursor.execute(self.insert_music_sql,(
                        data['id'], data['name'], data['singer'], data['album'], data['albumartist'],
                        data['album_data'], data['time'], data['photo'], data['like'], data['path'],
                        data['storage_time'], name_pinyin, singer_pinyin, album_pinyin
                    ))

                self.SQLiteCursor.execute(self.insert_musiclist_sql,
                                          (list_id, data['id'], data['storage_time']))

        self.unification_album_artist()

        self.update_playlist(list_id)

        self.update()

    def unification_album_artist(self):
        datas = self.get_all_music()
        album = {}
        for i in datas:
            if i['album'] not in album:
                album[i['album']] = [{
                    'albumartist': i['albumartist'],
                    'album_data': i['album_data'],
                    'photo': i['photo']
                }]
            else:
                for j in album[i['album']]:
                    if j['album_data'] == i['album_data']:
                        if j['albumartist'] == i['albumartist'] or j['albumartist'] in i['albumartist']:
                            if j['photo'] == 'media/app_photo.png':
                                j['photo'] = i['photo']
                            break

                        if i['albumartist'] in j['albumartist']:
                            j['albumartist'] = i['albumartist']
                            if i['photo'] != 'media/app_photo.png':
                                j['photo'] = i['photo']
                            break
                    if j == album[i['album']][-1]:
                        album[i['album']].append({
                            'albumartist': i['albumartist'],
                            'album_data': i['album_data'],
                            'photo': i['photo']
                        })

        for i in datas:
            album_data = album[i['album']]
            for j in album_data:
                if j['albumartist'] in i['albumartist'] and j['album_data'] == i['album_data']:
                    i['albumartist'] = j['albumartist']
                    if i['photo'] != j['photo']:
                        if os.path.exists(i['photo']) and i['photo'] != 'media/app_photo.png':
                            # Delete the file
                            os.remove(i['photo'])
                        i['photo'] = j['photo']
                    break
        for i in datas:
            self.SQLiteCursor.execute("UPDATE musiclibrary SET albumartist = ?, photo = ? WHERE id = ?", (i['albumartist'], i['photo'], i['id']))


    def update_playlist(self, list_id):
        musiclist = self.get_musiclist(list_id)
        num = len(musiclist)

        if num:
            photo = self.get_song_by_id(musiclist[0])['photo']
            self.SQLiteCursor.execute(f"UPDATE playlist SET num = ?, photo = ? WHERE list_id = ?", (num, photo, list_id))

    def update_playlist_music_num(self, list_id ,add):
        self.SQLiteCursor.execute("SELECT * FROM playlist WHERE list_id = ?", (list_id,))
        playlist_data = self.SQLiteCursor.fetchone()
        num = playlist_data[2]
        if add:
            num += 1
        else:
            num -= 1
        self.SQLiteCursor.execute(f"UPDATE playlist SET num = ? WHERE list_id = ?", (num, list_id))

    def music_sqlite_to_json(self, result):
        data = {
            'id': result[0],
            'name': result[1],
            'singer': result[2],
            'album': result[3],
            'albumartist': result[4],
            'album_data': result[5],
            'time': result[6],
            'photo': result[7],
            'like': result[8],
            'path': result[9],
            'storage_time': result[10]
        }

        return data

    def playlist_sqlite_to_json(self, result):
        data = {
            'list_id': result[0],
            'name': result[1],
            'num': result[2],
            'photo': result[3],
            'order': result[4]
        }

        return data


    def get_song_by_id(self, target_id):
        """根据id查找单首歌（精确匹配，唯一结果）"""
        query_id = "SELECT * FROM musiclibrary WHERE id = ?"
        self.SQLiteCursor.execute(query_id, (target_id,))
        result = self.SQLiteCursor.fetchone()
        data = self.music_sqlite_to_json(result)

        return data

    def get_songs_by_name(self, target_name):
        """根据歌名查找歌曲（可能返回多首）"""
        query_name = "SELECT * FROM musiclibrary WHERE name = ?"
        self.SQLiteCursor.execute(query_name, (target_name,))
        result = self.SQLiteCursor.fetchall()
        data = []
        for i in result:
            data.append(self.music_sqlite_to_json(i))

        return data

    def get_songs_by_singer(self, target_singer):
        """根据歌手查找歌曲（可能返回多首）"""
        query_singer = "SELECT * FROM musiclibrary WHERE LOWER(singer) LIKE LOWER(?)"
        self.SQLiteCursor.execute(query_singer, (f'%{target_singer}%',))  # 通配符%表示包含目标歌手
        result = self.SQLiteCursor.fetchall()
        data = []
        for item in result:
            data.append(self.music_sqlite_to_json(item))

        return data

    def get_songs_by_album(self, target_album):
        """根据专辑查找歌曲（可能返回多首）"""
        query_album = "SELECT * FROM musiclibrary WHERE album = ?"
        self.SQLiteCursor.execute(query_album, (target_album,))
        result = self.SQLiteCursor.fetchall()
        data = []
        for i in result:
            data.append(self.music_sqlite_to_json(i))

        return data

    def get_all_singers(self):
        """获取所有歌手"""
        query_singers = """
            SELECT DISTINCT singer 
            FROM musiclibrary 
            WHERE singer IS NOT NULL AND singer != ''
            ORDER BY singer
        """
        self.SQLiteCursor.execute(query_singers)
        result = self.SQLiteCursor.fetchall()
        data = []
        for i in result:
            data.append(i[0])

        return data

    def get_all_albums(self):
        """获取所有专辑"""
        query_albums = """
            SELECT DISTINCT album, albumartist
            FROM musiclibrary 
            WHERE album IS NOT NULL AND album != ''
            ORDER BY album
        """
        self.SQLiteCursor.execute(query_albums)
        result = self.SQLiteCursor.fetchall()
        data = []
        for i in result:
            data.append(i[0])
        return data

    def get_all_music(self):
        """获取所有歌曲"""
        query_music = "SELECT * FROM musiclibrary"
        self.SQLiteCursor.execute(query_music)
        result = self.SQLiteCursor.fetchall()
        data = []
        for i in result:
            data.append(self.music_sqlite_to_json(i))
        return data

    def get_playlist_list(self):
        query_playlist = "SELECT * FROM playlist ORDER BY list_id ASC"
        self.SQLiteCursor.execute(query_playlist)
        result = self.SQLiteCursor.fetchall()
        data = []
        for i in result:
            data.append(i[0])
        data.sort()
        return data

    def get_playlist(self, list_id):
        self.SQLiteCursor.execute("SELECT * FROM playlist WHERE list_id = ?", (list_id,))
        result = self.SQLiteCursor.fetchone()
        data = self.playlist_sqlite_to_json(result)
        return data

    def get_musiclist(self, list_id):
        self.SQLiteCursor.execute("SELECT * FROM playlist WHERE list_id = ?", (list_id,))
        playlist_data = self.SQLiteCursor.fetchone()

        # 修复2：添加空值检查
        if not playlist_data:
            return []

        order = playlist_data[4]  # sort_order 是第5列

        order_mapping = {
            0: "musiclist.time DESC",
            1: "musiclist.time ASC",
            2: "musiclibrary.name_pinyin ASC",
            3: "musiclibrary.singer_pinyin ASC",
            4: "musiclibrary.album_pinyin ASC"
        }

        order_by = order_mapping.get(order, "musiclist.time DESC")  # 默认排序

        query_musiclist = f"""
            SELECT musiclist.*, musiclibrary.* 
            FROM musiclist
            JOIN musiclibrary ON musiclist.id = musiclibrary.id 
            WHERE musiclist.list_id = ? 
            ORDER BY {order_by}
        """

        self.SQLiteCursor.execute(query_musiclist, (list_id,))
        result = self.SQLiteCursor.fetchall()
        data = []
        for i in result:
            data.append(i[1])
        return data

    def update_like(self, id, like):
        if like:
            self.SQLiteCursor.execute(f"UPDATE musiclibrary SET like = ? WHERE id = ?", (1, id))
        else:
            self.SQLiteCursor.execute(f"UPDATE musiclibrary SET like = ? WHERE id = ?", (0, id))

    def is_or_no_like(self, id):
        query_id = "SELECT 1 FROM musiclist WHERE list_id = ? AND id = ?"
        self.SQLiteCursor.execute(query_id, (0, id))

        if not self.SQLiteCursor.fetchone():
            self.SQLiteCursor.execute(self.insert_musiclist_sql, (0, id, time.time()))
            self.update_playlist_music_num(0, True)
        else:
            self.SQLiteCursor.execute(self.delete_musiclist_sql, (0, id))
            self.update_playlist_music_num(0, False)
        self.update()

    def add_music(self, id, list_id):
        query_id = "SELECT 1 FROM musiclist WHERE list_id = ? AND id = ?"
        self.SQLiteCursor.execute(query_id, (list_id, id))
        if not self.SQLiteCursor.fetchone():

            if list_id == 0:
                self.SQLiteCursor.execute(f"UPDATE musiclibrary SET like = ? WHERE id = ?", (1, id))

            self.SQLiteCursor.execute(self.insert_musiclist_sql, (list_id, id, time.time()))

            self.update_playlist_music_num(list_id, True)

            if list_id != 0:
                self.update_playlist(list_id)

            self.update()
        else:
            print('歌曲已存在')

    def delete_music(self, id, list_id):
        self.SQLiteCursor.execute(self.delete_musiclist_sql, (list_id, id))
        self.update_playlist(list_id)
        self.update()

    def delete_list(self, list_id):
        delete_musiclist_sql = "DELETE FROM musiclist WHERE list_id = ?"
        self.SQLiteCursor.execute(self.delete_playlist_sql, (list_id,))
        self.SQLiteCursor.execute(delete_musiclist_sql, (list_id,))
        self.update()

    def update_play_music(self, id, list_id):
        data = self.get_song_by_id(id)

        duration_seconds = int(data["time"] / 100)
        minutes, seconds = divmod(duration_seconds, 60)
        if minutes < 10:
            minutes = f"0{minutes}"
        time = f"{minutes}:{seconds:02d}"

        self.setting['photo'] = data['photo']
        self.setting['name'] = data['name']
        self.setting['singer'] = data['singer']
        self.setting['time'] = time
        self.setting['id'] = data['id']
        self.setting['like'] = data['like']
        self.setting['play'] = True
        if list_id != -1:
            self.setting['play_list_id'] = list_id

        self.update()

    def list_search(self, list_id, keyword):
        list = self.get_musiclist(list_id)

        datas = []
        keyword = keyword.lower()
        for i in range(len(list)):
            data = self.get_song_by_id(list[i])
            if keyword in data['name'].lower() or keyword in data['singer'].lower() or keyword in data['album'].lower():
                datas.append(data)

        self.SQLiteCursor.execute("SELECT * FROM playlist WHERE list_id = ?", (list_id,))
        playlist_data = self.SQLiteCursor.fetchone()

        # 修复2：添加空值检查
        if not playlist_data:
            return []

        order = playlist_data[4]  # sort_order 是第5列

        if order == 0:
            sorted_datas = sorted(datas, key=lambda x: x["storage_time"], reverse=True)
        elif order == 1:
            sorted_datas = sorted(datas, key=lambda x: x["storage_time"])
        elif order == 2:
            sorted_datas = sorted(datas, key=lambda x: lazy_pinyin(x["name"]))
        elif order == 3:
            sorted_datas = sorted(datas, key=lambda x: lazy_pinyin(x["singer"]))
        elif order == 4:
            sorted_datas = sorted(datas, key=lambda x: lazy_pinyin(x["album"]))

        datas = []
        for i in sorted_datas:
            datas.append(i['id'])

        return datas

    def music_library_search(self, keyword):
        global_search_music = []
        keyword = keyword.lower()

        results = self.search_engine.search(keyword)
        for i, song in enumerate(results, 1):
            global_search_music.append(song['id'])

        return global_search_music


