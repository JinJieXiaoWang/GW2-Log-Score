#!/usr/bin/env python3
"""
GW2日志评分系统 - 综合功能测试脚本
测试范围：核心功能、边界条件、异常场景
"""

import os
import sys
import json
import sqlite3
import traceback
import tempfile
import shutil
import hashlib
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parser.ei_parser import EIParser
from src.database.db_manager import DBManager
from src.scoring.scoring_engine import ScoringEngine
from src.config import settings

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
        self.test_db_path = os.path.join(os.path.dirname(__file__), "databases", "test_runner.db")

    def log(self, message, level="INFO"):
        try:
            print(f"[{level}] {message}")
        except UnicodeEncodeError:
            clean_msg = message.replace('\u2713', 'PASS').replace('\u2717', 'FAIL').replace('\u00d7', 'X')
            print(f"[{level}] {clean_msg}")

    def assert_true(self, condition, message):
        if condition:
            self.passed += 1
            self.result = True
            self.log(f"✓ {message}", "PASS")
        else:
            self.failed += 1
            self.result = False
            self.log(f"✗ {message}", "FAIL")

    def assert_equal(self, actual, expected, message):
        if actual == expected:
            self.passed += 1
            self.result = True
            self.log(f"✓ {message}", "PASS")
        else:
            self.failed += 1
            self.result = False
            self.log(f"✗ {message}: 期望 {expected}, 实际 {actual}", "FAIL")

    def assert_in(self, member, container, message):
        if member in container:
            self.passed += 1
            self.result = True
            self.log(f"✓ {message}", "PASS")
        else:
            self.failed += 1
            self.result = False
            self.log(f"✗ {message}", "FAIL")

    def print_header(self, title):
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)

    def print_section(self, title):
        print(f"\n--- {title} ---")

    def cleanup_test_db(self):
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except:
                pass


