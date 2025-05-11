"""
Try Scorer Model Utilities
- Feature engineering and prediction for anytime try scorer
- Refactored from antyime_try_scorer_model.ipynb for pipeline use
"""
import json
import pandas as pd
import numpy as np
from collections import defaultdict
import os

# --- Data Loading Functions ---
def load_match_data(year=2024, total_rounds=8, teams=None, variables=None, data_dir="./data"):
    if teams is None:
        teams = ["Broncos", "Roosters", "Wests Tigers", "Rabbitohs", "Storm", "Eels", "Raiders", "Knights", "Dragons", "Sea Eagles", "Panthers", "Sharks", "Bulldogs", "Dolphins", "Titans", "Cowboys", "Warriors"]
    if variables is None:
        variables = ["Year", "Win", "Defense", "Attack", "Margin", "Home", "Versus", "Round", "Halftime_Attack", "Halftime_Defense"]
    df = pd.DataFrame(columns=[f"{team} {variable}" for team in teams for variable in variables])
    # Load match data
    with open(os.path.join(data_dir, f"nrl_data_{year}.json"), 'r') as file:
        data = json.load(file)["NRL"]
        years_arr = data[0][str(year)]
    # Load detailed match data
    round_game_data = defaultdict(dict)
    with open(os.path.join(data_dir, f"nrl_detailed_match_data_{year}.json"), 'r') as file:
        data = json.load(file)["NRL"]
        for round in range(0, total_rounds):
            round_data = data[round]
            for key, value in round_data.items():
                game_datas = round_data[key]
                for game in game_datas:
                    game_name = list(game.keys())[0]
                    round_game_data[round][game_name] = game[game_name]
    # Feature engineering (simplified for pipeline)
    all_store = []
    for round in range(0, total_rounds):
        try:
            round_data = years_arr[round][str(round+1)]
            round_store = np.zeros([len(teams)*len(variables)], dtype=int)
            round_teams = []
            for game in round_data:
                h_team = game['Home']
                h_score = int(game['Home_Score'])
                a_team = game['Away']
                a_score = int(game['Away_Score'])
                h_team_name = h_team.replace(" ", "-")
                a_team_name = a_team.replace(" ", "-")
                rgd = round_game_data[round][f"{h_team} v {a_team}"]
                match_data_away = rgd['away']['half_time']
                match_data_home = rgd['home']['half_time']
                h_team_win, a_team_win = h_score >= a_score, a_score >= h_score
                h_home, a_home = 1, 0
                h_versus, a_versus= teams.index(a_team), teams.index(h_team)
                h_team_defense = a_score
                a_team_defense = h_score
                h_team_attack = h_score
                a_team_attack = a_score
                h_team_margin =  h_score - a_score
                a_team_margin =  a_score - h_score
                round_teams.append(h_team)
                round_teams.append(a_team)
                a_team_idx = teams.index(a_team)
                h_team_idx = teams.index(h_team)
                a_team_idx_fm = a_team_idx * len(variables)
                h_team_idx_fm = h_team_idx * len(variables)
                for idx, data in zip(range(a_team_idx_fm, a_team_idx_fm + 10), [year, a_team_win, a_team_defense, a_team_attack, a_team_margin, a_home, a_versus, round + 1, match_data_away, match_data_home]):
                    round_store[idx] = data
                for idx, data in zip(range(h_team_idx_fm, h_team_idx_fm + 10), [year, h_team_win, h_team_defense, h_team_attack, h_team_margin, h_home, h_versus, round + 1, match_data_home, match_data_away]):
                    round_store[idx] = data
            bye_teams = list(set(teams) - set(round_teams))
            for bye_team in bye_teams:
                b_team_idx = teams.index(bye_team)
                b_team_idx_fm = b_team_idx * len(variables)
                round_store[b_team_idx_fm] = year
                round_store[b_team_idx_fm+1] = -1
                round_store[b_team_idx_fm+2] = -1
                round_store[b_team_idx_fm+3] = -1
                round_store[b_team_idx_fm+4] = 0
                round_store[b_team_idx_fm+5] = -1
                round_store[b_team_idx_fm+6] = -1
                round_store[b_team_idx_fm+7] = round+1
                round_store[b_team_idx_fm+8] = -1
            all_store.append(round_store)
            df.loc[len(df)] = round_store
        except Exception as ex:
            print(ex)
    return df

def load_player_data(year=2024, total_rounds=8, teams=None, player_labels=None, data_dir="./data"):
    if teams is None:
        teams = ["Broncos", "Roosters", "Wests Tigers", "Rabbitohs", "Storm", "Eels", "Raiders", "Knights", "Dragons", "Sea Eagles", "Panthers", "Sharks", "Bulldogs", "Dolphins", "Titans", "Cowboys", "Warriors"]
    if player_labels is None:
        player_labels = ["Name", "Tries", "Tackle Efficiency"]
    years_arr = {}
    with open(os.path.join(data_dir, f"player_statistics_{year}.json"), 'r') as file:
        data = json.load(file)["PlayerStats"]
        years_arr[year] = data[0][str(year)]
    player_stats = defaultdict(list)
    for i in range(0, total_rounds):
        try:
            round = years_arr[year][i][str(i)]
            for round_game in round:
                for game in round_game:
                    game_split = game.split("v")
                    home_team = " ".join(game_split[0].split("-")[2:]).replace("-", " ").strip()
                    away_team = " ".join(game_split[-1:]).replace("-", " ").strip()
                    players = round_game[game]
                    player_round_stats = {} 
                    for player in players:
                        vals = [player[val] for val in player_labels]
                        player_round_stats[vals[0]] = vals[1:]
                    player_round_stats = list(player_round_stats.items())
                    player_round_stats_home, player_round_stats_away = player_round_stats[:18], player_round_stats[18:]
                    for player in player_round_stats_home:
                        player_stats[player[0]].append([player[1], i+1, home_team, away_team])
                    for player in player_round_stats_away:
                        player_stats[player[0]].append([player[1], i+1, away_team, home_team])
        except Exception as ex:
            print(f"Player data error: {ex}")
    return player_stats

# --- Feature Engineering & Prediction ---
def find_player_data(player_df):
    tries = (player_df[player_df['Tries']!= "-"])['Tries'].count()
    tackle_efficiency = player_df['Tackle Efficiency'].replace('-', '1.0')
    tackle_efficiency = tackle_efficiency.str.rstrip('%').astype(float) / 100
    games = player_df['Tries'].count()
    try_per_games = tries/games if games else 0
    return tackle_efficiency.mean(), try_per_games

def try_scorer_features(players, player_labels):
    # Example: return a DataFrame of player try scoring rates
    records = []
    for player, values in players.items():
        player_stat = [[*round[0], *round[1:]] for round in values]
        df = pd.DataFrame(player_stat, columns=player_labels + ["Round", "Team", "Opposition"])
        tef, tpg = find_player_data(df)
        records.append({"Player": player, "TackleEfficiency": tef, "TriesPerGame": tpg})
    return pd.DataFrame(records)

def save_try_scorer_features(df, output_path):
    df.to_csv(output_path, index=False)
    print(f"[SUCCESS] Try scorer features saved to {output_path}")
