import datetime
import glob
import os

from bacolonyzer.commands import abstract
from PIL import Image


class RenameImagesCommand(abstract.AbstractCommand):

    _SUBCOMMAND = 'rename_images'
    _DESCRIPTION = """\
    Rename image files according to date time format. By default it only shows
    the renaming of the image files, without applying the modification. Use the
    flag --no_dry_run to apply the renaming.
    """

    def register_arguments(self, parser):
        parser.add_argument(
            "-d",
            "--directory",
            help="""Directory where the images are stored.
            Default: current directory.""",
            default=".")
        parser.add_argument(
            "-g",
            "--glob",
            help="""Glob to match all images in the given directory.
            Default: *.jpg (matches all jpg files).""",
            default="*.[Jj][Pp][Gg]")
        parser.add_argument(
            "-p",
            "--prefix",
            help="File prefix for the ranaming. Default: QFA_90000000001_.",
            default="QFA_90000000001_")
        parser.add_argument(
            "-m",
            "--no_read_metadata",
            help="""By default, image files will be renamed using the date and
            time information retrieved from images metadata. If you specify
            this flag, the renaming will take place according to
            parameters -s and -i.""",
            action="store_true")
        parser.add_argument(
            "-s",
            "--start_time",
            help="""Initial time for files renaming.
            Required format: 'YYYY-MM-DD hh:mm'. Default: now.""",
            type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d %H:%M'),
            default=datetime.datetime.now())
        parser.add_argument(
            "-i",
            "--interval",
            help="Time interval between files in minutes. Default: 30.",
            type=int,
            default=30)
        parser.add_argument(
            "--no_dry_run",
            help="""By default the change of names won't take place.
            If you specify this flag the renaming will take place.""",
            action="store_true")

    def run(self, args):
        # Get list of files to rename.
        file_names = glob.glob(os.path.join(args.directory, args.glob))
        file_names.sort()

        if not file_names:
            raise RuntimeError(
                'No file names found with the glob expression: {}'.format(
                    args.glob))
        print('Found {} files to rename.'.format(len(file_names)))

        # Define starting date time and time interval according to -s and -i
        current_datetime = args.start_time
        delta_time = datetime.timedelta(minutes=args.interval)

        for file_path in file_names:
            # Get extension of the files
            extension = os.path.splitext(file_names[0])[1]

            if args.no_read_metadata:
                # Use default or imputed values of date and time
                date_time = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
                current_datetime += delta_time
            else:
                # Obtain date and time from image metadata
                exif_data = Image.open(file_path)._getexif()
                if not exif_data:
                    raise RuntimeError(
                        '''Metadata is not available from these images.
                        Please, use parameters -m, -s and -i
                        to properly rename your images.''')
                else:
                    exif_data = exif_data[36867]
                    d_t = datetime.datetime.strptime(exif_data,
                                                     '%Y:%m:%d %H:%M:%S')
                    date_time = d_t.strftime("%Y-%m-%d_%H-%M-%S")

            # Create new file name
            new_file_name = args.prefix + date_time + extension
            new_path = os.path.join(os.path.dirname(file_path), new_file_name)

            # Show the renaming to the user.
            print("{} -> {}".format(file_path, new_path))
            # If specified by users, perform the actual renaming of files.
            if args.no_dry_run:
                os.rename(file_path, new_path)

        # Print information to users
        if args.no_dry_run:
            print("All files renamed!")