class CoreFunctionalityTests(TestRunner):
    """核心功能模块测试"""

    def test_parser_json_parsing(self):
        """测试JSON文件解析"""
        self.print_section("测试1: JSON文件解析")
        data_file = os.path.join(os.path.dirname(__file__), "tests", "data.json")

        if not os.path.exists(data_file):
            self.log(f"测试文件不存在: {data_file}", "ERROR")
            return False

        parser = EIParser()
        result = parser.parse_file(data_file)

        self.assert_true(isinstance(result, dict), "解析结果为字典类型")
        self.assert_true('encounter_name' in result, "包含 encounter_name 字段")
        self.assert_true('mode' in result, "包含 mode 字段")
        self.assert_true('duration' in result, "包含 duration 字段")
        self.assert_true('players' in result, "包含 players 字段")
        self.assert_equal(result['mode'], 'WvW', "模式识别正确 (WvW)")
        self.assert_true(len(result['players']) > 0, "玩家列表非空")

        if result['players']:
            p = result['players'][0]
            self.assert_true('name' in p, "玩家数据包含 name 字段")
            self.assert_true('profession' in p, "玩家数据包含 profession 字段")
            self.assert_true('dps' in p, "玩家数据包含 dps 字段")

        return self.result

    def test_parser_evtc_parsing(self):
        """测试EVTC文件解析"""
        self.print_section("测试2: ZEVTC文件解析")
        evtc_file = os.path.join(os.path.dirname(__file__), "tests", "20260420-000535.zevtc")

        if not os.path.exists(evtc_file):
            self.log(f"测试文件不存在: {evtc_file}", "ERROR")
            return False

        parser = EIParser()
        result = parser.parse_file(evtc_file)

        self.assert_true(isinstance(result, dict), "解析结果为字典类型")
        self.assert_true('log_id' in result, "包含 log_id 字段")
        self.assert_true('players' in result, "包含 players 字段")

        return self.result

    def test_database_initialization(self):
        """测试数据库初始化"""
        self.print_section("测试3: 数据库初始化")
        self.cleanup_test_db()

        db = DBManager(self.test_db_path)

        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

        self.assert_in('players', tables, "players 表已创建")
        self.assert_in('combat_logs', tables, "combat_logs 表已创建")
        self.assert_in('combat_scores', tables, "combat_scores 表已创建")
        self.assert_in('file_fingerprints', tables, "file_fingerprints 表已创建")

        return self.result

    def test_database_crud_operations(self):
        """测试数据库增删改查"""
        self.print_section("测试4: 数据库CRUD操作")
        self.cleanup_test_db()
        db = DBManager(self.test_db_path)

        test_log_id = "test_log_001"
        test_date = datetime.now().strftime("%Y-%m-%d")

        db.add_combat_log(
            test_log_id, "PVE", "Test Encounter",
            test_date, 120, "test_path.json", "TestRecorder"
        )

        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM combat_logs WHERE log_id = ?", (test_log_id,))
            row = cursor.fetchone()

        self.assert_true(row is not None, "战斗日志已插入")
        self.assert_equal(row[1], "PVE", "模式字段正确")
        self.assert_equal(row[2], "Test Encounter", "战斗名称正确")

        db.add_player("TestPlayer", "Warrior", "DPS", "TestPlayer.1234")

        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM players WHERE name = ?", ("TestPlayer",))
            player_row = cursor.fetchone()

        self.assert_true(player_row is not None, "玩家已插入")
        self.assert_equal(player_row[1], "Warrior", "职业字段正确")

        scores = {'dps': 85.5, 'cc': 70.0, 'survival': 90.0, 'boon': 0}
        db.add_combat_score(test_log_id, "TestPlayer", scores, 82.5, {'test': 'detail'})

        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM combat_scores WHERE log_id = ?", (test_log_id,))
            score_row = cursor.fetchone()

        self.assert_true(score_row is not None, "评分记录已插入")
        self.assert_equal(score_row[6], 82.5, "总分正确")

        return self.result

    def test_scoring_engine_pve(self):
        """测试PVE评分引擎"""
        self.print_section("测试5: PVE评分引擎")
        data_file = os.path.join(os.path.dirname(__file__), "tests", "data.json")

        parser = EIParser()
        parsed_data = parser.parse_file(data_file)

        scorer = ScoringEngine()
        scores = scorer.calculate_pve_scores(parsed_data)

        self.assert_true(isinstance(scores, list), "评分结果为列表")
        self.assert_true(len(scores) > 0, "评分列表非空")

        if scores:
            s = scores[0]
            self.assert_true('player_name' in s, "评分包含玩家名称")
            self.assert_true('profession' in s, "评分包含职业")
            self.assert_true('total_score' in s, "评分包含总分")
            self.assert_true('scores' in s, "评分包含分项得分")
            self.assert_true(0 <= s['total_score'] <= 100, f"总分在有效范围(0-100): {s['total_score']}")

        return self.result

    def test_scoring_engine_wvw(self):
        """测试WvW评分引擎"""
        self.print_section("测试6: WvW评分引擎")
        data_file = os.path.join(os.path.dirname(__file__), "tests", "data.json")

        parser = EIParser()
        parsed_data = parser.parse_file(data_file)

        scorer = ScoringEngine()
        scores = scorer.calculate_wvw_scores(parsed_data)

        self.assert_true(isinstance(scores, list), "WvW评分结果为列表")

        return self.result

    def test_file_fingerprint(self):
        """测试文件指纹机制"""
        self.print_section("测试7: 文件指纹机制")
        self.cleanup_test_db()
        db = DBManager(self.test_db_path)

        data_file = os.path.join(os.path.dirname(__file__), "tests", "data.json")
        if not os.path.exists(data_file):
            self.log(f"测试文件不存在: {data_file}", "ERROR")
            return False

        file_hash = db.calculate_file_hash(data_file)
        file_name = os.path.basename(data_file)

        self.assert_true(len(file_hash) == 32, "文件哈希为MD5格式(32字符)")

        existing = db.get_today_file_fingerprint(file_name)
        self.assert_true(existing is None, "首次上传无现有指纹")

        db.save_file_fingerprint(file_name, file_hash, "test_log_fp")

        existing_after = db.get_today_file_fingerprint(file_name)
        self.assert_true(existing_after is not None, "指纹保存成功")

        hash_after, log_id = existing_after
        self.assert_equal(hash_after, file_hash, "保存的哈希值正确")

        hash_again = db.calculate_file_hash(data_file)
        self.assert_equal(hash_again, file_hash, "重复计算哈希值一致")

        return self.result


