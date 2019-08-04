#!/usr/bin/env python3

import argparse
import datetime
import glob
import os


def main(args):
    # Get list of files to rename
    file_names = glob.glob(os.path.join(args.directory, args.glob))
    file_names.sort()

    if not file_names:
        raise RuntimeError(
            'No file names found with the glob expression: {}'.format(
                args.glob))
    print('Found {} files to rename.'.format(len(file_names)))

    # Get extension of the files
    extension = os.path.splitext(file_names[0])[1]

    current_datetime = args.start_time
    delta_time = datetime.timedelta(minutes=args.interval)

    for file_path in file_names:
        file_name = os.path.splitext(os.path.basename(file_path))[0]

        new_file_name = args.prefix + current_datetime.strftime(
            "%Y-%m-%d_%H-%M-%S") + extension

        new_path = os.path.join(os.path.dirname(file_path), new_file_name)

        print("{} -> {}".format(file_path, new_path))
        if args.nodryrun:
            os.rename(file_path, new_path)

        current_datetime += delta_time

    if args.nodryrun:
        print("All files renamed!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Rename images names to follow a given dated pattern.')
    parser.add_argument(
        "-d",
        "--directory",
        help="Directory where the images are stored",
        default=".")
    parser.add_argument(
        "-g",
        "--glob",
        help="Glob to match all the images",
        default="*.[Jj][Pp][Gg]")
    parser.add_argument(
        "-p",
        "--prefix",
        help="File prefix to generate",
        default="QFA_90000000001_")
    parser.add_argument(
        "-s",
        "--start_time",
        help="Initial time for files renaming",
        type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d %H:%M'),
        default=datetime.datetime.now())
    parser.add_argument(
        "-i",
        "--interval",
        help="Time interval between files in minutes",
        type=int,
        default=30)
    parser.add_argument(
        "--nodryrun",
        help=
        "By default the change of names won't take place. If you specify this flag the renaming will take place.",
        action="store_true")

    args = parser.parse_args()

    main(args)
