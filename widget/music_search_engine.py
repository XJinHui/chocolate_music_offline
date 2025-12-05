import json
from difflib import SequenceMatcher
from datetime import datetime
import sqlite3

# 如果没有安装jieba，可以使用以下简单分词替代
try:
    import jieba

    HAS_JIEBA = True
except ImportError:
    HAS_JIEBA = False


class MusicSearchEngine:
    def __init__(self, cursor):
        """
        初始化音乐搜索引擎 - SQLite版本

        Args:
            cursor: SQLite游标对象
        """
        self.cursor = cursor
        self.search_history = []
        self.search_cache = {}

        # 搜索字段及其权重
        self.search_fields = {
            'name': 3,  # 歌名权重最高
            'singer': 2,  # 歌手权重次之
            'album': 1,  # 专辑权重
            'albumartist': 1  # 专辑艺术家权重
        }

        # 初始化jieba（如果可用）
        if HAS_JIEBA:
            jieba.initialize()

    def _sqlite_to_dict(self, result):
        """将SQLite查询结果转换为字典"""
        if not result:
            return None

        return {
            'id': result[0],
            'name': result[1],
            'singer': result[2],
            'album': result[3],
            'albumartist': result[4],
            'album_data': result[5],
            'time': result[6],
            'photo': result[7],
            'like': bool(result[8]),  # 转换为布尔值
            'path': result[9],
            'storage_time': result[10]
        }

    def _get_all_music_data(self):
        """获取所有音乐数据（用于需要全量数据的操作）"""
        self.cursor.execute("SELECT * FROM musiclibrary")
        results = self.cursor.fetchall()
        return [self._sqlite_to_dict(row) for row in results]

    def search(self, query, limit=100, min_score=0.1):
        """
        综合搜索方法 - SQLite优化版本

        Args:
            query: 搜索关键词
            limit: 返回结果数量限制
            min_score: 最小匹配分数阈值

        Returns:
            list: 排序后的搜索结果
        """
        if not query or not query.strip():
            # 如果没有查询词，返回所有音乐（按存储时间倒序）
            self.cursor.execute("""
                SELECT * FROM musiclibrary 
                ORDER BY storage_time DESC 
                LIMIT ?
            """, (limit,))
            results = self.cursor.fetchall()
            return [self._sqlite_to_dict(row) for row in results]

        query = query.strip()

        # 记录搜索历史
        self._add_to_search_history(query)

        # 检查缓存
        cache_key = f"{query}_{limit}_{min_score}"
        if cache_key in self.search_cache:
            return self.search_cache[cache_key]

        # 首先用SQL进行基础搜索，提高性能
        base_results = self._sql_base_search(query, limit * 3)  # 获取更多结果用于评分

        # 对基础结果进行评分和排序
        scored_results = []
        for song in base_results:
            score = self._calculate_match_score(query, song)
            if score >= min_score:
                song_with_score = song.copy()
                song_with_score['_search_score'] = score
                song_with_score['_is_liked'] = song.get('like', False)
                scored_results.append(song_with_score)

        # 按分数排序，分数相同的按收藏和存储时间排序
        scored_results.sort(key=lambda x: (
            -x['_search_score'],  # 分数降序
            -x.get('_is_liked', False),  # 收藏的优先
            -x.get('storage_time', 0)  # 新添加的优先
        ))

        # 移除临时添加的搜索字段
        for result in scored_results:
            if '_search_score' in result:
                del result['_search_score']
            if '_is_liked' in result:
                del result['_is_liked']

        results = scored_results[:limit]

        # 缓存结果
        self.search_cache[cache_key] = results
        if len(self.search_cache) > 100:
            self.search_cache.pop(next(iter(self.search_cache)))

        return results

    def _sql_base_search(self, query, limit):
        """使用SQL进行基础搜索，提高性能"""
        query_like = f"%{query}%"

        # 使用UNION合并不同字段的搜索结果
        sql = """
            SELECT * FROM musiclibrary 
            WHERE name LIKE ? OR singer LIKE ? OR album LIKE ? OR albumartist LIKE ?
            ORDER BY 
                CASE 
                    WHEN name LIKE ? THEN 1
                    WHEN singer LIKE ? THEN 2
                    WHEN album LIKE ? THEN 3
                    ELSE 4
                END,
                storage_time DESC
            LIMIT ?
        """

        self.cursor.execute(sql, (
            query_like, query_like, query_like, query_like,
            query_like, query_like, query_like,
            limit
        ))

        results = self.cursor.fetchall()
        return [self._sqlite_to_dict(row) for row in results]

    def _calculate_match_score(self, query, song):
        """计算歌曲与查询词的匹配分数"""
        query = query.lower().strip()
        total_score = 0

        # 1. 完全匹配（最高权重）
        for field, weight in self.search_fields.items():
            field_value = str(song.get(field, '')).lower()
            if query == field_value:
                total_score += weight * 10

        # 2. 包含匹配
        for field, weight in self.search_fields.items():
            field_value = str(song.get(field, '')).lower()
            if query in field_value:
                # 根据匹配位置给予不同权重（开头匹配权重更高）
                if field_value.startswith(query):
                    total_score += weight * 5
                else:
                    total_score += weight * 3

        # 3. 分词匹配
        query_words = self._tokenize(query)
        for field, weight in self.search_fields.items():
            field_value = str(song.get(field, '')).lower()
            field_words = self._tokenize(field_value)

            common_words = set(query_words) & set(field_words)
            if common_words:
                total_score += weight * len(common_words) * 2

        # 4. 模糊匹配
        for field, weight in self.search_fields.items():
            field_value = str(song.get(field, '')).lower()
            similarity = self._string_similarity(query, field_value)
            if similarity > 0.7:  # 相似度阈值
                total_score += weight * similarity

        return total_score

    def _tokenize(self, text):
        """分词函数"""
        if not text:
            return []

        # 如果有jieba，使用jieba分词
        if HAS_JIEBA:
            return [word for word in jieba.cut_for_search(text) if word.strip()]
        else:
            # 简单的中文分词：按字符分割，但保留英文单词
            words = []
            current_word = ''

            for char in text:
                if self._is_chinese(char):
                    if current_word:
                        words.append(current_word)
                        current_word = ''
                    words.append(char)
                elif char.isalnum():
                    current_word += char
                else:
                    if current_word:
                        words.append(current_word)
                        current_word = ''

            if current_word:
                words.append(current_word)

            return [word for word in words if len(word) > 1 or self._is_chinese(word)]

    def _is_chinese(self, char):
        """判断字符是否为中文"""
        return '\u4e00' <= char <= '\u9fff'

    def _string_similarity(self, a, b):
        """计算字符串相似度"""
        return SequenceMatcher(None, a, b).ratio()

    def _add_to_search_history(self, query):
        """添加搜索历史"""
        timestamp = datetime.now().isoformat()
        self.search_history.append({
            'query': query,
            'timestamp': timestamp
        })

        # 限制搜索历史数量
        if len(self.search_history) > 100:
            self.search_history = self.search_history[-100:]

    def get_search_suggestions(self, query, limit=10):
        """获取搜索建议 - SQLite优化版本"""
        if not query or len(query) < 1:
            return []

        query = query.lower().strip()
        suggestions = set()

        # 从数据库中提取建议
        query_like = f"%{query}%"

        # 搜索歌名、歌手、专辑中的建议
        sql = """
            SELECT name, singer, album FROM musiclibrary 
            WHERE name LIKE ? OR singer LIKE ? OR album LIKE ?
            LIMIT 50
        """

        self.cursor.execute(sql, (query_like, query_like, query_like))
        results = self.cursor.fetchall()

        for name, singer, album in results:
            for field_value in [name, singer, album]:
                if field_value and query in field_value.lower():
                    words = self._tokenize(field_value)
                    for word in words:
                        if query in word.lower() and len(word) > len(query):
                            suggestions.add(word)

        # 从搜索历史中提取建议
        for history in self.search_history:
            history_query = history['query'].lower()
            if query in history_query and history_query not in suggestions:
                suggestions.add(history_query)

        # 按与查询词的相关性排序
        sorted_suggestions = sorted(
            suggestions,
            key=lambda x: (
                x.startswith(query),  # 以查询词开头的优先
                -len(x),  # 长度较短的优先
                self._string_similarity(query, x)  # 相似度高的优先
            ),
            reverse=True
        )

        return sorted_suggestions[:limit]

    def search_by_artist(self, artist_name, limit=50):
        """按艺术家搜索"""
        return self.search(artist_name, limit=limit)

    def search_by_album(self, album_name, limit=50):
        """按专辑搜索"""
        return self.search(album_name, limit=limit)

    def get_popular_searches(self, limit=10):
        """获取热门搜索"""
        from collections import Counter
        search_counter = Counter([item['query'] for item in self.search_history])
        return [query for query, count in search_counter.most_common(limit)]

    def clear_cache(self):
        """清空缓存"""
        self.search_cache.clear()


