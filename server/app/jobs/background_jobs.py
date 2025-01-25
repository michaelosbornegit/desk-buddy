import os

from app.db import db


def update_firmware():
    folder_path = os.path.join(os.path.dirname(__file__), "../../../micropython")
    for root, _dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)

            if file_name not in (
                "main_.py",
                "wifi_config.py",
                "hwconfig_supermini.py",
                "hwconfig_xiao.py",
                "ruff.toml",
                "secrets.py",
            ) and (file_name.endswith((".py", ".pf"))):
                relative_path = os.path.relpath(file_path, folder_path)

                file_contents = None

                with open(file_path, "rb") as file:
                    file_contents = file.read()

                existing_entry = db.software_versions.find_one({"relative_path": relative_path})

                file_type = "firmware"
                if relative_path.startswith("apps/"):
                    file_type = "app"

                if existing_entry:
                    if existing_entry["contents"] != file_contents:
                        print(f"Updating {relative_path}")
                        db.software_versions.update_one(
                            {"_id": existing_entry["_id"]},
                            {"$set": {"contents": file_contents}, "$inc": {"version": 1}},
                        )
                else:
                    db.software_versions.insert_one(
                        {"relative_path": relative_path, "contents": file_contents, "type": file_type, "version": 1}
                    )
