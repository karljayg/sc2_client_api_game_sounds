import json
import random
import requests
import time
import pygame
from enum import Enum

class GameState(Enum):
    STARTED = 'Undecided'
    ENDED = ['Defeat', 'Victory', 'Tie']

# Add a variable to store the initial state
initial_state = True

# load configuration file
with open('config.json') as f:
    config = json.load(f)

# player to check results for
player_name = config['player_name']

def play_sound(game_event):
    pygame.mixer.init()
    sound_file = random.choice(config['sounds'][game_event])
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()

def get_game_status():
    response = requests.get('http://localhost:6119/game')
    data = response.json()
    print(f"Received data: {data}")  # Print the JSON data
    if not config['play_on_replay'] and data['isReplay']:
        return None
    game_statuses = {}
    for player in data['players']:
        if player['name'] in player_name:
            game_statuses[player['name']] = player['result']
    return game_statuses

def monitor_game():
    current_states = {}  # Initialize with an empty dictionary
    is_first_run = True  # Indicates whether this is the first run of the loop
    while True:
        game_statuses = get_game_status()
        if game_statuses:
            for player_name, game_status in game_statuses.items():
                current_state = current_states.get(player_name)
                if game_status != current_state:
                    if game_status == GameState.STARTED.value and (current_state in GameState.ENDED.value if current_state else True):
                        play_sound('start')
                    elif game_status in GameState.ENDED.value and not is_first_run:
                        play_sound(game_status.lower())
                    current_states[player_name] = game_status
            is_first_run = False  # Update the flag after the first run
        time.sleep(1)  # Wait a second before re-checking
          
if __name__ == "__main__":
    monitor_game()