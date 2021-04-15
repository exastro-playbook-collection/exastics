import datetime
import dateutil.parser
import json
import pathlib
import os
import sys


def get_datetime_from_filename(filename):
    return_value = None

    name, ext = os.path.splitext(filename)
    if ext == '.json':
        try:
            dt = dateutil.parser.isoparse(name)
            return_value = dt.isoformat(timespec='seconds')
        except ValueError:
            pass
    
    return return_value


def get_datetime_and_json_data(base_dir):
    for dirpath, _, filenames in os.walk(base_dir):
        for filename in filenames:
            dt = get_datetime_from_filename(filename)
            if not dt:
                continue

            try:
                with open(pathlib.PurePath(dirpath, filename)) as file:
                    data = json.load(file)
            except Exception as e:
                print(str(e), type(e))
                continue

            yield (dt, data)
