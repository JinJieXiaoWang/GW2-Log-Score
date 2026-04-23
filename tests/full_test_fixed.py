import json
import sys
import traceback
import os
from parser.ei_parser import EIParser
from database.db_manager import DBManager
from scoring.scoring_engine import ScoringEngine

def full_test_with_fix():
    print("=" * 80)
    print("完整解析流程测试（修复版）")
    print("=" * 80)

    db_path = 'test_gw2_logs.db'

    # 清理旧测试文件
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("\n已清理旧的测试数据库")
        except:
            pass

    try:
        # 步骤 1: 解析
        print("\n[步骤 1] 解析 JSON 文件...")
        parser = EIParser()
        parsed_data = parser.parse_file('data.json')

        print(f"✓ 解析成功")
        print(f"  - 战斗名称: {parsed_data['encounter_name']}")
        print(f"  - 模式: {parsed_data['mode']}")
        print(f"  - 时长: {parsed_data['duration']} 秒")
        print(f"  - 记录者: {parsed_data['recorded_by']}")
        print(f"  - 日期: {parsed_data['date']}")
        print(f"  - 玩家数量: {len(parsed_data['players'])}")

        if parsed_data['players']:
            print(f"\n  第一个玩家:")
            p = parsed_data['players'][0]
            print(f"    - 名称: {p['name']}")
            print(f"    - 职业: {p['profession']}")
            print(f"    - DPS: {p['dps']}")
            print(f"    - CC: {p['cc']}")
            print(f"    - Downs: {p['downs']}")
            print(f"    - Deaths: {p['deaths']}")
            print(f"    - Cleanses: {p['cleanses']}")
            print(f"    - Strips: {p['strips']}")
            print(f"    - Buffs 数量: {len(p['buffs'])}")

        # 步骤 2: 数据库存储
        print("\n[步骤 2] 初始化数据库...")
        db = DBManager(db_path)
        print("✓ 数据库初始化成功")

        print("\n[步骤 3] 存储战斗日志信息...")
        db.add_combat_log(
            parsed_data['log_id'],
            parsed_data['mode'],
            parsed_data['encounter_name'],
            parsed_data['date'],
            int(parsed_data['duration']),
            'data.json',
            parsed_data['recorded_by']
        )
        print("✓ 战斗日志存储成功")

        # 步骤 3: 评分计算
        print("\n[步骤 4] 计算评分...")
        scorer = ScoringEngine()

        # 根据模式选择评分方法
        if 'WvW' in parsed_data['mode']:
            print("  检测到 WvW 模式，使用 WvW 评分规则")
            scores = scorer.calculate_wvw_scores(parsed_data)
        elif 'PvP' in parsed_data['mode']:
            print("  检测到 PvP 模式（暂不支持）")
            scores = []
        else:
            print("  检测到 PVE 模式，使用 PVE 评分规则")
            scores = scorer.calculate_pve_scores(parsed_data)

        print(f"✓ 评分计算完成，共 {len(scores)} 个玩家")

        if scores:
            print(f"\n  第一个玩家评分:")
            s = scores[0]
            print(f"    - 玩家: {s['player_name']}")
            print(f"    - 职业: {s['profession']}")
            print(f"    - 定位: {s['role']}")
            print(f"    - 总分: {s['total_score']}")
            print(f"    - 分项得分: {s['scores']}")

        # 步骤 4: 存储评分
        print("\n[步骤 5] 存储评分数据...")
        for s in scores:
            db.add_player(s['player_name'], s['profession'], s['role'])
            db.add_combat_score(
                parsed_data['log_id'],
                s['player_name'],
                s['scores'],
                s['total_score'],
                s['details']
            )
        print(f"✓ 成功存储 {len(scores)} 个玩家的评分")

        # 步骤 5: 验证数据
        print("\n[步骤 6] 验证数据库数据...")
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM combat_logs")
            log_count = cursor.fetchone()[0]
            print(f"  - 战斗日志数: {log_count}")

            cursor.execute("SELECT COUNT(*) FROM players")
            player_count = cursor.fetchone()[0]
            print(f"  - 玩家数: {player_count}")

            cursor.execute("SELECT COUNT(*) FROM combat_scores")
            score_count = cursor.fetchone()[0]
            print(f"  - 评分记录数: {score_count}")

            # 查询第一条记录
            cursor.execute("""
                SELECT cl.encounter_name, cl.mode, cs.player_name, cs.total_score 
                FROM combat_scores cs
                JOIN combat_logs cl ON cs.log_id = cl.log_id
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                print(f"\n  示例记录:")
                print(f"    - 战斗: {row[0]}")
                print(f"    - 模式: {row[1]}")
                print(f"    - 玩家: {row[2]}")
                print(f"    - 总分: {row[3]}")

        print("\n" + "=" * 80)
        print("✓✓✓ 完整测试通过！所有步骤成功 ✓✓✓")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗✗✗ 测试失败 ✗✗✗")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {e}")
        print("\n完整堆栈跟踪:")
        print("-" * 80)
        traceback.print_exc()
        print("-" * 80)
        sys.exit(1)
    finally:
        # 清理测试数据库
        import gc
        gc.collect()  # 强制垃圾回收，确保数据库连接关闭
        
        if os.path.exists(db_path):
            try:
                # 等待一下确保连接关闭
                import time
                time.sleep(1)
                os.remove(db_path)
                print("\n已清理测试数据库")
            except Exception as e:
                print(f"\n警告: 无法清理测试数据库 - {e}")
                print("提示: 这不影响实际功能，可以手动删除 test_gw2_logs.db")

    if __name__ == "__main__":
        full_test_with_fix()
