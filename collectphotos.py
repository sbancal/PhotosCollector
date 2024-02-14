#!/usr/bin/env python3

import argparse
import hashlib
import os
import re
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

from PIL import Image

EXTENSIONS = [".jpg", ".jpeg"]
OPERATION = "ln"  # "copy" or "move" or "ln"
NO_EXIF_FOLDER = "no_exif"
NO_EXIF_FILE_NB_DIGITS = 7
SHOW_PROGRESS_EVERY = 10


def parse_options():
    """
    Parse the command line options
    Returns: Namespace(source=['src'], dest='dest')
    """

    def validate_folder(folder_name):
        if not os.path.isdir(folder_name):
            print(f"Error: Folder '{folder_name}' doesn't exist.", file=sys.stderr)
            sys.exit(1)

    parser = argparse.ArgumentParser(description="Collect photos and sort them by date")
    parser.add_argument("-s", "--source", nargs="+", help="The source folders")
    parser.add_argument("-d", "--dest", required=True, help="The destination folder")
    args = parser.parse_args()

    for source in args.source:
        validate_folder(source)
    validate_folder(args.dest)

    return args


class CheckSumManager:
    """
    Manage the checksums of files
    """

    def __init__(self):
        self.checksums = {}

    def process(self, file):
        """
        Process the checksum of a file
        """
        if file not in self.checksums:
            with open(file, "rb") as f:
                self.checksums[file] = hashlib.sha256(f.read()).hexdigest()

    def is_unique(self, file):
        """
        Returns the a boolean that confirms that the file is unique
        based on its checksum
        """
        self.process(file)
        # count how many times the checksum appears in the list of checksums
        # if it appears more than once, it's not unique
        count = len(
            list(filter(lambda x: x == self.checksums[file], self.checksums.values()))
        )
        return count == 1

    def dump(self):
        print("Checksums:")

        for file, checksum in sorted(self.checksums.items(), key=lambda item: item[1]):
            print(f"{checksum}: {file}")

        print()


class NoExifFolder:
    """
    Manage the NO_EXIF_FOLDER with a counter to name each file
    """

    def __init__(self, dest, check_sum_manager):
        self.dest = Path(dest) / NO_EXIF_FOLDER
        self.last_file_nb = 0
        for file in self.dest.rglob("*"):
            result = re.match(
                r"(\d{" + str(NO_EXIF_FILE_NB_DIGITS) + r"})\.(jpg|jpeg)",
                file.name,
                re.IGNORECASE,
            )
            if result:
                self.last_file_nb = max(self.last_file_nb, int(result.group(1)))
            check_sum_manager.process(file)

    def get_next_file_name(self):
        self.last_file_nb += 1
        return f"{self.last_file_nb:0{NO_EXIF_FILE_NB_DIGITS}}"


def browse_source(source_folder, dest_folder):
    """
    Browse the source folder and launch the processing of each file
    """
    tools = SimpleNamespace()
    tools.check_sum_manager = CheckSumManager()
    tools.no_exif_folder = NoExifFolder(dest_folder, tools.check_sum_manager)
    tools.counts = {
        "total_processed": 0,
        "no_date_collected": 0,
        "total_collected": 0,
        "duplicate": 0,
    }

    for file in Path(source_folder).rglob("*"):
        if file.suffix.lower() not in EXTENSIONS:
            # print(f"Skip {file=} (not a photo)")
            continue
        process_file(file, dest_folder, tools)
        tools.counts["total_processed"] += 1
        if tools.counts["total_processed"] % SHOW_PROGRESS_EVERY == 0:
            print(".", end="", flush=True)

    print(f"Processed {tools.counts['total_processed']} files")
    print(f"Collected {tools.counts['total_collected']} photos")
    print(f"Collected {tools.counts['no_date_collected']} photos with no date")
    print(f"Skipped {tools.counts['duplicate']} duplicates")


def process_file(file, dest_folder, tools):
    """
    Determine where to place the file and request the operation on it
    """
    try:
        exif = Image.open(file)._getexif()
        date = exif[36867]
        ymd, hms = date.split(" ")
        yyyy, mm, dd = ymd.split(":")
        hh, mi, ss = hms.split(":")
        dest = Path(dest_folder) / f"{yyyy}-{mm}"
        filename = f"{yyyy}-{mm}-{dd}_{hh}-{mi}-{ss}"
        no_date = False
    except (KeyError, TypeError):
        if not tools.check_sum_manager.is_unique(file):
            tools.counts["duplicate"] += 1
            return
        dest = tools.no_exif_folder.dest
        filename = tools.no_exif_folder.get_next_file_name()
        no_date = True

    operate_file(file, dest / filename, file.suffix, tools, no_date)


def operate_file(src, dest, suffix, tools, no_date, index=0):
    """
    Copy / move / hardlink the file to the destination (according to OPERATION)
    In case of name conflict, check if the file is a duplicate. If not, add a suffix
    """
    if index == 0:
        str_index = ""
    else:
        str_index = f"_{index}"
    full_dest = f"{dest}{str_index}{suffix}"
    if Path(full_dest).exists():
        tools.check_sum_manager.process(full_dest)
        if not tools.check_sum_manager.is_unique(src):
            tools.counts["duplicate"] += 1
            return
        return operate_file(src, dest, suffix, tools, no_date, index + 1)
    if OPERATION == "copy":
        # print(f"cp {src} {full_dest}")
        try:
            shutil.copy2(src, full_dest)
            if no_date:
                tools.counts["no_date_collected"] += 1
            else:
                tools.counts["total_collected"] += 1
        except FileNotFoundError:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, full_dest)
            if no_date:
                tools.counts["no_date_collected"] += 1
            else:
                tools.counts["total_collected"] += 1
    elif OPERATION == "move":
        # print(f"mv {src} {full_dest}")
        try:
            shutil.move(src, full_dest)
            if no_date:
                tools.counts["no_date_collected"] += 1
            else:
                tools.counts["total_collected"] += 1
        except FileNotFoundError:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src, full_dest)
            if no_date:
                tools.counts["no_date_collected"] += 1
            else:
                tools.counts["total_collected"] += 1
    elif OPERATION == "ln":
        # print(f"ln {src} {full_dest}")
        try:
            os.link(src, full_dest)
            if no_date:
                tools.counts["no_date_collected"] += 1
            else:
                tools.counts["total_collected"] += 1
        except FileNotFoundError:
            dest.parent.mkdir(parents=True, exist_ok=True)
            os.link(src, full_dest)
            if no_date:
                tools.counts["no_date_collected"] += 1
            else:
                tools.counts["total_collected"] += 1
    else:
        print(f"Error: Unknown operation {OPERATION}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    options = parse_options()

    for source in options.source:
        browse_source(source, options.dest)