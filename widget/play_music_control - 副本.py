import random
import time
import os
import threading
import re
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal
from ffpyplayer.player import MediaPlayer


class PlayMusicControl(QObject):
    # 定义信号
    update_lyrics = pyqtSignal()
    automatic_play_music = pyqtSignal()
    update_progress_bar = pyqtSignal(float)

    def __init__(self, music_library,main):
        super().__init__()
        self.start_play = False
        self.play_repeat = False  # 判断是否正在单曲循环
        self.play_automatic = False  # 判断是否正在自动播放
        self.play_status = False
        self.run = True
        self.music_library = music_library
        self.main = main
        self.music_play_order = []
        self.player = MediaPlayer('')

        # 连接信号
        self.update_lyrics.connect(self._handle_update_lyrics)
        self.automatic_play_music.connect(self._handle_automatic_play_music)
        self.update_progress_bar.connect(self._handle_update_progress_bar)

        if self.music_library.setting['volume_type']:
            self.set_volume(self.music_library.setting['volume'])
            self.volume = self.music_library.setting['volume']/100
        else:
            self.set_volume(0)
            self.volume = 0

        if self.music_library.setting['id']:
            self.music_play_order = [self.music_library.setting['id']]
            self.play_music()
        else:
            self.music = {}

    def update_music(self):
        id = self.music_library.setting['id']
        self.music = self.music_library.get_song_by_id(id)

    def play(self):
        self.play_status = False

        # while self.play_threading.is_alive() and len(threading.enumerate()) > 3:
        #     time.sleep(0.01)

        self.player = MediaPlayer(self.music['path'])  # 默认音频时钟、自动开始


        self.update_lyrics.emit()
        # self.main.lyrics_page_widget.display_lyrics()
        # time.sleep(1)
        # self.player.set_volume(self.volume)

        # 等待播放器准备就绪
        # max_retries = 1000
        while True:
            frame, val = self.player.get_frame()
            if frame is not None or val == 'eof':
                break
            time.sleep(0.0001)  # 增加等待时间

        self.play_status = True

        # 设置音量
        self.player.set_volume(self.volume)
        while self.run:
            frame, val = self.player.get_frame()  # 音频帧返回 None, val 是播放状态
            # print(frame,val)
            if val == 'eof':  # 播放完毕
                break

            if self.main.progress_bar:
                current_time = self.player.get_pts()
                self.update_progress_bar.emit(current_time)
                # try:
                #     self.main.horizontalSlider_music_progress_bar.setValue(int(current_time * 100))
                #     self.main.lyrics_page_widget.horizontalSlider_music_progress_bar.setValue(int(current_time * 100))
                # except:
                #     print('进度显示错误')
                #     pass

            # if self.lyrics:
            #     current_time = self.player.get_pts()
            #     keys = list(self.lyrics.keys())
            #     for i in range(len(keys)-1):
            #         if keys[i] <= current_time and keys[i+1] > current_time:
            #             print("\r" + " " * 80 + "\r" + self.lyrics[keys[i]], end='', flush=True)
            #             time.sleep(0.5)
            #             break
            #
            #     if keys[-1] < current_time:
            #         print("\r" + " " * 80 + "\r" + self.lyrics[keys[-1]], end='', flush=True)
            #
            #     elif keys[0] > current_time:
            #         print("\r" + " " * 80 + "\r" + self.lyrics[keys[0]], end='', flush=True)

            time.sleep(0.01)  # 释放 CPU
        self.player.close_player()
        if val == 'eof':
            self.automatic_play_music.emit()
        # time.sleep(0.01)
        # self.player.set_volume(volume)

    def _handle_update_lyrics(self):
        lyrics_path = Path(self.music['path']).with_suffix(".lrc")
        self.lyrics = {}
        if os.path.isfile(lyrics_path):
            with open(lyrics_path, "r", errors='ignore') as f:
                lrc = f.read()
                lrcs = re.match('.*?(\[\d\d.*)', lrc, re.S)
                lyrics = lrcs.group(1).split('[')
                for i in lyrics[1:]:
                    ret = re.match('(.*):(.*)](.*)', i)
                    lyrics_time = int(ret.group(1)) * 60 + float(ret.group(2))
                    if ret.group(3):
                        self.lyrics[lyrics_time] = ret.group(3)

        time.sleep(0.1)
        self.main.lyrics_page_widget.display_lyrics()

    def _handle_update_progress_bar(self, current_time):
        try:
            self.main.horizontalSlider_music_progress_bar.setValue(int(current_time * 100))
            self.main.lyrics_page_widget.horizontalSlider_music_progress_bar.setValue(int(current_time * 100))
        except:
            print('进度显示错误')

    def _handle_automatic_play_music(self):
        if self.music_library.setting['play_type'] != 1:
            # self.play_automatic = True
            self.next_music()
            # self.play_automatic = False
        else:
            # self.play_repeat = True
            self.update_page(self.music_library.setting['id'])
            # self.play_repeat = False

    def play_music(self):
        '''播放音乐'''
        # print(len(threading.enumerate()))
        self.update_music()
        self.run = False
        if self.start_play:
            while self.play_threading.is_alive():
                time.sleep(0.01)

        self.run = True
        self.play_threading = threading.Thread(target=self.play, args=())
        self.play_threading.setDaemon(True)
        self.play_threading.start()
        self.start_play = True

    def pause_or_play_music(self):
        '''暂停和播放音乐'''
        self.player.toggle_pause()

    def change_progress(self,time):
        '''改变进度条'''
        # print(time)
        self.player.seek(time/100, relative=False, accurate=True)
        # self.player.seek(time/100)

    def next_music(self):
        '''下一首音乐'''
        id = self.music_library.setting['id']
        list_id = self.music_library.setting['play_list_id']

        if list_id == -1:
            n = self.music_play_order.index(id)

            if n == len(self.music_play_order) - 1:
                while True:
                    n = random.randint(0, len(self.music_library.musiclibrary)-1)
                    next_id = self.music_library.musiclibrary[n]['id']
                    if next_id != self.music_library.setting['id']:
                        if next_id in self.music_play_order:
                            self.music_play_order.remove(next_id)
                        break
                self.music_play_order.append(next_id)

            else:
                next_id = self.music_play_order[n + 1]

        else:
            list = self.music_library.musiclist[f'{list_id}']

            if len(list) < 1:
                self.update_page(id)
                return
            if len(list) == 1:
                self.update_page(list[0])
                return

            if self.music_library.setting['play_type'] != 2:
                if id in list:
                    n = list.index(id)
                    if n == len(list) - 1:
                        next_id = list[0]
                    else:
                        next_id = list[n + 1]
                else:
                    next_id = list[0]
                self.music_play_order = [next_id]

            else:
                n = self.music_play_order.index(id)
                if n == len(self.music_play_order) - 1:
                    while True:
                        n = random.randint(0, len(list) - 1)
                        next_id = list[n]
                        if next_id != id:
                            if next_id in self.music_play_order:
                                self.music_play_order.remove(next_id)
                            break
                    self.music_play_order.append(next_id)
                else:
                    next_id = self.music_play_order[n + 1]

        self.update_page(next_id)



    def previous_music(self):
        '''上一首音乐'''
        id = self.music_library.setting['id']
        list_id = self.music_library.setting['play_list_id']

        if list_id == -1:
            n = self.music_play_order.index(id)

            if n == 0:
                while True:
                    n = random.randint(0, len(self.music_library.musiclibrary)-1)
                    next_id = self.music_library.musiclibrary[n]['id']
                    if next_id != self.music_library.setting['id']:
                        if next_id in self.music_play_order:
                            self.music_play_order.remove(next_id)
                        break
                self.music_play_order.insert(0,next_id)

            else:
                next_id = self.music_play_order[n - 1]

        else:
            list = self.music_library.musiclist[f'{list_id}']

            if len(list) < 1:
                self.update_page(id)
                return
            if len(list) == 1:
                self.update_page(list[0])
                return

            if self.music_library.setting['play_type'] != 2:
                if id in list:
                    n = list.index(id)
                    next_id = list[n - 1]
                else:
                    next_id = list[0]
                self.music_play_order = [next_id]

            else:
                n = self.music_play_order.index(id)
                if n == 0:
                    while True:
                        n = random.randint(0, len(list) - 1)
                        next_id = list[n]
                        if next_id != id:
                            if next_id in self.music_play_order:
                                self.music_play_order.remove(next_id)
                            break
                    self.music_play_order.insert(0,next_id)
                else:
                    next_id = self.music_play_order[n - 1]

        self.update_page(next_id)

    def set_volume(self, volume):
        '''设置音量'''
        self.player.set_volume(volume/100)
        self.volume = volume/100

    def update_page(self, id):
        '''更新页面'''
        self.music_library.update_play_music(id, self.music_library.setting['play_list_id'])
        self.main.update_play_music()
        self.main.horizontalSlider_music_progress_bar.setValue(0)
        self.main.lyrics_page_widget.horizontalSlider_music_progress_bar.setValue(0)
        self.play_music()