#!/usr/bin/env python3

import datetime
import dateutil.parser
import exastics._reposlist
import exastics._chartdata
import json
import pathlib
import os
import sys


class GitHubTag:
    def __init__(self, release):
        self.tag_name = release['tag_name']
        self.id = release['id']

        self.assets = []
        for asset in release['assets']:
            self.assets.append(GitHubAsset(asset))


class GitHubAsset:
    def __init__(self, asset):
        self.id = asset['id']
        self.name = asset['name']
        self.download_count = asset['download_count']


def append_tag_time_series(tag_time_series, dt, github_tag):
    try:
        tag_time_series.setdefault(github_tag.tag_name, []).append((dt, github_tag))
    except AttributeError as e:
        print(github_tag)
        raise


def collect_tag_time_series(tag_time_series, dt, releases):
    all_assets = []

    for release in releases:
        github_tag = GitHubTag(release)
        append_tag_time_series(tag_time_series, dt, github_tag)
                
        all_assets += release['assets']
    
    presudo_github_tag = GitHubTag({
        'tag_name': 'total',
        'id': 0,
        'assets': all_assets
    })

    append_tag_time_series(tag_time_series, dt, presudo_github_tag)


def create_chart_data_entry(tag_name):
    download_counts = {}

    def download_counter(github_tag):
        for asset in github_tag.assets:
            download_counts[asset.id] = asset.download_count
        
        return sum(download_counts.values())

    return {
        'series': tag_name,
        'points': list(map(
            lambda obj: {'x': obj[0], 'y': download_counter(obj[1])},
            sorted(tag_time_series[tag_name], key=lambda obj: obj[0])
        ))
    }


def create_chart_data(tag_time_series):
    chart_data = []

    for tag_name in sorted(tag_time_series.keys(), reverse=True):
        entry = create_chart_data_entry(tag_name)

        if tag_name == 'total':
            chart_data.insert(0, entry)
        else:
            chart_data.append(entry)

    return chart_data


if __name__ == '__main__':
    github_account = sys.argv[1]
    github_reposlist = sys.argv[2]

    base_dir = pathlib.PurePath(github_account, github_reposlist)

    github_reositories = exastics._reposlist.publish_api(base_dir)

    chart_index = []
    total_index = []
    for github_repository in github_reositories:
        if (github_repository != "gathering" and github_repository != "gathering"):
            base_dir = pathlib.PurePath(github_account, github_repository)

            output_file = pathlib.PurePath(f'./docs/assets/chart-data/{github_repository}-github-download-count.json')

            chart_index.append({
                'caption'   : f'{github_repository}',
                'data_file' : f'assets/chart-data/{github_repository}-github-download-count.json'
            })

            tag_time_series = {}
            for dt, github_releases in exastics._chartdata.get_datetime_and_json_data(base_dir):
                collect_tag_time_series(tag_time_series, dt, github_releases)

            chart_data = create_chart_data(tag_time_series)

            with open(output_file, 'w') as f:
                json.dump(chart_data, f, indent=4)

            total_index.append({
                'date': chart_data[0]["points"][-1]["x"],
                'count_accum': chart_data[0]["points"][-1]["y"],
                'count_today': chart_data[0]["points"][-1]["y"] - chart_data[0]["points"][-2]["y"],
                'repos': github_repository
            })

    output_file = pathlib.PurePath(f'./docs/assets/chart-data/all-repos-github-download-count.json')

    chart_index.insert(0, {
        'caption'   : f'download count',
        'data_file' : f'assets/chart-data/all-repos-github-download-count.json'
    })

    with open(output_file, 'w') as f:
        json.dump(total_index, f, indent=4)

    output_file = pathlib.PurePath(f'./docs/assets/chart-index.json')

    with open(output_file, 'w') as f:
        json.dump(chart_index, f, indent=4)

