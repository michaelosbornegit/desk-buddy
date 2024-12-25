import utime
import asyncio
import requests
import copy

from activity import Activity


class Menu(Activity):
    def __init__(self, name, hardware, functions, secrets):
        super().__init__(name, hardware, functions, secrets)
        # Set up instance specific variables
        # what is displayed on the screen
        self.current_raw_display = []
        # store menu states so we can go up and down menus and remember where we were
        self.menu_states = []
        self.needs_render = True

    async def render(self):
        if not self.needs_render:
            return

        # if we have no menu states, push on the current menu from device config
        if len(self.menu_states) == 0:
            # tack on back button to the top level menu
            top_level_menu = copy.deepcopy(
                self.functions.get_current_device_config()["menu"]
            )
            top_level_menu.append({"label": "Go Back"})

            self.menu_states.append({"selected_menu_item": 0, "menu": top_level_menu})

        self.current_raw_display = []

        # First, convert to raw menu items to display
        for index, item in enumerate(self.menu_states[-1]["menu"]):
            if index == self.menu_states[-1]["selected_menu_item"]:
                # put inverted box to show its selected
                self.current_raw_display.append(
                    {
                        "height": 16,
                        "font": "text-16",
                        "children": [
                            {"height": 16, "color": 1},
                            {
                                "content": item["label"],
                                "font": "text-16",
                                "height": 16,
                                "horizAlign": 1,
                                "color": 0,
                            },
                        ],
                    }
                )
            else:
                self.current_raw_display.append(
                    {
                        "height": 16,
                        "font": "text-16",
                        "children": [
                            {
                                "content": item["label"],
                                "height": 16,
                                "horizAlign": 1,
                            }
                        ],
                    }
                )

        self.functions.set_current_raw_display(self.current_raw_display)
        self.needs_render = False

    async def button_click(self):
        # Cycle through menu items
        current_menu_state = self.menu_states[-1]
        if (
            current_menu_state["selected_menu_item"]
            == len(current_menu_state["menu"]) - 1
        ):
            current_menu_state["selected_menu_item"] = 0
        else:
            current_menu_state["selected_menu_item"] += 1
        self.needs_render = True

    async def button_long_click(self):
        current_menu_state = self.menu_states[-1]
        if (
            current_menu_state["selected_menu_item"]
            == len(current_menu_state["menu"]) - 1
        ):
            # go back
            if len(self.menu_states) == 1:
                # we are at the top level, go back to dashboard
                self.hardware.display.clear()
                await self.functions.switch_activity("DASHBOARD")
            if len(self.menu_states) > 1:
                # we are in a submenu, go back to the previous menu
                self.hardware.display.clear()
                self.menu_states.pop()
                self.needs_render = True
        else:
            # an actual menu item was selected, we need to do something
            if (
                "children"
                in current_menu_state["menu"][current_menu_state["selected_menu_item"]]
            ):
                # we selected a submenu, push it on the stack
                # tack on back button
                menu = copy.deepcopy(
                    current_menu_state["menu"][
                        current_menu_state["selected_menu_item"]
                    ]["children"]
                )
                menu.append({"label": "Go Back"})
                self.menu_states.append({"selected_menu_item": 0, "menu": menu})
                self.needs_render = True
            else:
                # we selected an action, do it
                action = current_menu_state["menu"][
                    current_menu_state["selected_menu_item"]
                ]["action"]
                if action == "fetchExec":
                    path = current_menu_state["menu"][
                        current_menu_state["selected_menu_item"]
                    ]["path"]
                    await self.functions.fetch_exec(path)
                else:
                    print(f"Unknown action: {action}")

    async def on_mount(self):
        self.hardware.display.clear()
        self.current_raw_display = []
        self.menu_states = []
        self.needs_render = True

    async def on_unmount(self):
        pass
