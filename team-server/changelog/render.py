import glob
import json
import argparse
import yaml
from natsort import natsorted
import requests
from pathlib import Path
from collections import OrderedDict
from datetime import date


def get_current_release_dir() -> str:
    """Get the directory to the current release
    Returns:
    """
    releases = list()
    for release in glob.glob("./releases/*"):
        releases.append(release)

    releases = natsorted(releases)

    return releases[-1]


def generate_changelog() -> OrderedDict:
    """Method to generate the changelog data structure as an OrderedDict
    Returns:
        OrderedDict
    """
    latest_version_dir = get_current_release_dir()

    messages = list()
    changes = dict()
    for changelog_file in glob.glob(f"{latest_version_dir}/*.yaml"):
        contents = yaml.safe_load(Path(changelog_file).read_bytes())

        _, pr_number = contents['prLink'].rsplit('/', 1)

        if 'message' in contents:
            messages.append(contents['message'])

        for item in contents['changelog']:
            if item['type'] == "NON_USER_FACING":
                continue

            changes.setdefault(item['type'], []).append(f"{item['description']} (#{pr_number})")

    if len(messages) == 0:
        # legacy code requires an empty message string if no messages.
        messages.append("")

    # Add to existing file
    data = OrderedDict()
    data["date"] = str(date.today())
    data["changes"] = changes
    data["messages"] = messages
    _, data["version"] = latest_version_dir.rsplit("/", 1)

    return data


def render_markdown(output_dir: str) -> None:
    """Render the changelog data to a markdown file.
    Args:
        output_dir: directory to write file
    Returns:
        None
    """
    data = generate_changelog()
    md = ""

    md = md + f"## {data['date']}\n\n"
    md = md + f"### Team Server ({data['version']})\n\n"

    for section in data['changes']:
        md = md + f"* **{section}**\n"
        for change in data['changes'][section]:
            md = md + f"  * {change}\n"

        md = md + "\n"

    md = md + "\n\n"

    Path(Path(output_dir).expanduser().absolute(), 'changelog.md').write_text(md)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("--directory", '-d', default='.', help="Desired output directory.")

    args = parser.parse_args()

    render_markdown(args.directory)