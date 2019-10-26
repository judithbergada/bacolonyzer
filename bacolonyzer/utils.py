"""Functions to set the inputs that will be used.
"""

import logging

logger = logging.getLogger(__name__)


# Set input parameters for analysis
def summarise(args):
    """Read user input, set up flags for analysis, report on
    options chosen and find files to be analysed."""

    # Get variables nrow and ncol according to rows and columns provided
    nrow, ncol = get_grid_format(args.grid_format)

    # If required by the user, summarise basic input information
    logger.debug("")
    logger.debug("Summary of inputs:")
    logger.debug("Grid:")
    logger.debug("Expecting %s rows and %s columns on plate.", nrow, ncol)
    logger.debug("Searching for colony locations automatically.")
    logger.debug("Assuming that grid occupies at least {:.1f}%".format(
        args.fraction * 100))

    logger.debug("Corrections:")
    if args.light_correction_off:
        logger.debug("Lighting correction turned on.")
    else:
        logger.debug("Lighting correction turned off.")

    logger.debug("Analysis:")
    if args.endpoint:
        logger.debug("Analysing only last image in series.")
    else:
        logger.debug("Analysing the entire set of images in series.")


def get_grid_format(given_format):
    """Check that the input variable --gridformat is correct.
    Raise an error message if --gridformat is wrong.

    Extract number of rows and columns of the grid by using --gridformat.
    """
    error = False
    # If grid format is provided as nrow x ncol, separate the integers
    if len(given_format) == 1 and len(given_format[0].split("x")) == 2:
        tmp = given_format[0].split("x")
        # Make sure that digits are provided and are higher than 0
        if tmp[0].isdigit() and tmp[1].isdigit():  # Check that inputs are int
            if int(tmp[0]) > 0 and int(tmp[1]) > 0:  # Check that inputs > 0
                nrow, ncol = int(tmp[0]), int(tmp[1])
            else:
                error = True
        else:  # If grid format is not numeric or not separated by x, error
            error = True
    # If grid format is provided as 2 integers showing nrow ncol, use them
    elif len(given_format) == 2:  # Check that inputs are integers and > 0
        if given_format[0].isdigit() and given_format[1].isdigit():
            if int(given_format[0]) > 0 and int(given_format[1]) > 0:
                nrow, ncol = [int(x) for x in given_format]
            else:  # If inputs are not bigger than 0, error
                error = True
        else:  # If grid format is not numeric, error
            error = True
    # If grid format is wrong because there are too many dimensions, error
    else:
        error = True

    # If there has been an error, print it and exit
    if error:
        raise ValueError("""Wrong dimensions for a rectangular grid format.
        Check variable --gridformat and modify it accordingly.""")
    return nrow, ncol


def range_float(x):
    """Check the float is in [0, 1] range."""
    x = float(x)
    if x <= 0.0 or x >= 1.0:
        raise argparse.ArgumentTypeError("%r not in range (0.0, 1.0)" % (x, ))
    return x
