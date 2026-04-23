
import os
import shutil
import uuid
import json
from parser.ei_parser import EIParser
from database.db_manager import DBManager
from scoring.scoring_engine import ScoringEngine

def test_upload_logic():
    print("--- Testing API Upload Logic ---")
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "gw2_logs.db")
    
    # Ensure fresh start
    if os.path.exists(db_path):
        os.remove(db_path)
        
    db = DBManager(db_path)
    parser = EIParser()
    scorer = ScoringEngine()
    
    source_file = "data.json"
    if not os.path.exists(source_file):
        print(f"Error: {source_file} not found")
        return

    # Simulate upload save
    UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        
    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{source_file}")
    shutil.copy(source_file, file_path)
    print(f"File saved to {file_path}")

    try:
        # 1. Parse
        print("1. Parsing...")
        parsed_data = parser.parse_file(file_path)
        
        # 2. Database Log
        print("2. Adding to combat_logs...")
        duration = 0
        try:
            d_val = parsed_data.get('duration', 0)
            if isinstance(d_val, str):
                duration = int(parsed_data.get('duration_ms', 0) / 1000)
            else:
                duration = int(float(d_val))
        except:
            duration = 0

        db.add_combat_log(
            parsed_data['log_id'],
            parsed_data['mode'],
            parsed_data['encounter_name'],
            parsed_data['date'],
            duration,
            file_path,
            parsed_data['recorded_by']
        )
        
        # 3. Scoring & Players
        print("3. Calculating scores and adding to DB...")
        scores = scorer.calculate_scores(parsed_data)
        for s in scores:
            db.add_player(s['player_name'], s['profession'], s['role'])
            db.add_combat_score(
                parsed_data['log_id'],
                s['player_name'],
                s['scores'],
                s['total_score'],
                s['details']
            )
            
        print(f"SUCCESS: Processed {len(scores)} players from {parsed_data['encounter_name']}")
        
        # 4. Verify Score Query
        print("4. Verifying database query...")
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT cl.date, cl.encounter_name, cs.* 
                FROM combat_scores cs
                JOIN combat_logs cl ON cs.log_id = cl.log_id
                ORDER BY cl.date DESC
            ''')
            rows = cursor.fetchall()
            print(f"Query returned {len(rows)} rows")
            if len(rows) > 0:
                print(f"Sample row: {dict(rows[0])}")

        print("\n--- API Logic Test Passed! ---")
    except Exception as e:
        import traceback
        print("\n--- API Logic Test FAILED! ---")
        traceback.print_exc()

if __name__ == "__main__":
    test_upload_logic()
