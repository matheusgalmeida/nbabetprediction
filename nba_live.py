import curses
from nba_api.live.nba.endpoints import scoreboard
import json

def format_game_clock(game_clock):
    if not game_clock or game_clock == "":
        return "00M:00S"

    formatted_time = game_clock[2:].replace("M", "M:").replace("S", "S")
    formatted_time = formatted_time.replace(".00", "")
    return formatted_time

def display_team_scores(stdscr, home_team, away_team, row, col):
    home_periods = home_team.get('periods', [])
    away_periods = away_team.get('periods', [])

    for i in range(4):  # Assuming there are 4 quarters
        home_score = home_periods[i]['score'] if i < len(home_periods) else 0
        away_score = away_periods[i]['score'] if i < len(away_periods) else 0

        stdscr.addstr(row + i, col, f"Q{i + 1}: {home_score} - {away_score}")
    

def todayGames(stdscr):
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Jogos de Hoje:")

        # Today's Score Board
        games = scoreboard.ScoreBoard()
        # JSON
        games_json = games.get_json()
        # Convert JSON string to a Python object
        games_data = json.loads(games_json)

        num_games = len(games_data['scoreboard']['games'])
        terminal_height, terminal_width = stdscr.getmaxyx()

        max_width_per_game = terminal_width // 4  # Adjust the number of games per row as needed

        for i in range(num_games):
            game = games_data['scoreboard']['games'][i]
            home_team = game['homeTeam']
            away_team = game['awayTeam']
            game_clock_formatted = format_game_clock(game['gameClock'])

            row_offset = 2 + (i // 4) * 15  # Adjust the row_offset calculation
            col_offset = (i % 4) * max_width_per_game

            if row_offset + 11 < terminal_height and col_offset + max_width_per_game <= terminal_width:
                stdscr.addstr(row_offset, col_offset, f"Game ID: {game['gameId']}")
                stdscr.addstr(row_offset + 1, col_offset, f"Game Status: {game['gameStatusText']}")
               # stdscr.addstr(row_offset + 2, col_offset, f"Time: {game_clock_formatted}")
                stdscr.addstr(row_offset + 2, col_offset,
                              f"{home_team['teamTricode']} {home_team['teamName']} {home_team['score']} X {away_team['score']} {away_team['teamTricode']} {away_team['teamName']}")

                # Display team scores for each quarter below team names
                display_team_scores(stdscr, home_team, away_team, row_offset + 4, col_offset)

                stdscr.addstr(row_offset + 11, col_offset, "-" * max_width_per_game)  # Separator line

        stdscr.refresh()
        curses.napms(500)

curses.wrapper(todayGames)
