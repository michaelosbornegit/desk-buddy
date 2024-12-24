from fileinput import filename
from app.db import db
from datetime import datetime, timezone
from app.bcrypt import GlobalBcrypt
from app.errors import unauthorized
from app.helpers.utils import get_property_if_exists

DEFAULT_DEVICE_CONFIG = {
    'dashboard': {
        'widgets': [
            'time2row',
            'configureMeNote2row'
        ],
        "dashboardFetchInterval": (1 / 2) * 1000,
    },
    'menu':  [
                {
                    'label': 'Games',
                    'children': [
                        {
                            'label': 'Reflexes',
                            'action': 'fetchExec',
                            'path': 'modules/games/reflexes',
                        },
                        {
                            'label': 'Simon Says',
                            'action': 'fetchExec',
                            'path': 'modules/games/simon-says',
                        },
                        {
                            'label': 'Beat keeper',
                            'action': 'fetchExec',
                            'path': 'modules/games/simon-says',
                        },
                        {
                            'label': 'Back',
                            'action': 'back',
                        },
                    ]
                },
                {
                    'label': 'Ask Buddy',
                    'children': [
                        {
                            'label': 'Motivation',
                            'action': 'fetchExec',
                            'path': 'modules/ask-buddy/motivation',
                        },
                        {
                            'label': 'Meaning',
                            'action': 'fetchExec',
                            'path': 'modules/ask-buddy/meaning',
                        },
                        {
                            'label': 'Joke',
                            'action': 'fetchExec',
                            'path': 'modules/ask-buddy/joke',
                        },
                        {
                            'label': 'Back',
                            'action': 'back',
                        },
                    ]
                },
                {
                    'label': 'Go Home',
                    'action': 'home',
                },
            ],
            'configFetchInterval': 1000,
    }

def get_firmware():
    firmware = list(db.software_versions.find(
        # TODO remove, this is for debugging, app should be on demand and firmware is critical and regularly updated
        {'type': {'$in': ['firmware', 'app']}},
        {'_id': 0, 'file_name': 1, 'relative_path': 1, 'version': 1}
    ))
    return firmware

def build_apps_menu():
    apps = list(db.software_versions.find(
        {'type': 'app'},
    ).sort('relative_path', 1))

    menu_item = {
        'label': 'Apps',
        'children': []
    }

    for app in apps:
        directories = app['relative_path'].split('/')[1:-1]
        # Support at most double nesting
        if len(directories) == 2:
            parent = next((child for child in menu_item['children'] if child['label'] == directories[0]), None)
            if parent is None:
                parent = {
                    'label': directories[0],
                    'children': []
                }
                menu_item['children'].append(parent)  # Append parent only if it doesn't exist
            child = next((child for child in parent['children'] if child['label'] == directories[1]), None)
            if child is None:
                child = {
                    'label': directories[1],
                    'children': []
                }
                parent['children'].append(child)
            child['children'].append({
                'label': app['relative_path'].split('/')[-1],
                'action': 'fetchExec',
                'path': app['relative_path'],
            })
        elif len(directories) == 1:
            parent = next((child for child in menu_item['children'] if child['label'] == directories[0]), None)
            if parent is None:
                parent = {
                    'label': directories[0],
                    'children': []
                }
                menu_item['children'].append(parent)  # Append parent only if it doesn't exist
            parent['children'].append({
                'label': app['relative_path'].split('/')[-1],
                'action': 'fetchExec',
                'path': app['relative_path'],
            })
        else:
            menu_item['children'].append({
                'label': app['relative_path'],
                'action': 'fetchExec',
                'path': app['relative_path'],
            })

    return menu_item



def build_main_menu():
    menu = [
        {
            # TODO make notification firmware
            'label': '0 Notifications',
        },
        build_apps_menu(),
    ]

    return menu

def register_device(request_data):
    device_id = request_data['deviceId']
    username = request_data['username']
    password = request_data['password']

    # Check if username exists on any device
    existing_user = db.users.find_one({'username': username})

    if existing_user:
        # Check if password matches
        if not GlobalBcrypt.instance.check_hash(password, existing_user['password']):
            return unauthorized('Invalid password')
    else:
        # Create new user
        db.users.insert_one({
            'username': username,
            'password': GlobalBcrypt.instance.generate_hash(password),
        })

    # see if device exists
    existing_device = db.devices.find_one({'deviceId': device_id})

    device_config = DEFAULT_DEVICE_CONFIG

    # If user is new to device, overwrite devie config with defaults, otherwise keep existing device config
    if existing_device is not None:
        if existing_device['username'] != username:
            device_config = DEFAULT_DEVICE_CONFIG
        else:
            device_config = existing_device['deviceConfig']
    
    # Register user to device
    db.devices.update_one(
        {'deviceId': device_id},
        {'$set': {
            'username': username,
            'deviceConfig': device_config,
        }},
        upsert=True
    )

    device_config['firmware'] = get_firmware()
    device_config['menu'] = build_main_menu()

    return device_config
    # TODO more complex login logic
    # See if a user already exists with given username associated with any device
    # if user exists, passwords must match
    # See if device is already registered to a different account

def get_config(device_id):
    device = db.devices.find_one({'deviceId': device_id})
    device_config = device['deviceConfig']
    device_config['firmware'] = get_firmware()
    device_config['menu'] = build_main_menu()
    return device_config

def get_firmware_contents(relative_path):   
    firmware = db.software_versions.find_one(
        {'relative_path': relative_path},
        {'_id': 0, 'contents': 1}
    )

    return firmware