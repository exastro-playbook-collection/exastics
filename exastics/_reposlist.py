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

def publish_api(base_dir):
    repositories = []

    for dt, github_repos in get_datetime_and_json_data(base_dir):
        for github_repo in github_repos:
            if 'name' in github_repo:
                if github_repo['name'] != "exastics":
                    repositories.append(github_repo['name'])

    filepath = pathlib.PurePath(base_dir, 'repositories.json')
    print(f'filepath ... {filepath}')

    os.makedirs(filepath.parent, exist_ok=True)
    with open(filepath, mode='w') as f:
        json.dump(repositories, f)

    print("succeeded")

    return (repositories)
