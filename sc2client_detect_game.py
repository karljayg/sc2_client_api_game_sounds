import json
import random
import requests
import time
import pygame
from enum import Enum

class GameState(Enum):
    STARTED = 'Undecided'
    ENDED = ['Defeat', 'Victory', 'Tie']

# load configuration file
with open('config.json') as f:
    config = json.load(f)

# player to check results for
player_names = config['player_name']

def play_sound(game_event):
    pygame.mixer.init()
    sound_file = random.choice(config['sounds'][game_event])
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()

def get_game_status(previous_game_statuses=None):
    response = requests.get('http://localhost:6119/game')
    data = response.json()
    if not config['play_on_replay'] and data['isReplay']:
        return None, previous_game_statuses
    game_statuses = {}
    for player in data['players']:
        if player['name'] in player_names:
            game_statuses[player['name']] = player['result']
    if game_statuses != previous_game_statuses:
        print(f"Received data: {data}")  # Print the JSON data
    return game_statuses, previous_game_statuses

def monitor_game():
    previous_game_statuses = {}  # Initialize with an empty dictionary
    while True:
        game_statuses, previous_game_statuses = get_game_status(previous_game_statuses)
        if game_statuses:
            for player_name, game_status in game_statuses.items():
                previous_state = previous_game_statuses.get(player_name)
                if game_status != previous_state:
                    if game_status == GameState.STARTED.value and (previous_state in GameState.ENDED.value if previous_state else True):
                        play_sound('start')
                    elif game_status in GameState.ENDED.value and previous_state:
                        play_sound(game_status.lower())
                previous_game_statuses[player_name] = game_status
        time.sleep(1)  # Wait a second before re-checking

if __name__ == "__main__":
    monitor_game()

