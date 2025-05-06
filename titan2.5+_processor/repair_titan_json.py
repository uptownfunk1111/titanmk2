import os
import json
import logging

# === CONFIGURATION ===
SOURCE_BASE = "C:/Users/slangston1/TITAN/titan2.5+_processor/nrl"
DEST_BASE = "C:/Users/slangston1/TITAN/titan2.5+_processor/nrl_fixed"
YEARS = list(range(2019, 2026))

os.makedirs(DEST_BASE, exist_ok=True)

def save_json(filepath, data):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to save {filepath}: {e}")

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
                    except Exception as e:
                        logging.warning(f"NDJSON parse error: {e}")
        return {"PlayerStats": repaired}
    except Exception as e:
        logging.error(f"Error repairing player file {path}: {e}")
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
        logging.error(f"Error repairing detailed file {path}: {e}")
        return []

def repair_all():
    logging.info(f"\n🔧 Starting JSON Repair Process...")
    logging.info(f"📂 Source: {SOURCE_BASE}")
    logging.info(f"💾 Destination: {DEST_BASE}")

    for year in YEARS:
        logging.info(f"\n🗂 Processing year: {year}")
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
                logging.info(f"✅ Copied match file for {year}")
            except Exception as e:
                logging.error(f"❌ Invalid JSON in match file {year}: {e}")
        else:
            logging.warning(f"⚠️  Missing match file for {year}")

        # === PLAYER FILE: Repair ===
        if os.path.exists(player_file):
            repaired = repair_player_file(player_file)
            save_json(os.path.join(dest_folder, f"NRL_player_statistics_{year}.json"), repaired)
            logging.info(f"✅ Repaired player stats for {year}")
        else:
            logging.warning(f"⚠️  Missing player file for {year}")

        # === DETAILED FILE: Repair ===
        if os.path.exists(detailed_file):
            repaired = repair_detailed_file(detailed_file)
            save_json(os.path.join(dest_folder, f"NRL_detailed_match_data_{year}.json"), repaired)
            logging.info(f"✅ Repaired detailed match data for {year}")
        else:
            logging.warning(f"⚠️  Missing detailed file for {year}")

    logging.info("\n✅ Repair complete. All fixed files saved to /nrl_fixed/.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
    repair_all()
