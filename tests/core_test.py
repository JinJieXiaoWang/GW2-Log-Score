#!/usr/bin/env python3
import sys
import os
import json

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("=" * 70)
print("GW2 Log Score System - Core Functionality Test")
print("=" * 70)
print()

test_results = []
passed = 0
failed = 0

def record_test(name, passed_test, message=""):
    global passed, failed
    status = "[PASS]" if passed_test else "[FAIL]"
    if passed_test:
        passed += 1
        print(f"{status} {name}")
    else:
        failed += 1
        print(f"{status} {name} - {message}")
    test_results.append({"name": name, "passed": passed_test, "message": message})
    return passed_test

print("=" * 70)
print("Phase 1: Core Module Tests")
print("=" * 70)
print()

print("1. Testing Parser Module...")
try:
    from src.parser.ei_parser import EIParser
    parser = EIParser()
    data_file = os.path.join(project_root, "tests", "data.json")
    result = parser.parse_file(data_file)
    record_test("Parser loads data.json", result is not None)
    record_test("Parser detects WvW mode", result.get('mode') == 'WvW')
    record_test("Parser extracts players", len(result.get('players', [])) > 0)
    record_test("Parser extracts encounter name", 'Red Desert' in result.get('encounter_name', ''))
    record_test("Parser has duration", result.get('duration', 0) > 0)
except Exception as e:
    record_test("Parser Module", False, str(e))

print()
print("2. Testing Scoring Engine...")
try:
    from src.scoring.scoring_engine import ScoringEngine
    engine = ScoringEngine()

    wvw_data = {
        'mode': 'WvW',
        'players': [
            {'name': 'Player1', 'profession': 'Warrior', 'dps': 5000, 'cc': 300, 'cleanses': 5, 'strips': 2, 'downs': 0, 'deaths': 0, 'buffs': {}},
            {'name': 'Player2', 'profession': 'Guardian', 'dps': 4000, 'cc': 400, 'cleanses': 10, 'strips': 5, 'downs': 1, 'deaths': 0, 'buffs': {}}
        ],
        'duration': 120
    }

    scores = engine.calculate_scores(wvw_data)
    record_test("WvW scoring returns results", len(scores) == 2)
    record_test("Scores have total_score", all('total_score' in s for s in scores))
    record_test("Scores in valid range", all(0 <= s['total_score'] <= 100 for s in scores))

    pve_data = {
        'mode': 'PVE',
        'players': [
            {'name': 'DPS1', 'profession': 'Berserker', 'dps': 10000, 'cc': 500, 'cleanses': 0, 'strips': 0, 'downs': 0, 'deaths': 0, 'buffs': {}},
            {'name': 'Healer1', 'profession': 'Druid', 'dps': 1000, 'cc': 100, 'cleanses': 20, 'strips': 5, 'downs': 0, 'deaths': 0, 'buffs': {30328: 80}}
        ],
        'duration': 300
    }
    pve_scores = engine.calculate_scores(pve_data)
    record_test("PVE scoring returns results", len(pve_scores) == 2)
    record_test("PVE scores have valid range", all(0 <= s['total_score'] <= 100 for s in pve_scores))
except Exception as e:
    import traceback
    traceback.print_exc()
    record_test("Scoring Engine", False, str(e))

print()
print("3. Testing Database Module...")
try:
    from src.database.db_manager import DBManager
    test_db = os.path.join(project_root, "databases", "test_final.db")
    if os.path.exists(test_db):
        os.remove(test_db)

    db = DBManager(test_db)
    record_test("Database initializes", os.path.exists(test_db))

    db.add_combat_log("test_log.json", "WvW", "Test Encounter", "2025-01-01", 120, "abc123", "Tester")
    db.add_player("Player1", "Warrior", "DPS", "Player1.1234")
    db.add_player("Player2", "Guardian", "SUPPORT", "Player2.5678")
    db.add_combat_score("test_log.json", "Player1", {"dps": 80, "cc": 70, "survival": 90}, 82.5, {})
    db.add_combat_score("test_log.json", "Player2", {"dps": 60, "cc": 85, "survival": 95}, 75.0, {})

    logs = db.get_all_logs()
    record_test("Combat logs saved", len(logs) > 0)
    record_test("Log has correct mode", logs[0]['mode'] == "WvW" if logs else False)

    scores = db.get_all_scores()
    record_test("Scores saved and retrieved", len(scores) >= 2)
    record_test("Score values preserved", abs(scores[0]['total_score'] - 82.5) < 0.1 if scores else False)

