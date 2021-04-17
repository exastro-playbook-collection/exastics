#!/usr/bin/env python3

import exastics._cleanup
import exastics._collect
import pathlib
import sys
import urllib.parse

if __name__ == '__main__':
    github_account = sys.argv[1]
    github_reposlist = sys.argv[2]

    base_dir = pathlib.PurePath(github_account, github_reposlist)

    exastics._cleanup.publish_api(base_dir)

    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }

    url_parts = (
        'https',
        'api.github.com',
        urllib.parse.quote(f'/users/{github_account}/repos'),
        '',
        'per_page=100&page=1',
        ''
    )

    exastics._collect.publish_api(url_parts, headers, base_dir)

    url_parts = (
        'https',
        'api.github.com',
        urllib.parse.quote(f'/users/{github_account}/repos'),
        '',
        'per_page=100&page=2',
        ''
    )

    exastics._collect.publish_api(url_parts, headers, base_dir)

