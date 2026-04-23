#!/usr/bin/env python3
import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("Debugging Scoring Engine")
print("-" * 50)

# 测试数据
test_data = {
    'mode': 'WvW',
    'players': [
        {'name': 'Player1', 'profession': 'Warrior', 'dps': 5000, 'cc': 300, 'cleanses': 5, 'strips': 2, 'downs': 0, 'deaths': 0, 'buffs': {}},
    ],
    'duration': 120
}

# 手动加载scoring engine代码检查
from src.scoring.scoring_engine import ScoringEngine
engine = ScoringEngine()

# 让我们打印所有内容
players = test_data['players']
for p in players:
    print(f"Player: {p['name']}, Profession: {p['profession']}")
    
    from src.config.config_loader import PROF_ROLES
    role = PROF_ROLES.get(p['profession'], 'DPS')
    print(f"Role from config: {role}")
    
    from src.config.config_loader import SCORING_CONFIG
    cfg = SCORING_CONFIG['WvW'].get(role, SCORING_CONFIG['WvW']['DPS'])
    print(f"Config for role: {cfg}")
    print()

try:
    scores = engine.calculate_scores(test_data)
    print("Success! Scores:")
    for s in scores:
        print(f"{s['player_name']}: {s['total_score']}")
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
