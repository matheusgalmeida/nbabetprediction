from nba_api.stats.endpoints import teamgamelog
from nba_api.live.nba.endpoints import scoreboard
import pandas as pd
from datetime import datetime
import json

def get_game_information(game_number):
    games = scoreboard.ScoreBoard()
    games_json = games.get_json()
    games_data = json.loads(games_json)
    game = games_data['scoreboard']['games'][game_number]
    home_team = game['homeTeam']
    away_team = game['awayTeam']
    home_fullname = home_team['teamCity'] +' '+ home_team['teamName']
    away_fullname = away_team['teamCity'] +' '+ away_team['teamName']
    name_game = f'{home_fullname} - {away_fullname}'
    game_id = game['gameId']
    return home_team, away_team, name_game, game_id 

def get_team_game_logs(team_id, seasons, current_date):
    team_game_log_data_all = pd.DataFrame()

    for season in seasons:
        game_log = teamgamelog.TeamGameLog(
            team_id=team_id,
            season=season
        )
        team_game_log_data = game_log.get_data_frames()[0]
        team_game_log_data = team_game_log_data[team_game_log_data['GAME_DATE'] != current_date]
        
        team_game_log_data_all = pd.concat([team_game_log_data_all, team_game_log_data])

    return team_game_log_data_all

def main():
    #game_number = int(input("Digite o número do jogo: "))
    #home_team, away_team, name_game = get_game_information(game_number)
    games = scoreboard.ScoreBoard()
    games_json = games.get_json()
    games_data = json.loads(games_json)
    all_games_info = []

    for game_number in range(len(games_data['scoreboard']['games'])):
        home_team, away_team, name_game, game_id = get_game_information(game_number)
        
        get_home_team_id = home_team['teamId']
        get_away_team_id = away_team['teamId']
        home_fullname = home_team['teamCity'] +' '+ home_team['teamName']
        away_fullname = away_team['teamCity'] +' '+ away_team['teamName']
        
        seasons =  ['2023-22', '2022-21', '2021-20','2020-19']
        
        current_date = datetime.now().strftime('%b %d, %Y').upper()

        home_team_game_log_data_all = get_team_game_logs(get_home_team_id, seasons, current_date)
        away_team_game_log_data_all = get_team_game_logs(get_away_team_id, seasons, current_date)

        matching_game_ids = set(home_team_game_log_data_all['Game_ID']).intersection(away_team_game_log_data_all['Game_ID'])
        
        filtered_home_team_game_log = home_team_game_log_data_all[home_team_game_log_data_all['Game_ID'].isin(matching_game_ids)]
        filtered_away_team_game_log = away_team_game_log_data_all[away_team_game_log_data_all['Game_ID'].isin(matching_game_ids)]
        
        columns_to_average = ['FG3M', 'FTM', 'DREB', 'OREB', 'REB', 'AST', 'PTS']
        home_avarages = {}
        away_avarages = {}
        both_team_avarages = {}

        for column in columns_to_average:
            average_home_team = round(filtered_home_team_game_log[column].mean(), 1)
            average_away_team = round(filtered_away_team_game_log[column].mean(), 1)

            home_avarages[f"{column}"] = average_home_team
            away_avarages[f"{column}"] = average_away_team
            
            total_average = round(pd.concat([filtered_home_team_game_log[column], filtered_away_team_game_log[column]]).mean()*2, 1)
            both_team_avarages[f"{column}"] = total_average

        renamed_both_teams_columns = {
            'FG3M': 'Total Arremessos de três pontos Marcados',
            'FTM': 'Total de lances livres marcados na partida',
            'OREB':'Total de rebotes ofensivos da partida',
            'DREB':'Total de rebotes defensivos da partida',
            'REB': 'Total de Rebotes',
            'AST': 'Total de Assistências',
            'PTS': 'Total de Pontos'
        }
        renamed_team_home_columns = {
            'FG3M':f'Total Arremessos de três pontos marcados da equipe - {home_fullname}',
            'FTM': f'Total de lances livres marcados pela equipe - {home_fullname}',
            'OREB':f'Total de rebotes ofensivos da equipe - {home_fullname}',
            'DREB':f'Total de rebotes defensivos da equipe - {home_fullname}',
            'REB': f'Total de Rebotes da equipe - {home_fullname}',
            'AST': f'Total de Assistências da equipe - {home_fullname}',
            'PTS': 'Total de Pontos'
        }
        renamed_team_away_columns = {
            'FG3M':f'Total Arremessos de três pontos marcados da equipe - {away_fullname}',
            'FTM': f'Total de lances livres marcados pela equipe - {away_fullname}',
            'OREB':f'Total de rebotes ofensivos da equipe - {away_fullname}',
            'DREB':f'Total de rebotes defensivos da equipe - {away_fullname}',
            'REB': f'Total de Rebotes da equipe - {away_fullname}',
            'AST': f'Total de Assistências da equipe - {away_fullname}',
            'PTS': 'Total de Pontos'
        }

        both_team_avarages_renamed = {}
        home_team_avarages_renamed = {}
        away_team_avarages_renamed = {}

        for key, value in both_team_avarages.items():
            renamed_key = renamed_both_teams_columns[key]
            both_team_avarages_renamed[renamed_key] = value

        for key, value in home_avarages.items():
            renamed_key = renamed_team_home_columns[key]
            home_team_avarages_renamed[renamed_key] = value

        for key, value in away_avarages.items():
            renamed_key = renamed_team_away_columns[key]
            away_team_avarages_renamed[renamed_key] = value

        #game_info = {
        #    "game": {
        #        "name_game": name_game,
        #        "both_team_avarages": both_team_avarages_renamed,
        #        "home_team_avarages": home_team_avarages_renamed,
        #        "away_team_avarages": away_team_avarages_renamed
        #    }
        #}
        game_info = {
            "game": {
                "name": name_game,
                "game_id":game_id
            },
            "both_team_avarages": both_team_avarages_renamed,
            "home_team_avarages": home_team_avarages_renamed,
            "away_team_avarages": away_team_avarages_renamed
        }
        
        all_games_info.append(game_info)

    #json_response = json.dumps(all_games_info, indent=4)
    json_response = json.dumps(all_games_info, indent=4, ensure_ascii=False)
    with open('nbaprediction.json', 'w') as file:
        file.write(json_response)
if __name__ == "__main__":
    main()
