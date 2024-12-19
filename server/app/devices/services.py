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
            'configFetchInterval': 10 * 1000,
    }

def get_firmware():
    firmware = list(db.software_versions.find(
        {'type': 'firmware'},
        {'_id': 0, 'file_name': 1, 'relative_path': 1, 'version': 1}
    ))
    print('Firmware:', firmware)
    return firmware

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

    return device_config
    # TODO more complex login logic
    # See if a user already exists with given username associated with any device
    # if user exists, passwords must match
    # See if device is already registered to a different account

def get_config(device_id):
    device = db.devices.find_one({'deviceId': device_id})
    device_config = device['deviceConfig']
    device_config['firmware'] = get_firmware()
    return device_config

def get_firmware_contents(file_name):   
    firmware = db.software_versions.find_one(
        {'file_name': file_name},
        {'_id': 0, 'contents': 1}
    )

    return firmware