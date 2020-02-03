"""Functions to prepare de directories and to obtain the files for analysis.
"""

import logging
import os

import cv2

logger = logging.getLogger(__name__)


def get_directory(directory=None):
    """Get directory to work with."""
    # Set variable fdir = current directory, if user didn't specify another dir
    if not directory:
        fdir = os.getcwd()
    # Set variable fdir = directory chosen by the user, if a dir is specified
    else:
        fdir = os.path.realpath(os.path.expanduser(directory))
        # Make sure that the directory exists. Otherwise, print error and exit
        if not os.path.isdir(fdir):
            raise ValueError("Directory doesn't exist. Check --directory.")
    return fdir


def arrange_directories(directory):
    """Creates directories to save output files."""
    # Set directories to keep or create.
    imdir = os.path.join(directory, "Output_Images")
    datdir = os.path.join(directory, "Output_Data")

    # Create directories to save the outputs.
    if not os.path.isdir(imdir):
        os.mkdir(imdir)
    if not os.path.isdir(datdir):
        os.mkdir(datdir)
    logger.debug("Outputs will be saved in " + imdir + " & " + datdir)


def get_images(directory, endpoint, reference_image):
    """Get filenames for all images in working directory.
    Return a list of filenames to analyse"""

    # Set image formats that will be considered.
    image_formats = {".jpg", ".jpeg", ".tif", ".tiff", ".png"}
    # Obtain all file names in the specified directory
    filenames = os.listdir(directory)

    # Take only the images from the directory (images have any image_formats)
    allfiles = [
        newfile for newfile in filenames
        if os.path.splitext(newfile.lower())[1] in image_formats
    ]
    allfiles.sort()

    # If endpoint is True, then take only first and last images
    if endpoint:
        allfiles = [allfiles[-1]]

    # Obtain all images to analyse
    imanalyse = []
    for filename in allfiles:
        fullfilename = os.path.join(directory, filename)
        # Make sure that the reference image is not included in timeseries
        if fullfilename != os.path.abspath(reference_image):
            imanalyse.append(fullfilename)

    # If there aren't any new images to analyse, display error and exit
    if not imanalyse:
        raise ValueError("No new images to analyse in " + directory + ".")
    imanalyse.sort()
    return imanalyse


def get_file_name(image_path):
    """Get file names from given path removing extension and directories."""
    return os.path.basename(os.path.splitext(image_path)[0])


def save_output(file_name, output_df, output_image, output_base_dir):
    """Saves output."""

    # Save DataFrame of output metrics.
    output_df.to_csv(
        os.path.join(output_base_dir, "Output_Data",
                     "{}.out".format(file_name)),
        sep="\t",
        index=False)
    # Save Image mask
    img_outputs_dir = os.path.join(output_base_dir, "Output_Images",
                                   "{}.png".format(file_name))
    cv2.imwrite(img_outputs_dir, output_image)
