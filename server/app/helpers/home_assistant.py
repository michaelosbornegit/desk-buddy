import requests

from config import Config
from app.helpers import utils


def get_home_assistant_value(entity_id):
    response = requests.get(f'{Config.HA_HOST}/states/{entity_id}', 
                            headers = { "Authorization": "Bearer " + Config.HA_TOKEN })
    responseJson = response.json()

    if (utils.get_property_if_exists(responseJson, "message") == "Entity not found"):
        print(f"Entity {entity_id} not found, check for a typo")
        return None

    return response.json()

def press_home_assistant_button(entity_id):
    response = requests.post(f'{Config.HA_HOST}/services/input_button/press', 
                             headers = { "Authorization": "Bearer " + Config.HA_TOKEN }, 
                             json={ "entity_id": entity_id })
    return response.json()