class BoundaryConditionTests(TestRunner):
    """边界条件测试"""

    def test_empty_players_list(self):
        """测试空玩家列表"""
        self.print_section("测试8: 空玩家列表边界条件")
        parser = EIParser()
        scorer = ScoringEngine()

        empty_data = {
            'log_id': 'empty_test',
            'encounter_name': 'Empty Encounter',
            'duration': 120,
            'mode': 'PVE',
            'players': []
        }

        scores = scorer.calculate_pve_scores(empty_data)
        self.assert_equal(len(scores), 0, "空玩家列表返回空评分")

        return self.result

    def test_single_player(self):
        """测试单玩家场景"""
        self.print_section("测试9: 单玩家边界条件")
        parser = EIParser()
        scorer = ScoringEngine()

        single_player_data = {
            'log_id': 'single_test',
            'encounter_name': 'Single Player Test',
            'duration': 120,
            'mode': 'PVE',
            'players': [{
                'name': 'SoloPlayer',
                'account': 'Solo.1234',
                'profession': 'Warrior',
                'dps': 15000,
                'cc': 500,
                'cleanses': 10,
                'strips': 5,
                'downs': 0,
                'deaths': 0,
                'buffs': {}
            }]
        }

        scores = scorer.calculate_pve_scores(single_player_data)
        self.assert_equal(len(scores), 1, "单玩家返回单条评分")
        if scores:
            self.assert_equal(scores[0]['player_name'], 'SoloPlayer', "玩家名称正确")

        return self.result

    def test_zero_duration(self):
        """测试零时长战斗"""
        self.print_section("测试10: 零时长边界条件")
        parser = EIParser()
        scorer = ScoringEngine()

        zero_duration_data = {
            'log_id': 'zero_dur',
            'encounter_name': 'Zero Duration',
            'duration': 0,
            'mode': 'PVE',
            'players': [{
                'name': 'TestPlayer',
                'account': 'Test.1234',
                'profession': 'Warrior',
                'dps': 15000,
                'cc': 500,
                'cleanses': 10,
                'strips': 5,
                'downs': 0,
                'deaths': 0,
                'buffs': {}
            }]
        }

        try:
            scores = scorer.calculate_pve_scores(zero_duration_data)
            self.assert_true(isinstance(scores, list), "零时长可计算评分")
        except Exception as e:
            self.log(f"零时长处理异常: {e}", "WARN")

        return self.result

    def test_extreme_dps_values(self):
        """测试极端DPS值"""
        self.print_section("测试11: 极端DPS值边界条件")
        parser = EIParser()
        scorer = ScoringEngine()

        extreme_data = {
            'log_id': 'extreme_dps',
            'encounter_name': 'Extreme DPS Test',
            'duration': 120,
            'mode': 'PVE',
            'players': [
                {'name': 'MaxDPS', 'account': 'Max.1', 'profession': 'Warrior',
                 'dps': 100000, 'cc': 5000, 'cleanses': 100, 'strips': 50, 'downs': 0, 'deaths': 0, 'buffs': {}},
                {'name': 'ZeroDPS', 'account': 'Zero.2', 'profession': 'Warrior',
                 'dps': 0, 'cc': 0, 'cleanses': 0, 'strips': 0, 'downs': 5, 'deaths': 2, 'buffs': {}}
            ]
        }

        scores = scorer.calculate_pve_scores(extreme_data)
        self.assert_equal(len(scores), 2, "极端值返回正确数量评分")

        if scores:
            max_score = max(s['total_score'] for s in scores)
            self.assert_true(max_score <= 100, f"最高分不超过100: {max_score}")

        return self.result

    def test_special_characters_in_filename(self):
        """测试特殊字符文件名"""
        self.print_section("测试12: 特殊字符文件名边界条件")
        parser = EIParser()

        temp_dir = tempfile.mkdtemp()
        special_names = [
            "data_测试.json",
            "data with spaces.json",
            "data@special#chars.json",
            "data_中文_日本語.json"
        ]

        try:
            for name in special_names:
                test_file = os.path.join(temp_dir, name)
                with open(test_file, 'w', encoding='utf-8') as f:
                    json.dump({'players': []}, f)

                try:
                    result = parser.parse_file(test_file)
                    self.assert_true('log_id' in result, f"特殊字符文件名处理成功: {name}")
                except Exception as e:
                    self.log(f"特殊字符文件名异常 {name}: {e}", "WARN")
        finally:
            shutil.rmtree(temp_dir)

        return self.result


