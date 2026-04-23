
import os
import sqlite3

db_path = "gw2_logs.db"

def clean_db():
    print(f"Checking for database at {db_path}...")
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Successfully deleted {db_path}. A fresh one will be created on next start.")
        except Exception as e:
            print(f"Error deleting database: {e}")
            print("Please make sure api.py is NOT running and try again.")
    else:
        print("No database file found. Nothing to clean.")

if __name__ == "__main__":
    clean_db()
