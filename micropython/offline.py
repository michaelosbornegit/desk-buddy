import os

import secrets

# Set offline_mode = True in secrets.py to run without wifi or the server
OFFLINE_MODE = getattr(secrets, "offline_mode", False)

APPS_DIR = "apps"
DIR_TYPE = 0x4000

# Shown on the dashboard instead of the server rendered one
OFFLINE_DASHBOARD = [
    {
        "height": 32,
        "children": [
            {"content": "Desk Buddy", "font": "text-16", "horizAlign": 1},
            {"content": "Press for menu", "horizAlign": 1, "y": 20},
        ],
    },
    {
        "height": 32,
        "children": [
            {"content": "((o))", "vertAlign": 2, "horizAlign": 1, "height": 8},
            {"content": "|", "vertAlign": 2, "horizAlign": 1, "height": 16},
            {"content": "[o_o]", "vertAlign": 2, "horizAlign": 1, "height": 24},
        ],
    },
]


def _build_apps_menu(path):
    # Mirrors the server's apps menu: folders become submenus, .py files become activities
    menu = []
    for entry in sorted(os.ilistdir(path)):
        name, entry_type = entry[0], entry[1]
        entry_path = f"{path}/{name}"
        if entry_type == DIR_TYPE:
            children = _build_apps_menu(entry_path)
            if children:
                menu.append({"label": name, "children": children})
        elif name.endswith(".py"):
            menu.append(
                {"label": name[:-3], "action": "activity", "path": entry_path}
            )
    return menu


def build_offline_config():
    # Kept so the menu matches online mode, it explains notifications need the server
    menu = [
        {"label": "Notifications", "action": "activity", "path": "notifications.py"}
    ]
    try:
        menu += _build_apps_menu(APPS_DIR)
    except OSError:
        pass

    return {"menu": menu, "notifications": []}