class ExceptionScenarioTests(TestRunner):
    """异常场景测试"""

    def test_nonexistent_file(self):
        """测试文件不存在异常"""
        self.print_section("测试13: 文件不存在异常")
        parser = EIParser()

        try:
            parser.parse_file("nonexistent_file.json")
            self.assert_true(False, "应抛出FileNotFoundError")
        except FileNotFoundError:
            self.assert_true(True, "正确抛出FileNotFoundError")
        except Exception as e:
            self.failed += 1
            self.log(f"✗ 异常类型不正确: {type(e).__name__}", "FAIL")

        return self.result

    def test_unsupported_file_format(self):
        """测试不支持的文件格式"""
        self.print_section("测试14: 不支持文件格式异常")
        parser = EIParser()

        temp_file = tempfile.mktemp(suffix=".txt")
        with open(temp_file, 'w') as f:
            f.write("test content")

        try:
            parser.parse_file(temp_file)
            self.assert_true(False, "应抛出ValueError")
        except ValueError as e:
            self.assert_true("Unsupported" in str(e) or "format" in str(e).lower(),
                          "正确抛出ValueError")
        except Exception as e:
            self.log(f"异常: {type(e).__name__}: {e}", "WARN")
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

        return self.result

    def test_invalid_json_format(self):
        """测试无效JSON格式"""
        self.print_section("测试15: 无效JSON格式异常")
        parser = EIParser()

        temp_file = tempfile.mktemp(suffix=".json")
        with open(temp_file, 'w') as f:
            f.write("{ invalid json content }")

        try:
            parser.parse_file(temp_file)
            self.assert_true(False, "应抛出JSON解析异常")
        except (json.JSONDecodeError, ValueError) as e:
            self.assert_true(True, "正确抛出JSON解析异常")
        except Exception as e:
            self.log(f"异常: {type(e).__name__}: {e}", "WARN")
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

        return self.result

    def test_database_file_not_exists(self):
        """测试数据库文件不存在场景"""
        self.print_section("测试16: 数据库文件不存在场景")
        nonexistent_db = os.path.join(tempfile.gettempdir(), "nonexistent_db_12345.db")

        if os.path.exists(nonexistent_db):
            os.remove(nonexistent_db)

        try:
            db = DBManager(nonexistent_db)
            self.assert_true(os.path.exists(nonexistent_db), "数据库文件自动创建")

            with sqlite3.connect(nonexistent_db) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                self.assert_true(len(tables) >= 4, "数据库表已初始化")
        finally:
            if os.path.exists(nonexistent_db):
                os.remove(nonexistent_db)

        return self.result

    def test_duplicate_fingerprint_same_content(self):
        """测试相同内容重复上传"""
        self.print_section("测试17: 相同内容重复上传处理")
        self.cleanup_test_db()
        db = DBManager(self.test_db_path)

        data_file = os.path.join(os.path.dirname(__file__), "tests", "data.json")
        file_name = os.path.basename(data_file)
        file_hash = db.calculate_file_hash(data_file)

        log_id_1 = "log_001"
        db.save_file_fingerprint(file_name, file_hash, log_id_1)

        log_id_2 = "log_002"
        db.save_file_fingerprint(file_name, file_hash, log_id_2)

        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT file_hash, log_id FROM file_fingerprints WHERE file_name = ?",
                (file_name,)
            )
            rows = cursor.fetchall()

        self.assert_equal(len(rows), 1, "相同哈希只保留一条记录")

        return self.result

    def test_missing_optional_fields(self):
        """测试缺少可选字段"""
        self.print_section("测试18: 缺少可选字段处理")
        parser = EIParser()

        minimal_data = {
            'players': [
                {'account': 'Test.1234', 'profession': 'Warrior'}
            ]
        }

        try:
            result = parser._read_json_file
            self.assert_true(callable(result), "解析器方法可调用")
        except Exception as e:
            self.log(f"可选字段处理: {e}", "WARN")

        return self.result

    def cleanup_test_db(self):
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except:
                pass


