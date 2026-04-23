#!/usr/bin/env python3
"""
检查完整的数据流：解析 -> 评分 -> 存储 -> 读取
"""

import json
import os
import sys
import sqlite3

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_full_flow():
    """检查完整流程"""
    from src.parser.ei_parser import EIParser
    from src.scoring.scoring_engine import ScoringEngine
    from src.database.db_manager import DBManager
    
    print("=" * 80)
    print("检查完整数据流程")
    print("=" * 80)
    
    # 1. 解析
    print("\n[1] 解析数据...")
    json_file = os.path.join(os.path.dirname(__file__), "data.json")
    parser = EIParser()
    parsed_data = parser.parse_file(json_file)
    print(f"  [OK] 解析到 {len(parsed_data['players'])} 个玩家")
    
    # 2. 评分
    print("\n[2] 计算评分...")
    scorer = ScoringEngine()
    scores = scorer.calculate_wvw_scores(parsed_data)
    print(f"  [OK] 计算了 {len(scores)} 个玩家的评分")
    
    if scores:
        print(f"\n  前3个玩家:")
        for i, s in enumerate(scores[:3]):
            print(f"  {i+1}. {s['player_name']} - {s['profession']} - {s['role']} - {s['total_score']}")
    
    # 3. 存储
    print("\n[3] 存储到数据库...")
    test_db_path = os.path.join(os.path.dirname(__file__), "temp_test.db")
    
    # 清理旧的测试数据库
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    db = DBManager(test_db_path)
    
    # 存储战斗日志
    db.add_combat_log(
        parsed_data['log_id'],
        parsed_data['mode'],
        parsed_data['encounter_name'],
        parsed_data['date'],
        int(parsed_data['duration']),
        json_file,
        parsed_data['recorded_by']
    )
    
    # 存储玩家和评分
    for s in scores:
        db.save_player(s['player_name'], s['profession'], s['role'], s['account'])
        db.save_score(
            parsed_data['log_id'],
            s['player_name'],
            s['scores'].get('dps', 0),
            s['scores'].get('cc', 0),
            s['scores'].get('survival', 0),
            0,  # boon
            s['total_score'],
            str(s['details'])
        )
    
    print(f"  [OK] 存储完成")
    
    # 4. 检查存储结果
    print("\n[4] 检查数据库内容...")
    with sqlite3.connect(test_db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查玩家
        cursor.execute("SELECT COUNT(*) FROM players")
        player_count = cursor.fetchone()[0]
        print(f"  玩家表记录数: {player_count}")
        
        # 检查评分
        cursor.execute("SELECT COUNT(*) FROM combat_scores")
        score_count = cursor.fetchone()[0]
        print(f"  评分表记录数: {score_count}")
        
        # 检查实际内容
        print(f"\n  评分表中的前5个玩家:")
        cursor.execute("""
            SELECT cs.*, p.profession, p.role
            FROM combat_scores cs
            JOIN players p ON cs.player_name = p.name
            ORDER BY cs.total_score DESC
            LIMIT 5
        """)
        for i, row in enumerate(cursor.fetchall(), 1):
            print(f"  {i}. {row['player_name']} - {row['profession']} - {row['role']} - {row['total_score']}")
    
    # 5. 测试API读取
    print("\n[5] 测试API读取函数...")
    all_scores = db.get_all_scores()
    print(f"  get_all_scores() 返回: {len(all_scores)} 条记录")
    
    # 清理测试数据库
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        print(f"\n  [OK] 清理测试数据库")
    
    print("\n" + "=" * 80)
    print("检查完成！")
    print("=" * 80)


if __name__ == "__main__":
    check_full_flow()
