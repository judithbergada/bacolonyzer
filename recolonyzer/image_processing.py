"""Functions to get the agar and spot colors and to locate the grid.
"""

import itertools

import cv2
import numpy as np
from scipy.signal import find_peaks
from tqdm import tqdm


def get_agar_spot_color(im):
    """Get the color value of the agar and the spot.
    Obtain the values by checking the largest two peaks in the color histogram.
    """
    im_ = np.asarray(im).ravel()
    bincnt = np.bincount(im_)

    peaks, _ = find_peaks(bincnt, width=3)
    vals = bincnt[peaks]
    idx = np.argsort(vals)[::-1]

    # Take first peak: this will be the agar
    color_agar = peaks[idx[0]]
    # Take second peak: these will be the spots
    color_spot = peaks[idx[1]]
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

    #Create the pattern of circles following the grid structure.
    rpix = int(h / nrow)  # Set random size of window that will later be scaled
    rspot = int((rpix * 0.7) / 2)  # Set random size of spot radius to scale
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
        pat_h, pat_w = int(h * fraction), int(w * fraction)
        pattern_scaled = cv2.resize(pattern, (pat_w, pat_h))
        # Match the scaled pattern with the image.
        res = cv2.matchTemplate(im, pattern_scaled, cv2.TM_SQDIFF_NORMED)
        # The function gives the map of squared difference, so optimal location
        # will be the one with minimum value.
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if found is None or min_val < found[0]:
            found = (min_val, min_loc, pat_h, pat_w)
    return found
