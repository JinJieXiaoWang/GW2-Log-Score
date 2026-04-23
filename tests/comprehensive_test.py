#!/usr/bin/env python3
import sys
import os
import json
import tempfile

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("=" * 70)
print("GW2 Log Score System - Comprehensive Functional Test")
print("=" * 70)
print()

test_results = []
passed = 0
failed = 0

def test_result(name, passed_test, message=""):
    global passed, failed
    status = "PASS" if passed_test else "FAIL"
    if passed_test:
        passed += 1
        print(f"[{status}] {name}")
    else:
        failed += 1
        print(f"[{status}] {name} - {message}")
    test_results.append({"name": name, "passed": passed_test, "message": message})
    return passed_test

print("=" * 70)
print("Phase 1: Core Module Validation")
print("=" * 70)
print()

print("1. Testing Parser Module...")
try:
    from src.parser.ei_parser import EIParser
    parser = EIParser()
    data_file = os.path.join(project_root, "tests", "data.json")
    result = parser.parse_file(data_file)
    test_result("Parser loads data.json successfully", result is not None)
    test_result("Parser detects correct mode (WvW)", result.get('mode') == 'WvW')
    test_result("Parser extracts player data", len(result.get('players', [])) > 0)
    test_result("Parser extracts encounter name", 'Red Desert' in result.get('encounter_name', ''))
except Exception as e:
    test_result("Parser Module", False, str(e))

print()
print("2. Testing Scoring Engine...")
try:
    from src.scoring.scoring_engine import ScoringEngine
    engine = ScoringEngine()

    wvw_test_data = {
        'mode': 'WvW',
        'players': [
            {'name': 'Player1', 'profession': 'Warrior', 'dps': 5000, 'cc': 300, 'cleanses': 5, 'strips': 2, 'downs': 0, 'deaths': 0, 'buffs': {}},
            {'name': 'Player2', 'profession': 'Guardian', 'dps': 4000, 'cc': 400, 'cleanses': 10, 'strips': 5, 'downs': 1, 'deaths': 0, 'buffs': {}}
        ],
        'duration': 120
    }

    scores = engine.calculate_scores(wvw_test_data)
    test_result("Scoring engine calculates WvW scores", len(scores) == 2)
    test_result("Scores have total_score field", all('total_score' in s for s in scores))
    test_result("Scores are within valid range", all(0 <= s['total_score'] <= 100 for s in scores))

    pve_test_data = {
        'mode': 'PVE',
        'players': [
            {'name': 'DPS1', 'profession': 'Berserker', 'dps': 10000, 'cc': 500, 'cleanses': 0, 'strips': 0, 'downs': 0, 'deaths': 0, 'buffs': {}},
            {'name': 'Healer1', 'profession': 'Druid', 'dps': 1000, 'cc': 100, 'cleanses': 20, 'strips': 5, 'downs': 0, 'deaths': 0, 'buffs': {30328: 80}}
        ],
        'duration': 300
    }
    pve_scores = engine.calculate_scores(pve_test_data)
    test_result("Scoring engine calculates PVE scores", len(pve_scores) == 2)
except Exception as e:
    import traceback
    traceback.print_exc()
    test_result("Scoring Engine", False, str(e))

print()
print("3. Testing Database Module...")
try:
    from src.database.db_manager import DBManager
    test_db = os.path.join(project_root, "databases", "test_comprehensive.db")
    if os.path.exists(test_db):
        os.remove(test_db)

    db = DBManager(test_db)
    test_result("Database initializes successfully", os.path.exists(test_db))

    db.save_combat_log("test_log.json", "WvW", "Test Encounter", "2025-01-01", 120, "abc123", "Tester")
    db.save_player("Player1", "Warrior", "DPS", "Player1.1234")
    db.save_player("Player2", "Guardian", "SUPPORT", "Player2.5678")

    db.save_score("test_log.json", "Player1", 80, 70, 90, 0, 82.5, "{}")
    db.save_score("test_log.json", "Player2", 60, 85, 95, 0, 75.0, "{}")

    logs = db.get_all_logs()
    test_result("Database saves combat logs", len(logs) > 0)

    scores = db.get_all_scores()
    test_result("Database saves and retrieves scores", len(scores) >= 2)

    db_path_result = db.db_path
    test_result("Database path property works", db_path_result is not None)

except Exception as e:
    import traceback
    traceback.print_exc()
    test_result("Database Module", False, str(e))

