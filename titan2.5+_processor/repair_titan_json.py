import os
import json

# === CONFIGURATION ===
SOURCE_BASE = "C:/Users/slangston1/TITAN/titan2.5+_processor/nrl"
DEST_BASE = "C:/Users/slangston1/TITAN/titan2.5+_processor/nrl_fixed"
YEARS = list(range(2019, 2026))

os.makedirs(DEST_BASE, exist_ok=True)

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def repair_player_file(path):
    repaired = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            first_line = f.readline()
            f.seek(0)
            if first_line.strip().startswith("{"):
                # Standard JSON
                raw = json.load(f)
                records = raw.get("PlayerStats", [])
                for match in records:
                    if isinstance(match, dict) and isinstance(match.get("Players", []), list):
                        repaired.append(match)
            else:
                # NDJSON
                for line in f:
                    try:
                        obj = json.loads(line.strip())
                        if isinstance(obj, dict) and isinstance(obj.get("Players", []), list):
                            repaired.append(obj)
                    except:
                        continue
        return {"PlayerStats": repaired}
    except Exception as e:
        print(f"❌ Error repairing player file {path}: {e}")
        return {"PlayerStats": []}

def repair_detailed_file(path):
    repaired = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            if isinstance(raw, list):
                return [r for r in raw if isinstance(r, dict)]
            elif isinstance(raw, dict):
                for val in raw.values():
                    if isinstance(val, dict):
                        repaired.append(val)
            elif isinstance(raw, str):
                repaired = [json.loads(raw)]
        return repaired
    except Exception as e:
        print(f"❌ Error repairing detailed file {path}: {e}")
        return []

def repair_all():
    print(f"\n🔧 Starting JSON Repair Process...")
    print(f"📂 Source: {SOURCE_BASE}")
    print(f"💾 Destination: {DEST_BASE}")

    for year in YEARS:
        print(f"\n🗂 Processing year: {year}")
        src_folder = os.path.join(SOURCE_BASE, str(year))
        dest_folder = os.path.join(DEST_BASE, str(year))
        os.makedirs(dest_folder, exist_ok=True)

        match_file = os.path.join(src_folder, f"NRL_data_{year}.json")
        player_file = os.path.join(src_folder, f"NRL_player_statistics_{year}.json")
        detailed_file = os.path.join(src_folder, f"NRL_detailed_match_data_{year}.json")

        # === MATCH FILE: Copy through ===
        if os.path.exists(match_file):
            try:
                with open(match_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                save_json(os.path.join(dest_folder, f"NRL_data_{year}.json"), data)
                print(f"✅ Copied match file for {year}")
            except:
                print(f"❌ Invalid JSON in match file {year}")
        else:
            print(f"⚠️  Missing match file for {year}")

        # === PLAYER FILE: Repair ===
        if os.path.exists(player_file):
            repaired = repair_player_file(player_file)
            save_json(os.path.join(dest_folder, f"NRL_player_statistics_{year}.json"), repaired)
            print(f"✅ Repaired player stats for {year}")
        else:
            print(f"⚠️  Missing player file for {year}")

        # === DETAILED FILE: Repair ===
        if os.path.exists(detailed_file):
            repaired = repair_detailed_file(detailed_file)
            save_json(os.path.join(dest_folder, f"NRL_detailed_match_data_{year}.json"), repaired)
            print(f"✅ Repaired detailed match data for {year}")
        else:
            print(f"⚠️  Missing detailed file for {year}")

    print("\n✅ Repair complete. All fixed files saved to /nrl_fixed/.")

if __name__ == "__main__":
    repair_all()
