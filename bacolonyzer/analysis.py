"""Functions to compute the outputs that will be saved.
"""
import logging
import os
import re
import time

import cv2
import numpy as np
import pandas as pd
from bacolonyzer import filesystem, image_processing
from scipy.signal import find_peaks

logger = logging.getLogger(__name__)


def analyse_timeseries_qfa(images_paths,
                           nrow,
                           ncol,
                           output_dir,
                           light_correction=False,
                           fraction=0.8,
                           reference_image=""):
    # Set timer
    start_time = time.time()

    # Obtain first and last image
    latest_image = images_paths[-1]
    earliest_image = images_paths[0]

    # Print information to users
    logger.debug("")
    logger.debug("Starting analysis:")
    logger.debug("Earliest image: %s", earliest_image)
    logger.debug("Latest image: %s", latest_image)
    logger.debug("")
    logger.debug("Computing position of the grid")
    logger.debug("This may take a few seconds...")
    logger.debug("")

    # Get latest image to detect culture locations
    im_n = cv2.imread(latest_image, cv2.IMREAD_GRAYSCALE)

    # Perform some normalization in order to remove outliers and noise.
    # The 1% and 99% quantile clipping is a good option.
    quants = np.quantile(im_n.ravel(), [0.01, 0.99])
    im_n = np.clip(im_n, *quants)
    im_n = np.array(im_n, dtype=np.uint8)

    _, min_loc, pat_h, pat_w = image_processing.get_position_grid(
        im_n, nrow, ncol, fraction)

    # Cut the original image with the size of the best pattern match.
    w_right = int(min_loc[0] + pat_w)
    h_bottom = int(min_loc[1] + pat_h)
    im_ = im_n[min_loc[1]:h_bottom, min_loc[0]:w_right]

    # Find spots and agar based on an automatic threshold and last image
    _, mask = cv2.threshold(
        np.array(im_, dtype=np.uint8), 0, 255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Locate the position of the spots and the agar into different masks.
    grd = np.ones(mask.shape, dtype=bool)
    spots = np.logical_and(grd, ~mask)
    agar = np.logical_and(grd, mask)

    # Reset mask to avoid problems in future iterations.
    mask = None

    # Obtain maximum and minimum intensity that we can observe with camera
    if reference_image:
        min_ref, max_ref = image_processing.calibration_maxmin(reference_image)
    else:
        min_ref, max_ref = 0, 255

    logger.debug("Analysing each of the images:")
    for file_name in images_paths:

        img = cv2.imread(file_name, cv2.IMREAD_GRAYSCALE)
        arr = img[min_loc[1]:h_bottom, min_loc[0]:w_right]

        # Assume area of spots will always be =< spots at last image, so
        # set all pixels that are not spots to agar to remove noise
        arr_modified = arr.copy()
        color_agar = np.mean(arr_modified[agar])
        arr_modified[agar] = color_agar
        arr_modified = cv2.GaussianBlur(img, (15, 15), 0)

        # Set threshold automatically
        thresh, _ = cv2.threshold(
            np.array(arr_modified, dtype=np.uint8), 0, 255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Define threshold value between agar color and automatic threshold
        thresh = max((thresh + color_agar) / 2, color_agar + 1)

        # Create mask to detect spots in each image.
        # This will be used only to compute the area of the spots.
        mask = np.ones(arr.shape, dtype=np.bool)
        mask[arr < thresh] = False
        mask[agar] = False

        # Normalize image by using reference picture provided
        arr = (arr - min_ref) / (max_ref - min_ref)

        # Measure culture phenotypes.
        df = measure_outputs(arr, mask, pat_h, pat_w, nrow, ncol, file_name,
                             spots, light_correction)

        # Save mask for a visual check.
        mask = mask.astype(np.uint8) * 255

        logger.debug("Analysis complete for %s", os.path.basename(file_name))

        # Saving output.
        base_name = filesystem.get_file_name(file_name)
        filesystem.save_output(base_name, df, mask, output_dir)

    logger.debug("All analyses finished in {:.2f} seconds".format(time.time() -
                                                                  start_time))


def measure_outputs(im, mask, pat_h, pat_w, nrow, ncol, file_name, spots,
                    correction):
    """Add intensity measures and other measurements to a final dictionary.
    This dictionary will be outputed as a data-frame.
    """
    # Outputs will be saved in a dictionary with the following features.
    allrows, allcols, allintensities, allareas = [], [], [], []
    allcolonymeans, allcolonyvariance, allbackgroundmeans = [], [], []

    # Extract the windows for each spot. First get the window widht and heigh.
    d_x = int(pat_h / nrow)
    d_y = int(pat_w / ncol)

    # From now on: reference point is the top left corner of the rectangle.
    for i in range(nrow):
        for j in range(ncol):
            # Compute position x of each window or patch
            p_x = j * d_x  # Position x = ncol x dimension_x of window (d_x)
            p_y = i * d_y  # Position y = nrow x dimension_y of window (d_y)
            # Get window of this specific colony
            patch = im[p_y:p_y + d_y, p_x:p_x + d_x]
            mask_patch = mask[p_y:p_y + d_y, p_x:p_x + d_x]
            spots_patch = spots[p_y:p_y + d_y, p_x:p_x + d_x]

            # Perform some normalization in order to remove outliers and noise.
            # The 1% and 99% quantile clipping is a good option.
            quants = np.quantile(patch.ravel(), [0.01, 0.99])
            patch = np.clip(patch, *quants)

            # Compute area of colony based on the mask_patch
            area_patch = np.sum(mask_patch) / patch.size
            # Compute background mean of patch that will be useful to correct
            # for differences in intensity between AND within images
            if correction:
                backgr = np.mean(patch[~spots_patch])
            else:
                backgr = 0

            # Compute tiles intensities and filter only according to spots
            tile = patch - backgr
            spot_intensities = tile[spots_patch]

            # If there are colonies in the window or patch, compute metrics
            if spot_intensities.size > 1:
                # Compute the mean of the intensity (Normalized from 0 to 1)
                colony_mean_patch = np.mean(spot_intensities)
                # Compute the variance of the intensity
                colony_variance_patch = np.var(spot_intensities)
            else:  # If there aren't colonies in the window, intensities are 0
                colony_mean_patch = colony_variance_patch = 0

            # Compute all intensity values normalized by the size of window
            intens_patch = np.sum(tile) / tile.size

            # Compute agar information (agar is the opposite to the mask)
            bkgrnd = tile[~spots_patch]

            # If there is background in the patch, compute mean of intensities
            if bkgrnd.size > 1:
                background_mean_patch = np.mean(bkgrnd)
            else:  # If there is no background in the patch, intensities are 0
                background_mean_patch = 0

            # Save all variables in the final lists
            allrows.append(i + 1)
            allcols.append(j + 1)
            allintensities.append(intens_patch)
            allareas.append(area_patch)
            allcolonymeans.append(colony_mean_patch)
            allcolonyvariance.append(colony_variance_patch)
            allbackgroundmeans.append(background_mean_patch)

    # Save final outputs
    fname = filesystem.get_file_name(file_name)
    brcod = re.sub("\D[\d]+-[\d]+-[\d]+.*", "", fname)
    return pd.DataFrame({
        "Row": allrows,
        "Column": allcols,
        "Intensity": allintensities,
        "Area": allareas,
        "ColonyMean": allcolonymeans,
        "ColonyVariance": allcolonyvariance,
        "BackgroundMean": allbackgroundmeans,
        "Barcode": [brcod] * len(allrows),
        "Filename": [fname] * len(allrows),
    })