print()
print("4. Testing File Hash...")
try:
    import hashlib
    test_content = b"test content for hashing"
    hash_obj = hashlib.md5()
    hash_obj.update(test_content)
    expected_hash = hash_obj.hexdigest()
    test_result("MD5 hash generates 32-char string", len(expected_hash) == 32)
except Exception as e:
    test_result("File Hash", False, str(e))

print()
print("=" * 70)
print("Phase 2: API Endpoint Validation")
print("=" * 70)
print()

import requests
BASE_URL = "http://localhost:8000/api"

print("5. Testing API Endpoints...")
try:
    response = requests.get(f"{BASE_URL}/logs")
    test_result("GET /api/logs returns 200", response.status_code == 200)

    response = requests.get(f"{BASE_URL}/attendance")
    test_result("GET /api/attendance returns 200", response.status_code == 200)
except Exception as e:
    test_result("API Endpoints", False, str(e))

print()
print("6. Testing File Upload Flow...")
try:
    test_file_path = os.path.join(project_root, "tests", "data.json")
    with open(test_file_path, 'rb') as f:
        files = {'file': ('data.json', f, 'application/json')}
        response = requests.post(f"{BASE_URL}/upload", files=files)

    test_result("POST /api/upload accepts JSON file", response.status_code == 200)

    if response.status_code == 200:
        data = response.json()
        test_result("Upload returns success status", data.get('status') == 'success')
        test_result("Upload returns player count", 'player_count' in data)
        test_result("Upload returns encounter name", 'encounter' in data)
except Exception as e:
    test_result("File Upload Flow", False, str(e))

print()
print("=" * 70)
print("Phase 3: Edge Case Tests")
print("=" * 70)
print()

print("7. Testing Edge Cases...")
try:
    edge_parser = EIParser()

    empty_data = {'players': []}
    engine = ScoringEngine()
    empty_scores = engine.calculate_scores(empty_data)
    test_result("Empty player list returns empty scores", len(empty_scores) == 0)

    zero_duration_data = {
        'mode': 'WvW',
        'players': [{'name': 'P1', 'profession': 'Warrior', 'dps': 1000, 'cc': 100, 'cleanses': 5, 'strips': 2, 'downs': 0, 'deaths': 0, 'buffs': {}}],
        'duration': 0
    }
    zero_scores = engine.calculate_scores(zero_duration_data)
    test_result("Zero duration handled gracefully", len(zero_scores) == 1)

    extreme_dps_data = {
        'mode': 'WvW',
        'players': [
            {'name': 'HighDPS', 'profession': 'Warrior', 'dps': 100000, 'cc': 100, 'cleanses': 5, 'strips': 2, 'downs': 0, 'deaths': 0, 'buffs': {}},
            {'name': 'LowDPS', 'profession': 'Guardian', 'dps': 100, 'cc': 100, 'cleanses': 5, 'strips': 2, 'downs': 0, 'deaths': 0, 'buffs': {}}
        ],
        'duration': 120
    }
    extreme_scores = engine.calculate_scores(extreme_dps_data)
    test_result("Extreme DPS values handled", len(extreme_scores) == 2)
    test_result("DPS scores normalized to max 100", all(s['scores'].get('dps', 0) <= 100 for s in extreme_scores))

except Exception as e:
    import traceback
    traceback.print_exc()
    test_result("Edge Case Tests", False, str(e))

print()
print("8. Testing Exception Handling...")
try:
    edge_parser = EIParser()

    try:
        edge_parser.parse_file("nonexistent_file.json")
        test_result("FileNotFoundError for missing file", False, "Should have raised exception")
    except FileNotFoundError:
        test_result("FileNotFoundError for missing file", True)

    try:
        edge_parser.parse_file("setup.py")
        test_result("ValueError for unsupported format", False, "Should have raised exception")
    except ValueError:
        test_result("ValueError for unsupported format", True)

except Exception as e:
    test_result("Exception Handling", False, str(e))

print()
print("=" * 70)
print("Test Results Summary")
print("=" * 70)
print()
print(f"Total Tests: {passed + failed}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Success Rate: {passed * 100 / (passed + failed):.1f}%")
print()

if failed > 0:
    print("Failed Tests:")
    for result in test_results:
        if not result['passed']:
            print(f"  - {result['name']}: {result['message']}")
    print()

print("=" * 70)
print("System Status: " + ("READY" if failed == 0 else "NEEDS ATTENTION"))
print("=" * 70)
