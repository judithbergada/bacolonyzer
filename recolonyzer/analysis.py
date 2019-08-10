"""Functions to compute the outputs that will be saved.
"""
import logging
import os
import time

import cv2
import numpy as np
import pandas as pd

from recolonyzer import filesystem, image_processing

logger = logging.getLogger(__name__)


def analyse_timeseries_qfa(images_paths,
                           nrow,
                           ncol,
                           light_correction=False,
                           fraction=0.8):
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
    _, min_loc, pat_h, pat_w = image_processing.get_position_grid(
        im_n, nrow, ncol, fraction)

    # Cut the original image with the size of the best pattern match.
    w_right = int(min_loc[0] + pat_w)
    h_bottom = int(min_loc[1] + pat_h)
    im_ = im_n[min_loc[1]:h_bottom, min_loc[0]:w_right]

    # Find spots and agar based on an automatic threshold
    _, mask = cv2.threshold(
        np.array(im_, dtype=np.uint8), 0, 255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Locate the position of the spots and the agar into different masks.
    grd = np.ones(mask.shape, dtype=bool)
    spots = np.logical_and(grd, ~mask)  # grd & ~mask
    agar = np.logical_and(grd, mask)  # grd & mask

    # Reset mask to avoid problems in future iterations.
    mask = None

    output_dfs = []
    output_images = []
    logger.debug("Analysing each of the images:")
    for file_name in images_paths:

        img = cv2.imread(file_name, cv2.IMREAD_GRAYSCALE)
        arr = img[min_loc[1]:h_bottom, min_loc[0]:w_right]

        # Set threshold depending on last image
        thresh, _ = cv2.threshold(
            np.array(arr, dtype=np.uint8), 0, 255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        # If the threshold is lower than the values of the agar, set it higher.
        thresh = max(thresh, np.mean(arr[agar]) + 1)

        # Create mask to detect spots in each image.
        # This will be used only to compute the area of the spots.
        mask = np.ones(arr.shape, dtype=np.bool)
        mask[arr < thresh] = False

        # Measure culture phenotypes.
        output_dfs.append(
            measure_outputs(arr, mask, pat_h, pat_w, nrow, ncol, file_name,
                            spots, light_correction))

        # Save mask for a visual check.
        output_images.append(mask.astype(np.uint8) * 255)

        # Reset mask to avoid problems in the next iteration.
        mask = None
        logger.debug("Analysis complete for %s", os.path.basename(file_name))
    logger.debug("All analyses finished in {:.2f} seconds".format(time.time() -
                                                                  start_time))
    return output_dfs, output_images


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

    # Maximum intensity that we can see in a grayscale image is 255.
    int_max = 255

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

            # If there are colonies in the window (window = patch)
            if spot_intensities.size > 1:
                # Compute the mean of the intensity (Normalized from 0 to 1)
                colony_mean_patch = np.mean(spot_intensities / int_max)
                # Compute the variance of the intensity
                colony_variance_patch = np.var(spot_intensities / int_max)
                # Compute all intensity values normalized by the size of window
                intens_patch = np.sum(spot_intensities) / (tile.size * int_max)
            else:  # If there aren't colonies in the window, intensities are 0
                colony_mean_patch = colony_variance_patch = intens_patch = 0

            # Compute agar information (agar is the opposite to the mask)
            bkgrnd = tile[~spots_patch]

            # If there is background in the patch, compute mean of intensities
            if bkgrnd.size > 1:
                background_mean_patch = np.mean(bkgrnd / int_max)
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
    return pd.DataFrame({
        "Row": allrows,
        "Column": allcols,
        "Intensity": allintensities,
        "Area": allareas,
        "ColonyMean": allcolonymeans,
        "ColonyVariance": allcolonyvariance,
        "BackgroundMean": allbackgroundmeans,
        "Barcode": [fname[0:15]] * len(allrows),
        "Filename": [fname] * len(allrows),
    })
