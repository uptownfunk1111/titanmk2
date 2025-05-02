import json
import os

# === CONFIGURATION ===
INPUT_FILE = "NRL_player_statistics_2024.json"  # Change to your actual file
OUTPUT_PREFIX = "NRL_chunk"
MAX_CHARS = 100000  # Safe size for ChatGPT

# === LOAD JSON and extract PlayerStats list ===
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# Grab the actual player stat list inside the dictionary
data = raw_data.get("PlayerStats", [])

# === SPLIT INTO CHUNKS ===
chunks = []
current_chunk = []
current_size = 0

for entry in data:
    entry_str = json.dumps(entry)
    entry_size = len(entry_str)

    if current_size + entry_size > MAX_CHARS:
        chunks.append(current_chunk)
        current_chunk = []
        current_size = 0

    current_chunk.append(entry)
    current_size += entry_size

if current_chunk:
    chunks.append(current_chunk)

# === SAVE CHUNKS ===
os.makedirs("chunks", exist_ok=True)

for i, chunk in enumerate(chunks, start=1):
    output_path = os.path.join("chunks", f"{OUTPUT_PREFIX}_{i}.json")
    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(chunk, out, indent=2)

print(f"✅ Done: {len(chunks)} files saved in ./chunks/")