except Exception as e:
    import traceback
    traceback.print_exc()
    record_test("Database Module", False, str(e))

print()
print("4. Testing File Fingerprint...")
try:
    test_content = b"test content"
    import hashlib
    h = hashlib.md5(test_content).hexdigest()
    record_test("MD5 hash is 32 chars", len(h) == 32)
    record_test("Hash is hexadecimal", h.isalnum())
except Exception as e:
    record_test("File Fingerprint", False, str(e))

print()
print("=" * 70)
print("Phase 2: Edge Case Tests")
print("=" * 70)
print()

print("5. Testing Edge Cases...")
try:
    engine = ScoringEngine()

    empty = engine.calculate_scores({'mode': 'WvW', 'players': [], 'duration': 100})
    record_test("Empty player list", len(empty) == 0)

    zero_dur = engine.calculate_scores({
        'mode': 'WvW',
        'players': [{'name': 'P1', 'profession': 'Warrior', 'dps': 1000, 'cc': 100, 'cleanses': 5, 'strips': 2, 'downs': 0, 'deaths': 0, 'buffs': {}}],
        'duration': 0
    })
    record_test("Zero duration handled", len(zero_dur) == 1)

    extreme = engine.calculate_scores({
        'mode': 'WvW',
        'players': [
            {'name': 'High', 'profession': 'Warrior', 'dps': 100000, 'cc': 100, 'cleanses': 5, 'strips': 2, 'downs': 0, 'deaths': 0, 'buffs': {}},
            {'name': 'Low', 'profession': 'Guardian', 'dps': 100, 'cc': 100, 'cleanses': 5, 'strips': 2, 'downs': 0, 'deaths': 0, 'buffs': {}}
        ],
        'duration': 120
    })
    record_test("Extreme DPS handled", len(extreme) == 2)
    record_test("DPS normalized to 100 max", all(s['scores'].get('dps', 0) <= 100 for s in extreme))

except Exception as e:
    import traceback
    traceback.print_exc()
    record_test("Edge Cases", False, str(e))

print()
print("6. Testing Exception Handling...")
try:
    parser = EIParser()
    try:
        parser.parse_file("nonexistent.json")
        record_test("FileNotFoundError", False)
    except FileNotFoundError:
        record_test("FileNotFoundError", True)

    try:
        parser.parse_file("setup.py")
        record_test("ValueError for bad format", False)
    except ValueError:
        record_test("ValueError for bad format", True)

except Exception as e:
    record_test("Exception Handling", False, str(e))

print()
print("=" * 70)
print("Phase 3: Integration Test")
print("=" * 70)
print()

print("7. Full Pipeline Test...")
try:
    parser = EIParser()
    engine = ScoringEngine()
    test_db = os.path.join(project_root, "databases", "test_integration.db")

    if os.path.exists(test_db):
        os.remove(test_db)

    db = DBManager(test_db)

    data_file = os.path.join(project_root, "tests", "data.json")
    parsed = parser.parse_file(data_file)
    record_test("Parse real data file", parsed is not None)

    scores = engine.calculate_scores(parsed)
    record_test("Score calculation", len(scores) > 0)
    record_test("All scores valid", all(0 <= s['total_score'] <= 100 for s in scores))

    log_id = parsed['log_id']
    db.add_combat_log(log_id, parsed['mode'], parsed['encounter_name'], parsed.get('date', ''), parsed['duration'], "", parsed.get('recorded_by', ''))

    for p in parsed['players']:
        db.add_player(p['name'], p['profession'], p.get('role', ''), p.get('account', ''))

    for s in scores:
        db.add_combat_score(log_id, s['player_name'], s['scores'], s['total_score'], s.get('details', {}))

    db_scores = db.get_scores_by_log(log_id)
    record_test("Database storage works", len(db_scores) > 0)

    record_test("Scores match original", abs(db_scores[0]['total_score'] - scores[0]['total_score']) < 0.1 if db_scores else False)

except Exception as e:
    import traceback
    traceback.print_exc()
    record_test("Integration Test", False, str(e))

print()
print("=" * 70)
print("FINAL RESULTS")
print("=" * 70)
print()
print(f"Total Tests: {passed + failed}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Success Rate: {passed * 100 / (passed + failed):.1f}%")
print()

if failed > 0:
    print("Failed Tests:")
    for r in test_results:
        if not r['passed']:
            print(f"  - {r['name']}: {r['message']}")
    print()

print("=" * 70)
sys.exit(0 if failed == 0 else 1)
