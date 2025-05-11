import pandas as pd
import numpy as np
import json
from collections import defaultdict
import os
import ENVIRONMENT_VARIABLES as EV

def run_ref_analysis(year=2021, detailed_data_path=None, nrl_data_path=None, output_csv=None):
    teams = EV.TEAMS
    variables = ["Year", "Win", "Defense", "Attack", "Margin", "Home", "Versus", "Round", "Halftime_Attack", "Halftime_Defense", "Tries", "FirstHalf_Tries", "SecondHalf_Tries", "FirstHalf_Tries_Other", "SecondHalf_Tries_Other"]
    if not detailed_data_path:
        detailed_data_path = f'./data/nrl_detailed_match_data_{year}.json'
    if not nrl_data_path:
        nrl_data_path = f'./data/nrl_data_{year}.json'
    if not output_csv:
        output_csv = f'outputs/ref_analysis_{year}.csv'

    # Load NRL data
    with open(nrl_data_path, 'r') as file:
        data = json.load(file)['NRL']
        years_arr = {year: data[0][str(year)]}

    # Load detailed match data
    round_game_data = defaultdict(dict)
    with open(detailed_data_path, 'r') as file:
        data = json.load(file)['NRL']
        for round in range(0, 26):
            round_data = data[round]
            for key, value in round_data.items():
                game_datas = round_data[key]
                for game in game_datas:
                    game_name = list(game.keys())[0]
                    round_game_data[round][game_name] = game[game_name]

    # Build DataFrame
    df = pd.DataFrame(columns=[f"{team} {variable}" for team in teams for variable in variables])
    all_store = []
    for round in range(0, 27):
        try:
            round_data = years_arr[year][round][str(round+1)]
            round_store = np.zeros([len(teams)*len(variables)], dtype=int)
            round_teams = []
            for game in round_data:
                h_team = game['Home']
                h_score = int(game['Home_Score'])
                a_team = game['Away']
                a_score = int(game['Away_Score'])
                rgd = round_game_data[round][f"{h_team} v {a_team}"]
                match_data_away = rgd['away']['half_time']
                match_data_home = rgd['home']['half_time']
                try_amount_home = rgd['home']['try_minutes']
                try_second_half_home = sum(int(element.replace("'", ""))  > 40 for element in try_amount_home)
                try_amount_home = len(try_amount_home)
                try_first_half_home = try_amount_home-try_second_half_home
                try_amount_away = rgd['away']['try_minutes']
                try_second_half_away = sum(int(e.replace("'", ""))  > 40 for e in try_amount_away)
                try_amount_away = len(try_amount_away)
                try_first_half_away = try_amount_away-try_second_half_away
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
                for idx, data in zip(range(a_team_idx_fm, a_team_idx_fm + len(variables)), [year, a_team_win, a_team_defense, a_team_attack, a_team_margin, a_home, a_versus, round + 1, match_data_away, match_data_home, try_amount_away, try_first_half_away, try_second_half_away, try_first_half_home, try_second_half_home]):
                    round_store[idx] = data
                for idx, data in zip(range(h_team_idx_fm, h_team_idx_fm + len(variables)), [year, h_team_win, h_team_defense, h_team_attack, h_team_margin, h_home, h_versus, round + 1, match_data_home, match_data_away, try_amount_home, try_first_half_home, try_second_half_home, try_first_half_away, try_second_half_away]):
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
                round_store[b_team_idx_fm+9] = -1
                round_store[b_team_idx_fm+10] = -1
                round_store[b_team_idx_fm+11] = -1
                round_store[b_team_idx_fm+12] = -1
                round_store[b_team_idx_fm+13] = -1
            all_store.append(round_store)
            df.loc[len(df)] = round_store
        except Exception as ex:
            print(ex)
    df.to_csv(output_csv, index=False)
    print(f"[SUCCESS] Ref analysis exported to {output_csv}")

if __name__ == "__main__":
    run_ref_analysis()