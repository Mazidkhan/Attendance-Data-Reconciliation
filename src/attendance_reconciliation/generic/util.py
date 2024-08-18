import importlib
import random
import socket
import string
import time
from datetime import datetime, timedelta

import jwt
import structlog

logger = structlog.getLogger(__name__)


def check_internet():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        logger.debug("Checking for internet", internet="1")
        socket.create_connection(("reconindia.in", 80))
        logger.debug("Connection to internet successful", internet="5")
        return True
    except OSError:
        logger.info("Unable to connect to internet")
        return False
    except KeyboardInterrupt:
        raise
    except Exception:
        logger.info("Unable to connect to internet")
        return False


def calculate_time_to_sleep(custom_logger, sleep_interval, start_time, end_time):
    time_to_sleep = (sleep_interval / 1000) - end_time + start_time
    if time_to_sleep > 0:
        if time_to_sleep > (sleep_interval / 1000):
            custom_logger.info("time_to_sleep greater than normal : " + str(time_to_sleep))
            time_to_sleep = (sleep_interval / 1000)
        return time_to_sleep
    else:
        custom_logger.info("time_to_sleep less than 0 : " + str(time_to_sleep))
        return 0


def read_json_from_file(path):
    data = []
    with open(path) as json_data:
        import json
        data = json.loads(json_data.read())
        json_data.close()
    return data


def read_content_from_file(path):
    data = []
    with open(path) as json_data:
        data = json_data.read()
        json_data.close()
    return data


def write_to_file(file_name, content):
    f = open(file_name, "w")
    f.write(content)
    f.close()


def create_custom_class(name, protocol_settings):
    __mod = name.lower()
    __cls = name.capitalize()
    __required_class = getattr(importlib.import_module(__mod), __cls)
    required_class = __required_class(protocol_settings)
    return required_class


def random_string_generator(length=10):
    letters = string.ascii_uppercase + string.digits
    random_string = ''.join(random.choice(letters) for i in range(length))
    return random_string


def generate_jwt_token(user, secret_key):
    token = jwt.encode({
        'userId': user["id"],
        'name': user["name"],
        'role': user["role"],
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, secret_key)
    # token = jwt.encode({
    #     'userId': user["id"],
    #     'name': user["name"],
    #     'role': user["role"],
    #     'exp': datetime.utcnow() + timedelta(minutes=1)
    # }, secret_key)

    return token


def generate_event_object(event_id, event_type, source, data):
    event_obj = {
        "eventId": event_id,
        "timestamp": int(time.time()),
        "eventType": event_type,
        "source": source,
        "data": data
    }
    return event_obj


def ranged_lin_eq(points_list, input_obj):
    (input_value, dq, data_error) = input_obj
    input_value = float(input_value)
    x_axis_points = []  # [5, 10, 20, 40]
    if len(points_list) < 2:
        return input_obj
    for p in points_list:
        (x_coord, y_coord) = p
        x_axis_points.append(x_coord)
    if input_value < min(x_axis_points):
        first_closest_coordinate = points_list[0]
        second_closest_coordinate = points_list[1]
    elif input_value > max(x_axis_points):
        first_closest_coordinate = points_list[-2]
        second_closest_coordinate = points_list[-1]
    else:
        x_axis_points.append(input_value)  # [5, 10, 20, 40, 35]
        x_axis_points.sort()  # [5, 10, 20, 35, 40]
        raw_value_index = x_axis_points.index(input_value)
        first_closest_coordinate = points_list[raw_value_index - 1]
        second_closest_coordinate = points_list[raw_value_index]
    (first_point_x_value, first_point_y_value) = first_closest_coordinate
    (second_point_x_value, second_point_y_value) = second_closest_coordinate
    slope = (second_point_y_value - first_point_y_value) / (second_point_x_value - first_point_x_value)
    final_value = slope * (input_value - first_point_x_value) + first_point_y_value
    return final_value, dq, data_error
