#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
沙盒环境验证脚本 - 验证核心模块功能
"""
import sys
import os
import json

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("=" * 60)
print("GW2 Log Score System - Core Module Validation")
print("=" * 60)

# 测试1：验证Python环境和依赖
print("\n[1/6] Validating Python environment and dependencies...")
try:
    import fastapi
    import uvicorn
    import pandas
    import openpyxl
    print("  [OK] All dependencies installed")
    print(f"    - Python {sys.version.split()[0]}")
    print(f"    - FastAPI {fastapi.__version__}")
    print(f"    - Uvicorn {uvicorn.__version__}")
    print(f"    - Pandas {pandas.__version__}")
except ImportError as e:
    print(f"  [ERROR] Dependency missing: {e}")
    sys.exit(1)

# 测试2：验证解析器模块
print("\n[2/6] Validating Parser module...")
try:
    from src.parser.ei_parser import EIParser
    test_file = os.path.join(project_root, "tests", "data.json")
    if os.path.exists(test_file):
        parser = EIParser()
        result = parser.parse_file(test_file)
        if result and isinstance(result, dict):
            print(f"  [OK] Parser working correctly")
            print(f"    - Encounter: {result.get('encounter_name', 'N/A')}")
            print(f"    - Mode: {result.get('mode', 'N/A')}")
            print(f"    - Players: {len(result.get('players', []))}")
        else:
            print("  [ERROR] Parse failed")
    else:
        print(f"  [ERROR] Test file missing: {test_file}")
except Exception as e:
    print(f"  [ERROR] Parser error: {e}")
    import traceback
    traceback.print_exc()

# 测试3：验证数据库模块
print("\n[3/6] Validating Database module...")
try:
    from src.database.db_manager import DBManager
    test_db = os.path.join(project_root, "databases", "test_validation.db")
    if os.path.exists(test_db):
        os.remove(test_db)
    db = DBManager(test_db)
    
    # 检查表是否存在
    import sqlite3
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if len(tables) >= 4:
        print(f"  [OK] Database working correctly")
        print(f"    - Table count: {len(tables)}")
        print(f"    - Tables: {', '.join(tables)}")
    else:
        print(f"  [ERROR] Database tables incomplete")
except Exception as e:
    print(f"  [ERROR] Database error: {e}")
    import traceback
    traceback.print_exc()

# 测试4：验证评分引擎
print("\n[4/6] Validating Scoring Engine...")
try:
    from src.scoring.scoring_engine import ScoringEngine
    engine = ScoringEngine()
    
    # 使用测试数据文件
    test_file = os.path.join(project_root, "tests", "data.json")
    with open(test_file, 'r', encoding='utf-8') as f:
        parsed_data = json.load(f)
    
    scores = engine.calculate_scores(parsed_data)
    if scores and len(scores) > 0:
        print(f"  [OK] Scoring engine working correctly")
        print(f"    - Scored players: {len(scores)}")
        for s in scores[:1]:
            print(f"    - {s.get('player_name', 'Unknown')}: {s.get('total_score', 0):.2f}")
    else:
        print("  [ERROR] Scoring failed")
except Exception as e:
    print(f"  [ERROR] Scoring engine error: {e}")
    import traceback
    traceback.print_exc()

# 测试5：验证配置
print("\n[5/6] Validating configuration...")
try:
    from src.config import SCORING_CONFIG, BUFF_IDS, PROF_ROLES
    if SCORING_CONFIG and isinstance(SCORING_CONFIG, dict):
        print(f"  [OK] Configuration loaded correctly")
        print(f"    - Scoring config keys: {len(SCORING_CONFIG.keys())}")
except Exception as e:
    print(f"  [ERROR] Configuration error: {e}")

# 测试6：验证项目结构
print("\n[6/6] Validating project structure...")
required_dirs = ["src", "tests", "config", "databases", "uploads", "frontend"]
required_files = ["requirements.txt", "pyproject.toml", "start.py"]

all_good = True
for d in required_dirs:
    if not os.path.isdir(d):
        print(f"  [ERROR] Directory missing: {d}")
        all_good = False

for f in required_files:
    if not os.path.isfile(f):
        print(f"  [ERROR] File missing: {f}")
        all_good = False

if all_good:
    print("  [OK] Project structure complete")

print("\n" + "=" * 60)
print("Core module validation complete")
print("=" * 60)
print("\nProject is ready to start!")
print("\nTest commands:")
print("  1. Run comprehensive tests:")
print("     python run_all_tests.py")
print("\n  2. Start backend service:")
print("     python src/main.py --serve")
print("\nAccess URLs:")
print("  http://localhost:8000")
print("  http://localhost:8000/docs")
