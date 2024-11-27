def get_property_if_exists(obj, property_name, default=None):
    return obj[property_name] if property_name in obj else default

def pretty_print_time_until(start_time, end_time):
    delta = end_time - start_time
    finished = delta.total_seconds() < 0
    if finished:
        delta = start_time - end_time
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    pretty_string = f'{hours} : {minutes:02} : {seconds:02}'
    if finished:
        pretty_string += ' ago'
    else:
        pretty_string = 'in ' + pretty_string
    return pretty_string

def pretty_print_time_between(start_time, end_time):
    delta = end_time - start_time
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    pretty_string = f'{hours} : {minutes:02} : {seconds:02}'
    return pretty_string
