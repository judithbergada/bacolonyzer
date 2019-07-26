"""Functions to set the inputs that will be used.
"""

# Import packages
import os


def get_directory(args):
    # Set variable fdir = current directory, if user didn't specify another dir
    if args.directory == None:
        fdir = os.getcwd()
    # Set variable fdir = directory chosen by the user, if a dir is specified
    else:
        fdir = os.path.realpath(args.directory)
        # Make sure that the directory exists. Otherwise, print error and exit
        if not os.path.isdir(fdir):
            raise ValueError("Directory doesn't exist. Check --directory.")
    return fdir


# Set input parameters for analysis
def buildVars(args):
    '''Read user input, set up flags for analysis, report on
    options chosen and find files to be analysed.'''
    inp = args

    # Set variables nrow and ncol according to rows and columns provided
    nrow, ncol = get_grid_format(inp.gridformat)

    # If required by the user, summarise basic input information
    if not args.quiet:
        print("")
        print("Summary of inputs:")
        print("Grid:")
        print("Expecting {} rows and {} columns on plate.".format(nrow, ncol))
        print("Searching for colony locations automatically.")
        print("Assuming that grid occupies at least {:.1f}%".format(
            args.fraction * 100))

        print("Corrections:")
        if inp.lightcorrection:
            print("Lighting correction turned on.")
            print("Using first image as best estimate of pseudo-empty plate.")
        else:
            print("Lighting correction turned off.")

        print("Analysis:")
        if inp.endpoint:
            print("Analysing only last image in series.")
        else:
            print("Analysing the entire set of images in series.")

        if inp.remove:
            print("Removing any outputs existing in the directory.")
        else:
            print("Outputs that exist in the directory will not be removed.")

    input_params = {
        'endpoint': inp.endpoint,
        'remove': inp.remove,
    }
    return (input_params)


# Utils methods
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
        raise ValueError('''Wrong dimensions for a rectangular grid format.
        Check variable --gridformat and modify it accordingly.''')
    return nrow, ncol