# 高级搜索功能扩展
class AdvancedMusicSearchEngine(MusicSearchEngine):
    def __init__(self, cursor):
        super().__init__(cursor)
        self.filters = {}

    def add_filter(self, filter_type, value):
        """添加过滤器"""
        self.filters[filter_type] = value

    def clear_filters(self):
        """清空过滤器"""
        self.filters.clear()

    def search_with_filters(self, query, limit=50):
        """带过滤器的搜索"""
        # 先执行普通搜索
        results = self.search(query, limit=limit * 2)

        # 应用过滤器
        filtered_results = []
        for song in results:
            if self._apply_filters(song):
                filtered_results.append(song)

        return filtered_results[:limit]

    def _apply_filters(self, song):
        """应用所有过滤器"""
        for filter_type, value in self.filters.items():
            if not self._check_filter(song, filter_type, value):
                return False
        return True

    def _check_filter(self, song, filter_type, value):
        """检查单个过滤器"""
        if filter_type == 'min_duration':
            return song.get('time', 0) >= value
        elif filter_type == 'max_duration':
            return song.get('time', 0) <= value
        elif filter_type == 'liked_only':
            return song.get('like', False) == value
        elif filter_type == 'year_from':
            album_data = song.get('album_data', '')
            try:
                year = int(album_data) if album_data.isdigit() else 0
                return year >= value
            except:
                return False
        elif filter_type == 'year_to':
            album_data = song.get('album_data', '')
            try:
                year = int(album_data) if album_data.isdigit() else 0
                return year <= value
            except:
                return False
        elif filter_type == 'artist':
            return value.lower() in song.get('singer', '').lower()

        return True