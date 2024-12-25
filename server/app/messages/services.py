import datetime
import json
from bson import ObjectId

from app.db import db
from app import messages


def send_message(message_from, message_to, message):
    augmented_recipients = [{"to": recipient, "read": False} for recipient in message_to]
    message_to_insert = {
        "from": message_from,
        "to": augmented_recipients,
        "message": message,
        "createdAt": datetime.datetime.now(tz=datetime.UTC),
    }
    inserted_message = db.messages.insert_one(message_to_insert)

    return {"result": "Message sent", "messageId": str(inserted_message.inserted_id)}


def get_unread_messages(display_name):
    # Get latest 5 unread messages
    messages = list(db.messages.find({"to": {"$elemMatch": {"to": display_name, "read": False}}}).sort("createdAt", 1))
    messages = json.loads(json.dumps(messages, default=str))
    return messages


def get_read_messages(display_name, limit, offset):
    messages = (
        db.messages.find({"to": {"$elemMatch": {"to": display_name, "read": True}}})
        .sort("createdAt", -1)
        .limit(limit)
        .skip(offset)
    )
    return messages


def get_recipients():
    recipients = db.devices.distinct("displayName")
    return recipients


def read_message(message_id, device_id):
    # get the display name of the device
    device = db.devices.find_one({"deviceId": device_id})
    display_name = device["displayName"]

    print(f"Device {display_name} read message {message_id}")

    db.messages.update_one(
        {"_id": ObjectId(message_id), "to": {"$elemMatch": {"to": display_name}}},
        {"$set": {"to.$.read": True}},
    )

    return {"result": "Message read"}
