import utime
import time
import asyncio
import requests
import copy

from activity import Activity
from utils import get_property_if_exists


class notifications(Activity):
    def __init__(self, name, hardware, functions, secrets):
        super().__init__(name, hardware, functions, secrets)
        # Set up instance specific variables
        self.current_notification = None
        self.currently_viewing = None
        self.rendered = False

    async def read_notification(self, id):
        self.hardware.display.clear()
        self.hardware.display.text("Marking", 0, 0, 1, 0, 128, 64, 1)
        self.hardware.display.text("notification as", 0, 8, 1, 0, 128, 64, 1)
        self.hardware.display.text("read...", 0, 16, 1, 0, 128, 64, 1)
        self.hardware.display.show()
        try:
            notification_response = requests.post(
                f"{self.secrets.api_host}/messages/read-message",
                json={"messageId": id, "deviceId": self.secrets.device_id},
                headers={"Authorization": self.secrets.device_secret},
            )
            if notification_response.status_code == 200:
                self.functions.get_current_device_config()["notifications"].pop(0)
                self.current_notification = None
                self.rendered = False
            else:
                self.hardware.display.clear()
                self.hardware.display.text("Error marking", 0, 0, 1, 0, 128, 64, 1)
                self.hardware.display.text("notification as", 0, 8, 1, 0, 128, 64, 1)
                self.hardware.display.text("read", 0, 16, 1, 0, 128, 64, 1)
                self.hardware.display.show()
                await asyncio.sleep(5)
                await self.functions.switch_activity("dashboard")

        except Exception as e:
            print(f"Error fetching notification: {e}")
        pass

    async def render(self):
        if not self.rendered:
            if self.current_notification:
                # We have a notification to display, display it
                if self.current_notification["type"] == "message":
                    if self.currently_viewing == "from":
                        self.hardware.display.clear()
                        self.hardware.display.select_font(None)
                        # Group message display route
                        if len(self.current_notification["content"]["to"]) > 1:
                            self.hardware.display.text(
                                "Group Message", 0, 0, 1, 0, 128, 64, 1
                            )

                        else:
                            self.hardware.display.text(
                                "Message", 0, 0, 1, 0, 128, 64, 1
                            )
                        self.hardware.display.text(
                            "from:",
                            0,
                            8,
                            1,
                            0,
                            128,
                            64,
                            1,
                        )
                        self.hardware.display.text(
                            self.current_notification["content"]["from"],
                            0,
                            24,
                            1,
                            0,
                            128,
                            64,
                            1,
                        )
                    elif self.currently_viewing == "to":
                        self.hardware.display.clear()
                        self.hardware.display.select_font(None)
                        self.hardware.display.text("To:", 0, 0, 1, 0, 128, 64, 1)
                        for i, to in enumerate(
                            self.current_notification["content"]["to"]
                        ):
                            self.hardware.display.text(
                                to["to"], 0, 8 + i * 8, 1, 0, 128, 64, 1
                            )
                    elif self.currently_viewing == "content":
                        self.hardware.display.clear()
                        self.hardware.display.select_font(None)
                        if not self.current_notification["content"]["message"]:
                            self.hardware.display.text(
                                "No content", 0, 0, 1, 0, 128, 64, 1
                            )

                        else:
                            centerLines = 0
                            if get_property_if_exists(
                                self.current_notification["content"], "centerLines"
                            ):
                                centerLines = 1
                            split_content = self.current_notification["content"][
                                "message"
                            ].split("\n")
                            for i, line in enumerate(split_content):
                                self.hardware.display.text(
                                    line, 0, i * 8, centerLines, 0, 128, 64, 1
                                )
                self.rendered = True
            else:
                # Figure out if we have a current notification
                if len(self.functions.get_current_device_config()["notifications"]) > 0:
                    self.current_notification = (
                        self.functions.get_current_device_config()["notifications"][0]
                    )
                    if self.current_notification["type"] == "message":
                        self.currently_viewing = "from"
                else:
                    self.hardware.display.clear()
                    self.hardware.display.select_font(None)
                    self.hardware.display.text("No", 0, 0, 1, 0, 128, 64, 1)
                    self.hardware.display.text("notifications!", 0, 8, 1, 0, 128, 64, 1)
                    self.hardware.display.show()
                    await asyncio.sleep(3)
                    await self.functions.switch_activity("dashboard")

    async def button_click(self):
        if self.current_notification:
            if self.current_notification["type"] == "message":
                if self.currently_viewing == "from":
                    if len(self.current_notification["content"]["to"]) > 1:
                        self.currently_viewing = "to"
                    else:
                        self.currently_viewing = "content"
                elif self.currently_viewing == "to":
                    self.currently_viewing = "content"
                elif self.currently_viewing == "content":
                    await self.read_notification(
                        self.current_notification["content"]["_id"]
                    )
            self.rendered = False
        else:
            await self.functions.switch_activity("dashboard")

    async def button_long_click(self):
        await self.functions.switch_activity("dashboard")

    async def on_mount(self):
        pass

    async def on_unmount(self):
        self.functions.unload_activity("notifications")
