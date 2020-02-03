"""Definition of all commands available in BaColonyzer."""
import logging

from bacolonyzer import analysis, filesystem, utils
from bacolonyzer.commands import abstract

logger = logging.getLogger(__name__)


class AnalyseCommand(abstract.AbstractCommand):

    _SUBCOMMAND = 'analyse'
    _DESCRIPTION = """\
    Analyse timeseries of QFA images: locate cultures on
    plate, segment image into agar and cells, apply lighting correction,
    and generate output files for each image.
    """

    def register_arguments(self, parser):
        parser.add_argument(
            "-d",
            "--directory",
            type=str,
            help="""Directory in which to search for image files that need to be
            analysed.
            Default: current directory.""",
            default=".")
        parser.add_argument(
            "-c",
            "--light_correction_off",
            help="""Disables lighting correction between images.
            Default: Light correction is enabled.""",
            action="store_false")
        parser.add_argument(
            "-r",
            "--reference_image",
            type=str,
            help="""Path to a reference image that shows a white and a black
            paper next to each other. Important: this picture must be taken
            using the same camera settings as the image series. This is used
            to calibrate the final results and might be useful to compare
            different experiments.
            Default: No reference image is used.""",
            default="")
        parser.add_argument(
            "-q",
            "--quiet",
            help="""Suppresses messages printed during the analysis.
            Default: show messages.""",
            action="store_true")
        parser.add_argument(
            "-e",
            "--endpoint",
            help="""Analyses only the final image in the series.
            It is useful to test single images.
            Default: False. Analyse all images in the directory.""",
            action="store_true")
        parser.add_argument(
            "-g",
            "--grid_format",
            type=str,
            nargs='+',
            help="""Specifies rectangular grid format.
            Important: specify number of rows and number of columns, in this order
            (e.g. -g 8x12 or -g 8 12).
            Default: 8x12.""",
            default=['8x12'])
        parser.add_argument(
            "-f",
            "--fraction",
            type=utils.range_float,
            help="""Specifies the minimum fraction of the image that corresponds
            to the grid. Adjust it if grid occupies a small part of the total image.
            Default: 0.8.""",
            default=0.8)

    def run(self, args):
        # Setup logger
        if args.quiet:
            logging.basicConfig(format="%(message)s", level=logging.INFO)
        else:
            logging.basicConfig(format="%(message)s", level=logging.DEBUG)

        # Print information of inputs to users.
        utils.summarise(args)

        # Get working directory.
        fdir = filesystem.get_directory(args.directory)
        nrow, ncol = utils.get_grid_format(args.grid_format)

        # Create needed directories to save outputs.
        filesystem.arrange_directories(fdir)
        # Obtain list of images to analyse.
        imanalyse = filesystem.get_images(fdir, args.endpoint,
                                          args.reference_image)

        # Perform main logic.
        analysis.analyse_timeseries_qfa(
            imanalyse,
            nrow,
            ncol,
            fdir,
            light_correction=args.light_correction_off,
            fraction=args.fraction,
            reference_image=args.reference_image)

        logger.info("No more images to analyse. I'm done")
