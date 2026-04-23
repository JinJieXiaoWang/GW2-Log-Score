#!/usr/bin/env python3
import sys
import os
import json

# 项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("=" * 60)
print("GW2 Log Score System - Quick Test")
print("=" * 60)
print()

# 1. 测试解析器
print("1. Testing Parser...")
try:
    from src.parser.ei_parser import EIParser
    parser = EIParser()
    data_file = os.path.join(project_root, "tests", "data.json")
    result = parser.parse_file(data_file)
    print(f"   [OK] Parse successful")
    print(f"   - Encounter: {result['encounter_name']}")
    print(f"   - Mode: {result['mode']}")
    print(f"   - Players: {len(result['players'])}")
    print()
except Exception as e:
    print(f"   [ERROR] Parse failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 2. 测试评分引擎
print("2. Testing Scoring Engine...")
try:
    from src.scoring.scoring_engine import ScoringEngine
    engine = ScoringEngine()
    
    # 构建一个简单的测试数据，确保有dps值
    test_data = {
        'mode': 'WvW',
        'players': [
            {'name': 'Player1', 'profession': 'Warrior', 'dps': 5000, 'cc': 300, 'cleanses': 5, 'strips': 2, 'downs': 0, 'deaths': 0, 'kills': 5, 'down_contribution': 10, 'buffs': {}},
            {'name': 'Player2', 'profession': 'Guardian', 'dps': 4000, 'cc': 400, 'cleanses': 10, 'strips': 5, 'downs': 1, 'deaths': 0, 'kills': 3, 'down_contribution': 5, 'buffs': {}}
        ],
        'duration': 120
    }
    
    scores = engine.calculate_scores(test_data)
    print(f"   [OK] Scoring successful")
    print(f"   - Scores: {len(scores)}")
    for s in scores:
        print(f"   - {s['player_name']}: {s['total_score']:.2f}")
    print()
except Exception as e:
    print(f"   [ERROR] Scoring failed: {e}")
    import traceback
    traceback.print_exc()

# 3. 测试数据库
print("3. Testing Database...")
try:
    from src.database.db_manager import DBManager
    test_db = os.path.join(project_root, "databases", "test_fast.db")
    if os.path.exists(test_db):
        os.remove(test_db)
    db = DBManager(test_db)
    print(f"   [OK] Database initialized")
    
    # 测试插入
    log_id = "test_log.json"
    db.save_combat_log(log_id, 'WvW', 'Test Encounter', '2025-01-01', 120, "", "Tester")
    db.save_player('Player1', 'Warrior', "", 'Player1.1234')
    db.save_player('Player2', 'Guardian', "", 'Player2.5678')
    
    print(f"   [OK] Data inserted successfully")
    print()
    
    # 查询测试
    import sqlite3
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM players')
    player_count = cursor.fetchone()[0]
    print(f"   [OK] Query successful")
    print(f"   - Player count: {player_count}")
    conn.close()
    
except Exception as e:
    print(f"   [ERROR] Database failed: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("Quick Test Complete")
print("=" * 60)
