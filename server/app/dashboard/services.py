from config import Config
from app.helpers import home_assistant as home_assistant_helper
from app.helpers import utils
from datetime import datetime, timezone

def get_dog_dashboard_two_screens_four_buttons():
    # get all necessary values
    timer_since_last_out = home_assistant_helper.get_home_assistant_value("input_datetime.last_time_out")
    last_peed = home_assistant_helper.get_home_assistant_value("input_datetime.dog_last_peed")
    last_pooped = home_assistant_helper.get_home_assistant_value("input_datetime.dog_last_pooped")
    last_fed = home_assistant_helper.get_home_assistant_value("input_datetime.last_fed")

    utc_time = datetime.now(timezone.utc)

    last_out_time = datetime.fromisoformat(timer_since_last_out['last_reported'])
    try:
        last_out_time = datetime.fromisoformat(timer_since_last_out['attributes']['finishes_at'])
    except KeyError:
        pass

    # format response for display
    screen_one = {
        'text': f'''<- Last out
{utils.pretty_print_time_between(last_out_time, utc_time)}

Last fed ->
{utils.pretty_print_time_between(datetime.fromtimestamp(last_fed['attributes']['timestamp'], tz=timezone.utc), utc_time)}'''
    }

    screen_two = {
        'text': f'''<- Last peed
{utils.pretty_print_time_between(datetime.fromtimestamp(last_peed['attributes']['timestamp'], tz=timezone.utc), utc_time)}

Last pooped ->
{utils.pretty_print_time_between(datetime.fromtimestamp(last_pooped['attributes']['timestamp'], tz=timezone.utc), utc_time)}'''
    }

    return {
        'screen_one': screen_one,
        'screen_two': screen_two,
    }

def post_dog_dashboard_two_screens_four_buttons(button):
    print(button)
    if button == "button1":
        home_assistant_helper.press_home_assistant_button("input_button.i_took_jade_out_now")
    elif button == "button2":
        home_assistant_helper.press_home_assistant_button("input_button.i_fed_dog")
    elif button == "button3":
        home_assistant_helper.press_home_assistant_button("input_button.dog_peed")
    elif button == "button4":
        home_assistant_helper.press_home_assistant_button("input_button.dog_pooped")
    return "Button pressed"

def get_dog_dashboard_two_screens_readonly():
    # get all necessary values
    timer_since_last_out = home_assistant_helper.get_home_assistant_value("input_datetime.last_time_out")
    last_peed = home_assistant_helper.get_home_assistant_value("input_datetime.dog_last_peed")
    last_pooped = home_assistant_helper.get_home_assistant_value("input_datetime.dog_last_pooped")
    last_fed = home_assistant_helper.get_home_assistant_value("input_datetime.last_fed")

    utc_time = datetime.now(timezone.utc)

    last_out_time = datetime.fromisoformat(timer_since_last_out['last_reported'])
    try:
        last_out_time = datetime.fromisoformat(timer_since_last_out['attributes']['finishes_at'])
    except KeyError:
        pass

    # format response for display
    screen_one = {
        'text': f'''Last out
{utils.pretty_print_time_between(last_out_time, utc_time)}

Last fed
{utils.pretty_print_time_between(datetime.fromtimestamp(last_fed['attributes']['timestamp'], tz=timezone.utc), utc_time)}'''
    }

    screen_two = {
        'text': f'''Last peed
{utils.pretty_print_time_between(datetime.fromtimestamp(last_peed['attributes']['timestamp'], tz=timezone.utc), utc_time)}

Last pooped
{utils.pretty_print_time_between(datetime.fromtimestamp(last_pooped['attributes']['timestamp'], tz=timezone.utc), utc_time)}'''
    }

    return {
        'screen_one': screen_one,
        'screen_two': screen_two,
    }
        