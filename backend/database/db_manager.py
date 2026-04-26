import sqlite3
import json
import os
import hashlib
from datetime import datetime


class DBManager:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                ),
                "databases",
                "gw2_logs.db",
            )
        self.db_path = db_path
        self._init_db()
        self._migrate_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    name TEXT PRIMARY KEY,
                    profession TEXT,
                    role TEXT,
                    account TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS combat_logs (
                    log_id TEXT PRIMARY KEY,
                    mode TEXT,
                    encounter_name TEXT,
                    date TEXT,
                    duration INTEGER,
                    log_path TEXT,
                    recorder TEXT
                )
            """)

            cursor.execute("""
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
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_fingerprints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    upload_date TEXT NOT NULL,
                    log_id TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(file_name, upload_date)
                )
            """)

            # 字典类型�?            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sys_dict_type (
                    dict_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dict_name TEXT NOT NULL DEFAULT '',
                    dict_type TEXT NOT NULL DEFAULT '',
                    status INTEGER DEFAULT 0,
                    sort_order INTEGER DEFAULT 0,
                    remark TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(dict_type)
                )
            """)

            # 字典数据�?            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sys_dict_data (
                    dict_code INTEGER PRIMARY KEY AUTOINCREMENT,
                    dict_sort INTEGER DEFAULT 0,
                    dict_label TEXT NOT NULL DEFAULT '',
                    dict_value TEXT NOT NULL DEFAULT '',
                    dict_type TEXT NOT NULL DEFAULT '',
                    data_type TEXT DEFAULT '',
                    css_class TEXT,
                    list_class TEXT,
                    is_default INTEGER DEFAULT 0,
                    status INTEGER DEFAULT 0,
                    remark TEXT,
                    color TEXT DEFAULT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_dict_type ON sys_dict_data(dict_type)
            """)

            conn.commit()

    def _migrate_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 检�?players �?            cursor.execute("PRAGMA table_info(players)")
            columns = [column[1] for column in cursor.fetchall()]
            if "account" not in columns:
                print("Migrating database: adding 'account' column to players table...")
                cursor.execute("ALTER TABLE players ADD COLUMN account TEXT")
                conn.commit()
                print("Migration completed successfully.")
            
            # 检�?sys_dict_data 表是否有 color 字段
            cursor.execute("PRAGMA table_info(sys_dict_data)")
            dict_data_columns = [column[1] for column in cursor.fetchall()]
            if "color" not in dict_data_columns:
                print("Migrating database: adding 'color' column to sys_dict_data table...")
                cursor.execute("ALTER TABLE sys_dict_data ADD COLUMN color TEXT DEFAULT NULL")
                conn.commit()
                print("Color field migration completed successfully.")
            
            # 检查是否有旧的字典表需要迁�?            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dict_groups'")
            has_old_dict = cursor.fetchone() is not None
            
            if has_old_dict:
                print("Migrating old dictionary tables to new structure...")
                self._migrate_old_dict_tables(conn)
                print("Dictionary migration completed.")
    
    def _migrate_old_dict_tables(self, conn):
        cursor = conn.cursor()
        
        # 检查是否已经迁移过
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sys_dict_type'")
        has_new_dict = cursor.fetchone() is not None
        
        if has_new_dict:
            # 检查新表是否有数据，如果有则不迁移
            cursor.execute("SELECT COUNT(*) FROM sys_dict_type")
            if cursor.fetchone()[0] > 0:
                print("New dictionary tables already have data, skipping migration.")
                return
        
        try:
            # 迁移 dict_groups -> sys_dict_type
            cursor.execute("SELECT * FROM dict_groups")
            groups = cursor.fetchall()
            for group in groups:
                group_id, group_code, group_name, description, status, sort_order, created_at, updated_at = group
                cursor.execute(
                    "INSERT OR IGNORE INTO sys_dict_type (dict_name, dict_type, status, sort_order, remark, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (group_name, group_code, status, sort_order, description, created_at, updated_at)
                )
            
            # 迁移 dict_items -> sys_dict_data
            cursor.execute("SELECT * FROM dict_items")
            items = cursor.fetchall()
            for item in items:
                item_id, group_id, item_code, item_name, item_value, description, status, sort_order, created_at, updated_at = item
                # 获取 dict_type
                cursor.execute("SELECT dict_type FROM sys_dict_type WHERE ROWID IN (SELECT dict_id FROM sys_dict_type WHERE ROWID = ?)", (group_id,))
                dict_type_row = cursor.fetchone()
                if dict_type_row:
                    dict_type = dict_type_row[0]
                    cursor.execute(
                        "INSERT OR IGNORE INTO sys_dict_data (dict_sort, dict_label, dict_value, dict_type, status, remark, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (sort_order, item_name, item_code, dict_type, status, description, created_at, updated_at)
                    )
            
            conn.commit()
            print("Old dictionary tables migrated successfully.")
            
        except Exception as e:
            print(f"Error migrating old dictionary tables: {e}")
            conn.rollback()

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
            cursor.execute(
                """
                SELECT file_hash, log_id FROM file_fingerprints
                WHERE file_name = ? AND upload_date = ?
            """,
                (file_name, today),
            )
            return cursor.fetchone()

    def save_file_fingerprint(self, file_name, file_hash, log_id):
        today = datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO file_fingerprints
                (file_name, file_hash, upload_date, log_id)
                VALUES (?, ?, ?, ?)
            """,
                (file_name, file_hash, today, log_id),
            )
            conn.commit()

    def delete_log_data(self, log_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM combat_scores WHERE log_id = ?", (log_id,))
            cursor.execute("DELETE FROM combat_logs WHERE log_id = ?", (log_id,))
            cursor.execute("DELETE FROM file_fingerprints WHERE log_id = ?", (log_id,))
            conn.commit()

    def add_player(self, name, profession, role, account=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO players (name, profession, role, account)
                VALUES (?, ?, ?, ?)
            """,
                (name, profession, role, account or name),
            )
            conn.commit()

    def add_combat_log(
        self, log_id, mode, encounter_name, date, duration, log_path, recorder
    ):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO combat_logs (log_id, mode, encounter_name, date, duration, log_path, recorder)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (log_id, mode, encounter_name, date, duration, log_path, recorder),
            )
            conn.commit()

    def add_combat_score(self, log_id, player_name, scores, total_score, details):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            s_dps = scores.get("dps", 0)
            s_cc = scores.get("cc", 0)
            s_survival = scores.get("survival", 0)
            s_boon = scores.get(
                "boon", scores.get("boon_total", scores.get("stability", 0))
            )

            cursor.execute(
                """
                INSERT INTO combat_scores (log_id, player_name, score_dps, score_cc, score_survival, score_boon, total_score, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    log_id,
                    player_name,
                    s_dps,
                    s_cc,
                    s_survival,
                    s_boon,
                    total_score,
                    json.dumps(details),
                ),
            )
            conn.commit()

    def save_combat_log(
        self, log_id, mode, encounter_name, date, duration, log_path, recorder
    ):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO combat_logs (log_id, mode, encounter_name, date, duration, log_path, recorder)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (log_id, mode, encounter_name, date, duration, log_path, recorder),
            )
            conn.commit()

    def save_player(self, name, profession, role, account=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO players (name, profession, role, account)
                VALUES (?, ?, ?, ?)
            """,
                (name, profession, role, account or name),
            )
            conn.commit()

    def save_score(
        self,
        log_id,
        player_name,
        score_dps,
        score_cc,
        score_survival,
        score_boon,
        total_score,
        details,
    ):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO combat_scores (log_id, player_name, score_dps, score_cc, score_survival, score_boon, total_score, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    log_id,
                    player_name,
                    score_dps,
                    score_cc,
                    score_survival,
                    score_boon,
                    total_score,
                    details,
                ),
            )
            conn.commit()

    def get_player_attendance(self, name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(*) FROM combat_scores WHERE player_name = ?
            """,
                (name,),
            )
            return cursor.fetchone()[0]

    def get_all_logs(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM combat_logs ORDER BY date DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_all_scores(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM combat_scores ORDER BY total_score DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_scores_by_log(self, log_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM combat_scores WHERE log_id = ? ORDER BY total_score DESC
            """,
                (log_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_log_by_hash(self, file_hash):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT cl.* FROM combat_logs cl
                JOIN file_fingerprints ff ON cl.log_id = ff.log_id
                WHERE ff.file_hash = ?
            """,
                (file_hash,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def clear_all_data(self, backup=True):
        """
        清空所有数�?        :param backup: 是否在清除前备份数据�?        :return: 是否成功
        """
        if backup:
            backup_path = (
                f"{self.db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            try:
                import shutil

                shutil.copy2(self.db_path, backup_path)
                print(f"数据库已备份�? {backup_path}")
            except Exception as e:
                print(f"备份失败: {e}")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM combat_scores")
                cursor.execute("DELETE FROM combat_logs")
                cursor.execute("DELETE FROM players")
                cursor.execute("DELETE FROM file_fingerprints")
                conn.commit()
            print("所有数据已清空")
            return True
        except Exception as e:
            print(f"清空数据失败: {e}")
            return False

    def clear_today_data(self, backup=True):
        """
        清空当日数据
        :param backup: 是否在清除前备份数据�?        :return: 是否成功
        """
        today = datetime.now().strftime("%Y-%m-%d")

        if backup:
            backup_path = f"{self.db_path}.backup_today_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                import shutil

                shutil.copy2(self.db_path, backup_path)
                print(f"数据库已备份�? {backup_path}")
            except Exception as e:
                print(f"备份失败: {e}")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 获取需要删除的log_ids（根据combat_logs的date字段�?                cursor.execute(
                    """
                    SELECT log_id FROM combat_logs
                    WHERE date LIKE ?
                """,
                    (f"{today}%",),
                )
                log_ids = [row[0] for row in cursor.fetchall()]

                if log_ids:
                    for log_id in log_ids:
                        cursor.execute(
                            "DELETE FROM combat_scores WHERE log_id = ?", (log_id,)
                        )
                        cursor.execute(
                            "DELETE FROM file_fingerprints WHERE log_id = ?", (log_id,)
                        )

                # 删除当天的战斗日�?                cursor.execute(
                    """
                    DELETE FROM combat_logs
                    WHERE date LIKE ?
                """,
                    (f"{today}%",),
                )

                # 同时删除当天上传的文件指�?                cursor.execute(
                    "DELETE FROM file_fingerprints WHERE upload_date = ?", (today,)
                )
                conn.commit()
            print(f"{today}的当日数据已清空")
            return True
        except Exception as e:
            print(f"清空当日数据失败: {e}")
            return False

    # ==================== 字典类型管理 ====================
    def add_dict_type(self, dict_name, dict_type, status=0, sort_order=0, remark=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute(
                """
                INSERT INTO sys_dict_type (dict_name, dict_type, status, sort_order, remark, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (dict_name, dict_type, status, sort_order, remark, now, now),
            )
            conn.commit()
            return cursor.lastrowid

    def update_dict_type(self, dict_id, dict_name=None, dict_type=None, status=None, sort_order=None, remark=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            updates = []
            params = []
            if dict_name is not None:
                updates.append("dict_name = ?")
                params.append(dict_name)
            if dict_type is not None:
                updates.append("dict_type = ?")
                params.append(dict_type)
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            if sort_order is not None:
                updates.append("sort_order = ?")
                params.append(sort_order)
            if remark is not None:
                updates.append("remark = ?")
                params.append(remark)
            if updates:
                updates.append("updated_at = ?")
                params.extend([now, dict_id])
                cursor.execute(
                    f"UPDATE sys_dict_type SET {', '.join(updates)} WHERE dict_id = ?",
                    params,
                )
                conn.commit()

    def delete_dict_type(self, dict_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sys_dict_type WHERE dict_id = ?", (dict_id,))
            cursor.execute("DELETE FROM sys_dict_data WHERE dict_type IN (SELECT dict_type FROM sys_dict_type WHERE dict_id = ?)", (dict_id,))
            conn.commit()

    def get_dict_type(self, dict_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sys_dict_type WHERE dict_id = ?", (dict_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_dict_type_by_code(self, dict_type):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sys_dict_type WHERE dict_type = ?", (dict_type,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_dict_types(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sys_dict_type ORDER BY sort_order, dict_id")
            return [dict(row) for row in cursor.fetchall()]

    # ==================== 字典数据管理 ====================
    def add_dict_data(self, dict_type, dict_label, dict_value, dict_sort=0, data_type='', 
                      css_class=None, list_class=None, is_default=0, status=0, remark=None, color=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute(
                """
                INSERT INTO sys_dict_data (dict_sort, dict_label, dict_value, dict_type, data_type, 
                                         css_class, list_class, is_default, status, remark, color, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (dict_sort, dict_label, dict_value, dict_type, data_type, 
                 css_class, list_class, is_default, status, remark, color, now, now),
            )
            conn.commit()
            return cursor.lastrowid

    def update_dict_data(self, dict_code, dict_label=None, dict_value=None, dict_sort=None, 
                         data_type=None, css_class=None, list_class=None, is_default=None, 
                         status=None, remark=None, color=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            updates = []
            params = []
            if dict_label is not None:
                updates.append("dict_label = ?")
                params.append(dict_label)
            if dict_value is not None:
                updates.append("dict_value = ?")
                params.append(dict_value)
            if dict_sort is not None:
                updates.append("dict_sort = ?")
                params.append(dict_sort)
            if data_type is not None:
                updates.append("data_type = ?")
                params.append(data_type)
            if css_class is not None:
                updates.append("css_class = ?")
                params.append(css_class)
            if list_class is not None:
                updates.append("list_class = ?")
                params.append(list_class)
            if is_default is not None:
                updates.append("is_default = ?")
                params.append(is_default)
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            if remark is not None:
                updates.append("remark = ?")
                params.append(remark)
            if color is not None:
                updates.append("color = ?")
                params.append(color)
            if updates:
                updates.append("updated_at = ?")
                params.extend([now, dict_code])
                cursor.execute(
                    f"UPDATE sys_dict_data SET {', '.join(updates)} WHERE dict_code = ?",
                    params,
                )
                conn.commit()

    def delete_dict_data(self, dict_code):
        with sqlite3.connect(self.db_path) as cn:
            cursor = cn.cursor()
            cursor.execute("DELETE FROM sys_dict_data WHERE dict_code = ?", (dict_code,))
            cn.commit()

    def get_dict_data(self, dict_code):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sys_dict_data WHERE dict_code = ?", (dict_code,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_dict_data_by_type(self, dict_type, include_disabled=False):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if include_disabled:
                cursor.execute(
                    "SELECT * FROM sys_dict_data WHERE dict_type = ? ORDER BY dict_sort, dict_code",
                    (dict_type,),
                )
            else:
                cursor.execute(
                    "SELECT * FROM sys_dict_data WHERE dict_type = ? AND status = 0 ORDER BY dict_sort, dict_code",
                    (dict_type,),
                )
            return [dict(row) for row in cursor.fetchall()]

    def get_dict_data_by_value(self, dict_type, dict_value):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM sys_dict_data WHERE dict_type = ? AND dict_value = ?",
                (dict_type, dict_value),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

