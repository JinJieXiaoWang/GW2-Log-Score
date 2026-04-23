import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "databases", "gw2_logs.db")

def check_database():
    print("=== 检查历史数据 ===")
    print(f"数据库路径: {db_path}")
    print(f"数据库文件存在: {os.path.exists(db_path)}")
    
    if not os.path.exists(db_path):
        print("数据库文件不存在")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 检查combat_logs表
            print("\n=== 战斗日志记录 ===")
            cursor.execute('SELECT * FROM combat_logs ORDER BY date DESC')
            logs = cursor.fetchall()
            print(f"战斗日志数量: {len(logs)}")
            
            for log in logs:
                print(f"- 日期: {log['date']}, 模式: {log['mode']}, 副本: {log['encounter_name']}, 持续时间: {log['duration']}秒")
            
            # 检查combat_scores表
            print("\n=== 评分记录 ===")
            cursor.execute('SELECT COUNT(*) FROM combat_scores')
            score_count = cursor.fetchone()[0]
            print(f"评分记录数量: {score_count}")
            
            # 检查最近的评分记录
            cursor.execute('SELECT * FROM combat_scores ORDER BY id DESC LIMIT 5')
            recent_scores = cursor.fetchall()
            for score in recent_scores:
                print(f"- 玩家: {score['player_name']}, 评分: {score['total_score']}")
            
            # 检查players表
            print("\n=== 玩家记录 ===")
            cursor.execute('SELECT * FROM players')
            players = cursor.fetchall()
            print(f"玩家数量: {len(players)}")
            for player in players:
                print(f"- 姓名: {player['name']}, 账号: {player['account']}, 职业: {player['profession']}, 定位: {player['role']}")
            
            # 检查file_fingerprints表
            print("\n=== 文件指纹记录 ===")
            cursor.execute('SELECT * FROM file_fingerprints ORDER BY upload_date DESC')
            fingerprints = cursor.fetchall()
            print(f"文件指纹数量: {len(fingerprints)}")
            for fp in fingerprints:
                print(f"- 文件名: {fp['file_name']}, 上传日期: {fp['upload_date']}, 日志ID: {fp['log_id']}")
            
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    check_database()
