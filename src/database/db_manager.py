import sqlite3
import json
import os
import hashlib
from datetime import datetime

class DBManager:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "databases", "gw2_logs.db")
        self.db_path = db_path
        self._init_db()
        self._migrate_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    name TEXT PRIMARY KEY,
                    profession TEXT,
                    role TEXT,
                    account TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS combat_logs (
                    log_id TEXT PRIMARY KEY,
                    mode TEXT,
                    encounter_name TEXT,
                    date TEXT,
                    duration INTEGER,
                    log_path TEXT,
                    recorder TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS combat_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    log_id TEXT,
                    player_name TEXT,
                    score_dps REAL,
                    score_cc REAL,
                    score_survival REAL,
                    score_boon REAL,
                    total_score REAL,
                    details TEXT,
                    FOREIGN KEY(log_id) REFERENCES combat_logs(log_id),
                    FOREIGN KEY(player_name) REFERENCES players(name)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_fingerprints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    upload_date TEXT NOT NULL,
                    log_id TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(file_name, upload_date)
                )
            ''')
            
            conn.commit()

    def _migrate_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(players)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'account' not in columns:
                print("Migrating database: adding 'account' column to players table...")
                cursor.execute("ALTER TABLE players ADD COLUMN account TEXT")
                conn.commit()
                print("Migration completed successfully.")

    def calculate_file_hash(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def get_today_file_fingerprint(self, file_name):
        today = datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT file_hash, log_id FROM file_fingerprints
                WHERE file_name = ? AND upload_date = ?
            ''', (file_name, today))
            return cursor.fetchone()

    def save_file_fingerprint(self, file_name, file_hash, log_id):
        today = datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO file_fingerprints (file_name, file_hash, upload_date, log_id)
                VALUES (?, ?, ?, ?)
            ''', (file_name, file_hash, today, log_id))
            conn.commit()

    def delete_log_data(self, log_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM combat_scores WHERE log_id = ?', (log_id,))
            cursor.execute('DELETE FROM combat_logs WHERE log_id = ?', (log_id,))
            cursor.execute('DELETE FROM file_fingerprints WHERE log_id = ?', (log_id,))
            conn.commit()

    def add_player(self, name, profession, role, account=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO players (name, profession, role, account)
                VALUES (?, ?, ?, ?)
            ''', (name, profession, role, account or name))
            conn.commit()

    def add_combat_log(self, log_id, mode, encounter_name, date, duration, log_path, recorder):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO combat_logs (log_id, mode, encounter_name, date, duration, log_path, recorder)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (log_id, mode, encounter_name, date, duration, log_path, recorder))
            conn.commit()

    def add_combat_score(self, log_id, player_name, scores, total_score, details):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            s_dps = scores.get('dps', 0)
            s_cc = scores.get('cc', 0)
            s_survival = scores.get('survival', 0)
            s_boon = scores.get('boon', scores.get('boon_total', scores.get('stability', 0)))
            
            cursor.execute('''
                INSERT INTO combat_scores (log_id, player_name, score_dps, score_cc, score_survival, score_boon, total_score, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (log_id, player_name, s_dps, s_cc, s_survival, s_boon, total_score, json.dumps(details)))
            conn.commit()

    def save_combat_log(self, log_id, mode, encounter_name, date, duration, log_path, recorder):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO combat_logs (log_id, mode, encounter_name, date, duration, log_path, recorder)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (log_id, mode, encounter_name, date, duration, log_path, recorder))
            conn.commit()

    def save_player(self, name, profession, role, account=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO players (name, profession, role, account)
                VALUES (?, ?, ?, ?)
            ''', (name, profession, role, account or name))
            conn.commit()

    def save_score(self, log_id, player_name, score_dps, score_cc, score_survival, score_boon, total_score, details):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO combat_scores (log_id, player_name, score_dps, score_cc, score_survival, score_boon, total_score, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (log_id, player_name, score_dps, score_cc, score_survival, score_boon, total_score, details))
            conn.commit()

    def get_player_attendance(self, name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM combat_scores WHERE player_name = ?
            ''', (name,))
            return cursor.fetchone()[0]

    def get_all_logs(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM combat_logs ORDER BY date DESC')
            return [dict(row) for row in cursor.fetchall()]

    def get_all_scores(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM combat_scores ORDER BY total_score DESC')
            return [dict(row) for row in cursor.fetchall()]

    def get_scores_by_log(self, log_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM combat_scores WHERE log_id = ? ORDER BY total_score DESC
            ''', (log_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_log_by_hash(self, file_hash):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT cl.* FROM combat_logs cl
                JOIN file_fingerprints ff ON cl.log_id = ff.log_id
                WHERE ff.file_hash = ?
            ''', (file_hash,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def clear_all_data(self, backup=True):
        """
        清空所有数据
        :param backup: 是否在清除前备份数据库
        :return: 是否成功
        """
        if backup:
            backup_path = f"{self.db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                import shutil
                shutil.copy2(self.db_path, backup_path)
                print(f"数据库已备份至: {backup_path}")
            except Exception as e:
                print(f"备份失败: {e}")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM combat_scores')
                cursor.execute('DELETE FROM combat_logs')
                cursor.execute('DELETE FROM players')
                cursor.execute('DELETE FROM file_fingerprints')
                conn.commit()
            print("所有数据已清空")
            return True
        except Exception as e:
            print(f"清空数据失败: {e}")
            return False

    def clear_today_data(self, backup=True):
        """
        清空当日数据
        :param backup: 是否在清除前备份数据库
        :return: 是否成功
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        if backup:
            backup_path = f"{self.db_path}.backup_today_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                import shutil
                shutil.copy2(self.db_path, backup_path)
                print(f"数据库已备份至: {backup_path}")
            except Exception as e:
                print(f"备份失败: {e}")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 获取需要删除的log_ids（根据combat_logs的date字段）
                cursor.execute('''
                    SELECT log_id FROM combat_logs
                    WHERE date LIKE ?
                ''', (f"{today}%",))
                log_ids = [row[0] for row in cursor.fetchall()]
                
                if log_ids:
                    for log_id in log_ids:
                        cursor.execute('DELETE FROM combat_scores WHERE log_id = ?', (log_id,))
                        cursor.execute('DELETE FROM file_fingerprints WHERE log_id = ?', (log_id,))
                
                # 删除当天的战斗日志
                cursor.execute('''
                    DELETE FROM combat_logs
                    WHERE date LIKE ?
                ''', (f"{today}%",))
                
                # 同时删除当天上传的文件指纹
                cursor.execute('DELETE FROM file_fingerprints WHERE upload_date = ?', (today,))
                conn.commit()
            print(f"{today}的当日数据已清空")
            return True
        except Exception as e:
            print(f"清空当日数据失败: {e}")
            return False
