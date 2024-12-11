from app.helpers import home_assistant as home_assistant_helper
from app.helpers import utils
from datetime import datetime, timezone
from app.db import db
from zoneinfo import ZoneInfo

def get_time():
    return datetime.now(ZoneInfo('America/Los_Angeles')).strftime('%I:%M:%S %p')

def get_dashboard(device_id):
    # Get device config
    device = db.devices.find_one({'deviceId': device_id})

    raw_dashboard = []

    # Resolve widgets
    widgets = device['deviceConfig']['dashboard']['widgets']

    for widget in widgets:
        if widget == 'time2row':
            raw_dashboard.append({
                'height': 16,
                'children': [
                    {
                        'content': f'{get_time()}',
                        'font': 'text-16',
                        'horizAlign': 2
                    },
                    {
                        'content': '\x59',
                        'font': 'dripicons-v2-16-split1',
                    }
                ]
            })
        elif widget == 'configureMeNote2row':
            raw_dashboard.append({
                'height': 24,
                'children': [
                    {
                        'content': 'Configure me in',
                        'horizAlign': 1,
                    },
                    {
                        'content': 'the Desk Buddy',
                        'horizAlign': 1,
                        'y': 9
                    },
                    {
                        'content': 'app!',
                        'horizAlign': 1,
                        'y': 18
                    }
                ]})
    
    dashboard_response = raw_dashboard

    return dashboard_response