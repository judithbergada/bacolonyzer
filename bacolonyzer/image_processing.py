"""Functions to get the agar and spot colors, to locate the grid, and to
calibrate the image colors according to a black and white reference picture.
"""

import itertools
import os

import cv2
import numpy as np
from scipy.signal import find_peaks
from tqdm import tqdm


def get_agar_spot_color(im):
    """Get the color value of the agar and the spot.
    Obtain the values by checking the largest two peaks in the color histogram.
    """
    im_ = np.asarray(im).ravel()

    # Compute histogram of intensities
    bincnt = np.bincount(im_)

    # Find peaks in histogram
    peaks, _ = find_peaks(bincnt, width=3)
    vals = bincnt[peaks]
    idx = np.argsort(vals)[::-1]

    # Take first peak: this will be the agar, as it's the most abundant color
    color_agar = peaks[idx[0]]

    # Force the color of the spot to be higher than the color of the agar.
    second_idx = idx[idx > idx[0]]
    color_spot = peaks[second_idx[0]]

    # Set limits that are resonable to avoid noise affecting results
    lower_lim_spots = 2 * color_agar
    upper_lim_spots = 0.7 * im_.max()
    if color_spot < lower_lim_spots:
        color_spot = min(lower_lim_spots, upper_lim_spots)
    elif color_spot > upper_lim_spots:
        color_spot = max(lower_lim_spots, upper_lim_spots)

    return int(color_agar), int(color_spot)


def get_position_grid(im, nrow, ncol, frac):
    """Get the position of the grid in the image.
    Use an artificial pattern and the normalized squared difference to find it.
    Return the position of the grid and the size of the scaled the pattern.
    """
    # Find color values of agar and spots
    color_agar, color_spot = get_agar_spot_color(im)
    # Size of the given image.
    h, w = im.shape

    # Create the pattern of circles following the grid structure.
    rpix = int(h / nrow)  # Set random size of window that will later be scaled
    rspot = int((rpix * 0.5) / 2)  # Set random size of spot radius to scale
    pattern = np.ones((nrow * rpix, ncol * rpix), dtype=np.uint8) * color_agar
    for i, j in itertools.product(range(nrow), range(ncol)):
        cv2.circle(pattern,
                   (j * rpix + int(rpix / 2), i * rpix + int(rpix / 2)), rspot,
                   color_spot, -1)

    # Check for structure between frac and 100% of the total image size.
    min_fraction, max_fraction = frac, 1.0
    # Check for structure using iterations by increasing 0.2% of the image
    iterations = int((max_fraction - min_fraction) * 100 / 0.2)

    # Store the info about the best scale where pattern fits the image.
    found = None
    for fraction in tqdm(
            np.linspace(min_fraction, max_fraction, iterations),
            desc='Fitting pattern...'):
        # Scale the pattern to the fraction of the given image.
        pat_w = int(w * fraction)
        pat_h = int(pat_w * nrow / ncol)
        pattern_scaled = cv2.resize(pattern, (pat_w, pat_h))
        # Match the scaled pattern with the image.
        res = cv2.matchTemplate(im, pattern_scaled, cv2.TM_SQDIFF_NORMED)
        # The function gives the map of squared difference, so optimal location
        # will be the one with minimum value.
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if found is None or min_val < found[0]:
            found = (min_val, min_loc, pat_h, pat_w)
    return found


def calibration_maxmin(ref_img):
    """Obtain minimum and maximum intensity values captured by the camera by
    using a reference image. This will be used to calibrate the final results.
    """

    # Make sure that reference image exists
    if os.path.isfile(ref_img):
        # Open reference image and get all the intensity values
        reference_image = cv2.imread(ref_img, cv2.IMREAD_GRAYSCALE)

        # # Take 1% and 99% quantiles of the reference image to remove noise
        quants = np.quantile(reference_image.ravel(), [0.01, 0.99])
        reference_image = np.clip(reference_image, *quants)

        min_ref = reference_image.min()
        max_ref = reference_image.max()
    else:
        logger.info(
            """Reference image not found. Calibration not performed.""")
        min_ref, max_ref = 0, 255
    return (min_ref, max_ref)
