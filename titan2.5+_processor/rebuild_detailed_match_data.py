import os
import json
import logging

def safe_int(val):
    try:
        if isinstance(val, int):
            return val
        if isinstance(val, float):
            return int(val)
        if val is None or val in ["-", "—", ""]:
            return 0
        val = str(val).strip()
        if "/" in val:
            return int(val.split("/")[0])
        if "%" in val:
            return int(float(val.strip("%")) / 100)
        return int(val)
    except:
        return 0

def safe_float(val):
    try:
        if isinstance(val, float):
            return val
        if isinstance(val, int):
            return float(val)
        if val is None or val in ["-", "—", ""]:
            return 0.0
        val = str(val).strip()
        if "%" in val:
            return float(val.strip("%"))
        return float(val)
    except:
        return 0.0

def safe_ratio(val):
    try:
        if isinstance(val, str) and "/" in val:
            num, denom = val.split("/")
            return round(int(num) / int(denom), 4) if int(denom) != 0 else 0.0
        return safe_float(val)
    except:
        return 0.0

def extract_flat_matches(year, source_path, dest_path):
    logging.info(f"\n🧩 Rebuilding detailed match data for {year}...")
    try:
        with open(source_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception as e:
        logging.error(f"❌ Failed to load {source_path}: {e}")
        return
    base = raw.get("NRL", [])
    matches = []
    for round_block in base:
        for round_key, round_matches in round_block.items():
            for match_wrapper in round_matches:
                for matchup, content in match_wrapper.items():
                    match_data = {}
                    try:
                        match_meta = content.get("match", {})
                        home_stats = content.get("home", {})
                        away_stats = content.get("away", {})
                        match_data["Round"] = f"Round {round_key}"
                        match_data["MatchName"] = matchup
                        match_data["MatchID"] = f"{year}-{round_key}-{matchup.replace(' ', '')}"
                        match_data["Date"] = f"{year}-01-01"  # Placeholder
                        match_data["main_ref"] = match_meta.get("main_ref")
                        match_data["weather_condition"] = match_meta.get("weather_condition")
                        match_data["ground_condition"] = match_meta.get("ground_condition")
                        avg_pb = home_stats.get("Average_Play_Ball_Speed", "0")
                        match_data["Average_PlayBall_Speed"] = safe_float(avg_pb if isinstance(avg_pb, str) else str(avg_pb))
                        match_data["kicking_metres"] = {
                            "home": safe_int(home_stats.get("kicking_metres")),
                            "away": safe_int(away_stats.get("kicking_metres"))
                        }
                        match_data["errors"] = {
                            "home": safe_int(home_stats.get("errors")),
                            "away": safe_int(away_stats.get("errors"))
                        }
                        match_data["penalties_conceded"] = {
                            "home": safe_int(home_stats.get("penalties_conceded")),
                            "away": safe_int(away_stats.get("penalties_conceded"))
                        }
                        match_data["sin_bins"] = {
                            "home": safe_int(home_stats.get("sin_bins")),
                            "away": safe_int(away_stats.get("sin_bins"))
                        }
                        matches.append(match_data)
                    except Exception as e:
                        logging.warning(f"⚠️ Failed to process match: {matchup} — {e}")
                        continue
    logging.info(f"✅ Extracted {len(matches)} detailed matches for {year}")
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    try:
        with open(dest_path, "w", encoding="utf-8") as out_f:
            json.dump(matches, out_f, indent=2)
    except Exception as e:
        logging.error(f"Failed to save {dest_path}: {e}")

def rebuild_all_detailed():
    SOURCE_BASE = "C:/Users/slangston1/TITAN/titan2.5+_processor/nrl"
    DEST_BASE = "C:/Users/slangston1/TITAN/titan2.5+_processor/nrl_fixed"
    YEARS = list(range(2019, 2026))
    logging.info("\n🔄 Starting rebuild of detailed match data...")
    for year in YEARS:
        source = os.path.join(SOURCE_BASE, str(year), f"NRL_detailed_match_data_{year}.json")
        dest = os.path.join(DEST_BASE, str(year), f"NRL_detailed_match_data_{year}.json")
        if os.path.exists(source):
            extract_flat_matches(year, source, dest)
        else:
            logging.warning(f"⚠️ Source file missing: {source}")
    logging.info("\n🏁 Detailed match data rebuild complete.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
    rebuild_all_detailed()
