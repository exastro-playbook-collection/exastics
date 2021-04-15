#!/usr/bin/env python3

import exastics._reposlist
import exastics._collect
import pathlib
import sys
import urllib.parse
import pprint


if __name__ == '__main__':
    github_account = sys.argv[1]
    github_reposlist = sys.argv[2]

    base_dir = pathlib.PurePath(github_account, github_reposlist)

    github_reositories = exastics._reposlist.publish_api(base_dir)

    for github_repository in github_reositories:

        url_parts = (
            'https',
            'api.github.com',
            urllib.parse.quote(f'/repos/{github_account}/{github_repository}/releases'),
            '',
            '',
            ''
        )

        headers = {
            'Accept': 'application/vnd.github.v3+json'
        }

        base_dir = pathlib.PurePath(github_account, github_repository)

        exastics._collect.publish_api(url_parts, headers, base_dir)

