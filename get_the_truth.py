import json
import pandas as pd
import os

# ---------------------------------------------------------
# SETUP: Targeted specifically at your master file
source_file = "lark_venues_clean.json" 
# ---------------------------------------------------------

if not os.path.exists(source_file):
    print(f"❌ I cannot find '{source_file}'!")
    print("Please make sure this script is in the same folder as the json file.")
    exit()

try:
    print(f"📖 Reading from {source_file}...")
    
    with open(source_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle different JSON structures (List vs Dictionary)
    if isinstance(data, dict) and "venues" in data:
        venues = data["venues"]
    elif isinstance(data, list):
        venues = data
    else:
        # Fallback: maybe the venues are hiding under a different key?
        print(f"⚠️ Unexpected structure. Found keys: {data.keys() if isinstance(data, dict) else 'List'}")
        venues = []

    print(f"🔍 Found {len(venues)} venues.")

    # Flatten the data for the spreadsheet
    rows = []
    for v in venues:
        # Join tags into a simple string like "Folk, Intimate, Dark"
        # This makes them easy to edit in Excel
        tag_list = v.get("tags", [])
        if isinstance(tag_list, list):
            tag_string = ", ".join(tag_list)
        else:
            tag_string = str(tag_list)
        
        rows.append({
            "name": v.get("name", ""),
            "blurb": v.get("blurb", ""),
            "location": v.get("location", ""),
            "url": v.get("url", ""),
            "tags": tag_string,  # <--- The Moods!
            "status": "Active"   # Default status
        })

    # Save to CSV
    output_filename = "lark_master_audit.csv"
    df = pd.DataFrame(rows)
    df.to_csv(output_filename, index=False)
    
    print(f"✨ Success! Extracted {len(rows)} venues to '{output_filename}'.")
    print("👉 You can now open this CSV in Excel and start your audit.")

except Exception as e:
    print(f"⚠️ Error reading JSON: {e}")