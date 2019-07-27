"""Functions to prepare de directories and to obtain the files for analysis.
"""

import logging
import os
import shutil

import numpy as np

logger = logging.getLogger(__name__)


def arrange_directories(remove, directory):
    '''Remove and create directory to save output files.
    Return a boolean showing if output data folder is empty'''
    # Set directories to keep and/or remove and create
    imdir = os.path.join(directory, "Output_Images")
    datdir = os.path.join(directory, "Output_Data")

    # Define variable do_check to see if some analysis are already done
    do_check = True

    if remove and os.path.isdir(imdir):  # Remove existing output directories
        shutil.rmtree(imdir)
    if remove and os.path.isdir(datdir):
        shutil.rmtree(datdir)

    if not os.path.isdir(imdir):  # Create directories to save the outputs
        os.mkdir(imdir)
    if not os.path.isdir(datdir):
        os.mkdir(datdir)
        do_check = False  # If the directory has just been created, do_check = F

    logger.debug("Outputs will be saved in " + imdir + " & " + datdir)
    return do_check


def get_images(directory, docheck, endpoint):
    '''Get filenames for all images in current directory.
    Return a list of filenames to analyse'''

    # Set image formats that will be considered (.tif will also include .tiff)
    image_formats = [".jpg", ".jpeg", ".tif", ".png"]
    # Obtain all file names in the specified directory
    filenames = os.listdir(directory)

    # Take only the images from the directory (images have any image_formats)
    # TODO(judithbergada): Using os.path.splitext will help to make one single
    # loop
    allfiles = [
        newfile for newfile in filenames
        if any(nformat in newfile.lower() for nformat in image_formats)
    ]
    allfiles.sort()

    # If there's a need to check analysed outputs
    if docheck:
        # Obtain all file names from the folder of analysed data
        datdir = os.path.join(directory, "Output_Data")
        outputfiles = os.listdir(datdir)
        # Take names of all files that have already been analysed
        formatending = ".out"
        alldats = [
            newfile for newfile in outputfiles
            if formatending in newfile.lower()
        ]
        # Obtain only the names (remove .format)
        ims_done = list(np.unique([dat.split(".")[0] for dat in alldats]))
    else:
        ims_done = []

    # If endpoint is True, then take only first and last images
    if endpoint:
        allfiles = [allfiles[-1]]

    # Obtain all images to analyse
    imanalyse = []
    for filename in allfiles:
        fbase = filename.split(".")[0]  # Obtain only names (remove .format)
        if fbase not in ims_done:  # If image is not analysed, add to the "todo"
            fullfilename = os.path.join(directory, filename)
            imanalyse.append(fullfilename)

    # If there aren't any new images to analyse, display error and exit
    if not imanalyse:
        raise ValueError("No new images to analyse in " + directory + ".")
    return imanalyse
