import time
import utime


def get_property_if_exists(obj, property_name, default=None):
    return obj[property_name] if property_name in obj else default


def get_los_angeles_time():
    current_utc_time = time.localtime()

    # Define standard offset and DST offset
    STANDARD_OFFSET = -8  # Standard Pacific Time (UTC-8)
    DST_OFFSET = -7  # Daylight Saving Time Pacific Time (UTC-7)

    # Determine if DST is active (this can be more complex, depending on your needs)
    # Assume DST is active between the second Sunday in March and the first Sunday in November
    year = current_utc_time[0]
    month = current_utc_time[1]
    day = current_utc_time[2]
    weekday = current_utc_time[6]  # Monday=0, Sunday=6

    # Calculate DST start and end dates
    dst_start = utime.mktime((year, 3, 8, 2, 0, 0, 0, 0))  # Second Sunday in March
    while utime.localtime(dst_start)[6] != 6:  # Ensure it's Sunday
        dst_start += 86400

    dst_end = utime.mktime((year, 11, 1, 2, 0, 0, 0, 0))  # First Sunday in November
    while utime.localtime(dst_end)[6] != 6:  # Ensure it's Sunday
        dst_end += 86400

    # Determine current offset
    current_time = utime.mktime(current_utc_time)
    offset = DST_OFFSET if dst_start <= current_time < dst_end else STANDARD_OFFSET

    # Apply the offset
    los_angeles_time = utime.localtime(current_time + offset * 3600)
    return los_angeles_time
