from datetime import datetime, timezone
from app.db import db
from zoneinfo import ZoneInfo


def get_time():
    return datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%I:%M:%S %p")


def get_current_day_with_suffix_in_timezone(timezone="America/Los_Angeles"):
    # Get the current date and time in the specified time zone
    now = datetime.now(ZoneInfo(timezone))
    # Get the day of the month
    day = now.day

    # Determine the suffix for the day
    if 11 <= day <= 13:  # Special cases for 11th, 12th, and 13th
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

    # Format the date with the suffix
    return now.strftime(f"%a %b {day}{suffix}")


def get_dashboard(device_id):
    # Get device config
    device = db.devices.find_one({"deviceId": device_id})

    raw_dashboard = []

    # Resolve widgets
    widgets = device["deviceConfig"]["dashboard"]["widgets"]

    for widget in widgets:
        if widget == "time4row":
            raw_dashboard.append(
                {
                    "height": 32,
                    "children": [
                        {"content": f"{get_current_day_with_suffix_in_timezone()}", "font": "text-16", "horizAlign": 2},
                        {"content": "__CURRENT_DEVICE_TIME__", "font": "text-16", "horizAlign": 2, "y": 16},
                        {
                            "content": "\x59",
                            "font": "icons-16-1",
                            "y": 16,
                        },
                    ],
                }
            )
        elif widget == "configureMeNote2row":
            raw_dashboard.append(
                {
                    "height": 24,
                    "children": [
                        {
                            "content": "Configure me in",
                            "horizAlign": 1,
                        },
                        {"content": "the Desk Buddy", "horizAlign": 1, "y": 9},
                        {"content": "app!", "horizAlign": 1, "y": 18},
                    ],
                }
            )
        elif widget == "buddy":
            raw_dashboard.append(
                {
                    "height": 32,
                    "children": [
                        {"content": "((o))", "vertAlign": 2, "horizAlign": 1, "height": 8},
                        {"content": "|", "vertAlign": 2, "horizAlign": 1, "height": 16},
                        {"content": "[o_o]", "vertAlign": 2, "horizAlign": 1, "height": 24},
                    ],
                }
            )

    dashboard_response = raw_dashboard

    return dashboard_response
