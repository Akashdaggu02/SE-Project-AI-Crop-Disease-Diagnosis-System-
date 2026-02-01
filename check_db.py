
import sqlite3
import os
import sys

# Connect to DB
db_path = 'backend/database/crop_diagnosis.db'
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
    sys.exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def check_disease(crop, disease_name):
    print(f"\n--- Checking Disease: {disease_name} (Crop: {crop}) ---")
    
    # 1. Check Diseases Table
    rows = cursor.execute('SELECT * FROM diseases WHERE crop = ? AND disease_name = ?', (crop, disease_name)).fetchall()
    if rows:
        print(f"✅ Found in 'diseases' table: {[dict(r) for r in rows]}")
    else:
        print(f"❌ NOT found in 'diseases' table.")
        # Try finding partial matches
        rows_partial = cursor.execute('SELECT disease_name FROM diseases WHERE crop = ?', (crop,)).fetchall()
        print(f"   Available diseases for {crop}: {[r['disease_name'] for r in rows_partial]}")

    # 2. Check Pesticides
    disease_clean = disease_name.replace('___', ' ').replace('_', ' ')
    print(f"   Cleaning for pesticide search: '{disease_name}' -> '{disease_clean}'")
    
    query = "SELECT name, target_diseases FROM pesticides WHERE target_diseases LIKE ?"
    rows_pest = cursor.execute(query, (f'%{disease_clean}%',)).fetchall()
    
    if rows_pest:
        print(f"✅ Found matching pesticides: {[r['name'] for r in rows_pest]}")
    else:
        print(f"❌ NO pesticides found matching '%{disease_clean}%'")
        # Show all pesticides target strings
        # all_pests = cursor.execute("SELECT target_diseases FROM pesticides").fetchall()
        # print("   All targets:", [r['target_diseases'] for r in all_pests])

# Test with the failing case
check_disease('tomato', 'Early blight')
check_disease('tomato', 'Tomato___Early_blight')

# Test Rice
check_disease('rice', 'Brown spot')
check_disease('rice', 'BrownSpot')

conn.close()
