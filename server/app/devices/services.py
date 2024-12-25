from flask import session, abort

from app.db import db
from app.errors import unauthorized
from app.utils import get_property_if_exists
from app.messages import services as message_services

DEFAULT_DEVICE_CONFIG = {
    "dashboard": {
        "widgets": ["time2row", "configureMeNote2row"],
        "dashboardFetchInterval": 5000,
    },
    "configFetchInterval": 10000,
}


def get_firmware():
    firmware = list(
        db.software_versions.find(
            # TODO remove, this is for debugging, app should be on demand and firmware is critical and regularly updated
            {"type": {"$in": ["firmware", "app"]}},
            {"_id": 0, "file_name": 1, "relative_path": 1, "version": 1},
        )
    )
    return firmware


def build_apps_menu():
    apps = list(
        db.software_versions.find(
            {"type": "app"},
        ).sort("relative_path", 1)
    )

    menu_item = {"label": "Apps", "children": []}

    for app in apps:
        directories = app["relative_path"].split("/")[1:-1]
        # Support at most double nesting
        if len(directories) == 2:
            parent = next((child for child in menu_item["children"] if child["label"] == directories[0]), None)
            if parent is None:
                parent = {"label": directories[0], "children": []}
                menu_item["children"].append(parent)  # Append parent only if it doesn't exist
            child = next((child for child in parent["children"] if child["label"] == directories[1]), None)
            if child is None:
                child = {"label": directories[1], "children": []}
                parent["children"].append(child)
            child["children"].append(
                {
                    "label": app["relative_path"].split("/")[-1].split(".")[0],
                    "action": "activity",
                    "path": app["relative_path"],
                }
            )
        elif len(directories) == 1:
            parent = next((child for child in menu_item["children"] if child["label"] == directories[0]), None)
            if parent is None:
                parent = {"label": directories[0], "children": []}
                menu_item["children"].append(parent)  # Append parent only if it doesn't exist
            parent["children"].append(
                {
                    "label": app["relative_path"].split("/")[-1].split(".")[0],
                    "action": "activity",
                    "path": app["relative_path"],
                }
            )
        else:
            menu_item["children"].append(
                {
                    "label": app["relative_path"].split("/")[-1].split(".")[0],
                    "action": "activity",
                    "path": app["relative_path"],
                }
            )

    return menu_item


def notifications_menu_item(device_config):
    return {
        "label": f"{len(device_config['notifications'])} Notifications",
        "action": "activity",
        "path": "notifications.py",
    }


def build_main_menu(device_config):
    menu = [
        notifications_menu_item(device_config),
        build_apps_menu(),
    ]

    return menu


def login(pairing_code):
    device = db.devices.find_one({"pairingCode": pairing_code})

    if device is None:
        return abort(404, "Device not found")

    device_config = {}

    if get_property_if_exists(device, "deviceConfig") and get_property_if_exists(device, "displayName"):
        device_config = device["deviceConfig"]
    else:
        abort(500, "Device config not found, is the account registered?")

    return {
        "pairingCode": pairing_code,
        "displayName": device["displayName"],
    }


def register(pairing_code, display_name, force_associate):
    # Associating a new device with an existing user
    force_associate = force_associate or False

    # Get all devices with that pairing code
    existing_device = db.devices.find_one({"pairingCode": pairing_code})

    if existing_device is None:
        return abort(404, "Device not found")

    if display_name is None and get_property_if_exists(existing_device, "displayName") is None:
        return abort(400, "Display name is required, have you registered this device before?")

    should_register_to_device = False

    if display_name is not None:
        # must figure out what to do with given displayName
        if get_property_if_exists(existing_device, "displayName") is None:
            # Device has never been registered, register it
            should_register_to_device = True
        elif existing_device["displayName"] != display_name:
            # Device has been registered with a different display name
            if force_associate:
                should_register_to_device = True
            else:
                return unauthorized(f'Device registered to {existing_device["displayName"]}')
        elif existing_device["displayName"] == display_name:
            # Device has been registered with the same display name
            should_register_to_device = True

        if should_register_to_device:
            # Update device associaton
            db.devices.update_one(
                {"pairingCode": pairing_code},
                {
                    "$set": {
                        "displayName": display_name,
                    },
                },
            )

    # reload what we have in the database
    existing_device = db.devices.find_one({"pairingCode": pairing_code})

    device_config = {}

    if get_property_if_exists(existing_device, "deviceConfig"):
        device_config = existing_device["deviceConfig"]
    else:
        device_config = DEFAULT_DEVICE_CONFIG
        db.devices.update_one(
            {"pairingCode": pairing_code},
            {
                "$set": {
                    "deviceConfig": device_config,
                },
            },
        )

    # Create session
    session["pairingCode"] = existing_device["pairingCode"]
    session["displayName"] = existing_device["displayName"]

    return {
        "pairingCode": existing_device["pairingCode"],
        "displayName": existing_device["displayName"],
    }


def build_notifications(device_config):
    notifications = []

    # check messages
    messages = message_services.get_unread_messages(device_config["displayName"])

    for message in messages:
        notifications.append(
            {
                "type": "message",
                "content": message,
            }
        )

    return notifications


def get_config(device_id):
    device = db.devices.find_one({"deviceId": device_id})
    device_config = device["deviceConfig"]
    # put displayName on deviceConfig for display purposes on device, but otherwise keep it separate
    device_config["displayName"] = device["displayName"]
    device_config["firmware"] = get_firmware()
    device_config["notifications"] = build_notifications(device_config)
    device_config["menu"] = build_main_menu(device_config)
    return device_config


def get_firmware_contents(relative_path):
    firmware = db.software_versions.find_one({"relative_path": relative_path}, {"_id": 0, "contents": 1})

    return firmware