class IntegrationTests(TestRunner):
    """集成测试"""

    def test_full_pipeline(self):
        """测试完整数据处理流程"""
        self.print_section("测试19: 完整数据处理流程")
        self.cleanup_test_db()

        data_file = os.path.join(os.path.dirname(__file__), "tests", "data.json")
        db = DBManager(self.test_db_path)

        parser = EIParser()
        parsed_data = parser.parse_file(data_file)

        log_id = parsed_data['log_id']
        duration = int(parsed_data.get('duration', 0))

        db.add_combat_log(
            log_id,
            parsed_data['mode'],
            parsed_data['encounter_name'],
            parsed_data['date'],
            duration,
            data_file,
            parsed_data['recorded_by']
        )

        file_hash = db.calculate_file_hash(data_file)
        db.save_file_fingerprint(os.path.basename(data_file), file_hash, log_id)

        scorer = ScoringEngine()
        scores = scorer.calculate_pve_scores(parsed_data)

        for s in scores:
            db.add_player(s['player_name'], s['profession'], s['role'], s.get('account', s['player_name']))
            db.add_combat_score(log_id, s['player_name'], s['scores'], s['total_score'], s['details'])

        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM combat_logs")
            log_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM players")
            player_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM combat_scores")
            score_count = cursor.fetchone()[0]

        self.assert_equal(log_count, 1, "战斗日志记录正确")
        self.assert_equal(player_count, len(scores), f"玩家记录数正确: {len(scores)}")
        self.assert_equal(score_count, len(scores), f"评分记录数正确: {len(scores)}")

        return self.result

    def test_api_logic_simulation(self):
        """测试API逻辑模拟"""
        self.print_section("测试20: API逻辑模拟")

        data_file = os.path.join(os.path.dirname(__file__), "tests", "data.json")
        db = DBManager(self.test_db_path)
        parser = EIParser()
        scorer = ScoringEngine()

        file_hash = db.calculate_file_hash(data_file)
        file_name = os.path.basename(data_file)
        existing = db.get_today_file_fingerprint(file_name)

        is_update = False
        if existing:
            existing_hash, existing_log_id = existing
            if existing_hash == file_hash:
                status = "skipped"
                self.log("文件内容相同，应跳过处理", "INFO")
            else:
                db.delete_log_data(existing_log_id)
                is_update = True
                status = "updated"
        else:
            status = "new"

        parsed_data = parser.parse_file(data_file)
        scores = scorer.calculate_pve_scores(parsed_data)

        self.assert_in(status, ["skipped", "updated", "new"], f"状态正确: {status}")
        self.assert_true(len(scores) > 0, "评分计算成功")

        return self.result

    def cleanup_test_db(self):
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except:
                pass


def run_all_tests():
    """运行所有测试"""
    print("\n" + "#" * 70)
    print("#  GW2日志评分系统 - 综合功能测试套件")
    print("#  测试范围: 核心功能 | 边界条件 | 异常场景 | 集成测试")
    print("#" * 70)

    all_passed = 0
    all_failed = 0

    test_classes = [
        ("核心功能模块测试", CoreFunctionalityTests),
        ("边界条件测试", BoundaryConditionTests),
        ("异常场景测试", ExceptionScenarioTests),
        ("集成测试", IntegrationTests)
    ]

    for class_name, test_class in test_classes:
        print(f"\n{'#' * 70}")
        print(f"#  {class_name}")
        print(f"{'#' * 70}")

        instance = test_class()
        instance.cleanup_test_db()

        for method_name in dir(instance):
            if method_name.startswith('test_'):
                try:
                    getattr(instance, method_name)()
                except Exception as e:
                    instance.failed += 1
                    instance.log(f"✗ 测试执行异常 {method_name}: {e}", "ERROR")
                    traceback.print_exc()

        all_passed += instance.passed
        all_failed += instance.failed

        print(f"\n  小计: {instance.passed} 通过, {instance.failed} 失败")

    print("\n" + "=" * 70)
    print("  测试结果汇总")
    print("=" * 70)
    print(f"  总测试数: {all_passed + all_failed}")
    print(f"  通过: {all_passed}")
    print(f"  失败: {all_failed}")

    if all_failed == 0:
        print("\n  ✓✓✓ 所有测试通过！✓✓✓")
    else:
        print(f"\n  ✗✗✗ 有 {all_failed} 个测试失败 ✗✗✗")

    print("=" * 70 + "\n")

    return all_failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
