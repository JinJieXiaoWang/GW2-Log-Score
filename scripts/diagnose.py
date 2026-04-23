import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parser.ei_parser import EIParser
from src.scoring.scoring_engine import ScoringEngine
from src.database.db_manager import DBManager


def test_full_flow():
    print("--- Starting Diagnostic Test ---")
    data_path = "tests/data.json"
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found")
        return

    try:
        print(f"1. Loading and parsing {data_path}...")
        parser = EIParser()
        parsed_data = parser.parse_file(data_path)
        print(f"   Mode detected: {parsed_data['mode']}")
        print(f"   Players found: {len(parsed_data['players'])}")

        print("2. Calculating scores...")
        scorer = ScoringEngine()
        scores = scorer.calculate_pve_scores(parsed_data)
        print(f"   Scores calculated for {len(scores)} players")
        if scores:
            print(f"   Sample score (Player 0): {scores[0]['player_name']} - {scores[0]['total_score']}")

        print("3. Testing database storage...")
        db_path = "test_gw2.db"
        if os.path.exists(db_path):
            os.remove(db_path)
        db = DBManager(db_path)

        db.add_combat_log(
            parsed_data['log_id'],
            parsed_data['mode'],
            parsed_data['encounter_name'],
            parsed_data['date'],
            int(parsed_data['duration']),
            data_path,
            parsed_data['recorded_by']
        )

        for s in scores:
            db.add_player(s['player_name'], s['profession'], s['role'])
            db.add_combat_score(
                parsed_data['log_id'],
                s['player_name'],
                s['scores'],
                s['total_score'],
                s['details']
            )
        print("   Database operations successful")

        print("\n--- Diagnostic Test Passed! ---")
        os.remove(db_path)
    except Exception as e:
        import traceback
        print("\n--- Diagnostic Test FAILED! ---")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    test_full_flow()
