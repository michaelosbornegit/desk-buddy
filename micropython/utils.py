def get_property_if_exists(obj, property_name, default=None):
    return obj[property_name] if property_name in obj else default