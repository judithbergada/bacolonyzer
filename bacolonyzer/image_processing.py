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
    """Get the color value of the agar and the spots.
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
    if len(second_idx) == 0:
        color_spot = 0.7 * im_.max()
    else:
        color_spot = peaks[second_idx[0]]

    # Set limits that are resonable to avoid noise affecting results
    lower_lim_spots = 2 * color_agar
    upper_lim_spots = 0.7 * im_.max()
    if color_spot < lower_lim_spots:
        color_spot = min(lower_lim_spots, upper_lim_spots)
    elif color_spot > upper_lim_spots:
        color_spot = max(lower_lim_spots, upper_lim_spots)

    return int(color_agar), int(color_spot)


def get_position_grid(im, nrow, ncol, frac, grid_by_peaks=False, image_path=None):
    """Get the position of the grid in the image.
    Use an artificial pattern and the normalized squared difference to find it,
    or use peak detection if grid_by_peaks is True.
    Return the position of the grid and the size of the scaled the pattern.
    """
    # Find color values of agar and spots
    color_agar, color_spot = get_agar_spot_color(im)

    # detect grid by peaks
    if grid_by_peaks:
        # Use the mean profile of the image to find peaks
        y_profile = im.mean(axis=1)
        x_profile = im.mean(axis=0)

        # find peaks, using a width and distance that is a fraction of the image and based on the number of rows and columns
        y_peaks_all, _ = find_peaks(
            y_profile,
            width=0.1 * frac * im.shape[0] // nrow,
            distance=0.75 * frac * im.shape[0] // nrow,
        )
        x_peaks_all, _ = find_peaks(
            x_profile,
            width=0.1 * frac * im.shape[1] // ncol,
            distance=0.75 * frac * im.shape[1] // ncol,
        )

        # Sort peaks by distance to the center of the image
        center_y = im.shape[0] // 2
        center_x = im.shape[1] // 2
        y_center_idx = np.argsort(np.abs(y_peaks_all - center_y))[:nrow]
        x_center_idx = np.argsort(np.abs(x_peaks_all - center_x))[:ncol]
        y_peaks = np.sort(y_peaks_all[y_center_idx])
        x_peaks = np.sort(x_peaks_all[x_center_idx])

        # get average distance between peaks to estimate the size of the pattern
        avg_dy = np.mean(np.diff(y_peaks))
        avg_dx = np.mean(np.diff(x_peaks))

        # find top-left corner of the pattern
        min_y = int(round(y_peaks[0] - 0.5 * avg_dy))
        min_x = int(round(x_peaks[0] - 0.5 * avg_dx))

        # calculate height and width of the pattern
        pat_h = int(round((y_peaks[-1] - y_peaks[0]) + avg_dy))
        pat_w = int(round((x_peaks[-1] - x_peaks[0]) + avg_dx))
        min_loc = (min_x, min_y)

        return (None, min_loc, pat_h, pat_w)

    # --- Original pattern-matching code below ---
    # Size of the given image.
    h, w = im.shape

    # Create the pattern of circles following the grid structure.
    rpix = int(h / nrow)  # Set random size of window that will later be scaled
    rspot = int((rpix * 0.5) / 2)  # Set random size of spot radius to scale
    # Create a pattern with the agar color and spots
    pattern = np.ones((nrow * rpix, ncol * rpix), dtype=np.uint8) * color_agar
    for i, j in itertools.product(range(nrow), range(ncol)):
        cv2.circle(
            pattern,
            (j * rpix + int(rpix / 2), i * rpix + int(rpix / 2)),
            rspot,
            color_spot,
            -1,
        )

    # Check for structure between frac and 100% of the total image size.
    min_fraction, max_fraction = frac, 1.0

    # Check for structure using iterations by increasing 0.2% of the image
    iterations = int((max_fraction - min_fraction) * 100 / 0.2)
    found = None
    for fraction in tqdm(
        np.linspace(min_fraction, max_fraction, iterations),
        desc="Fitting grid pattern...",
    ):
        # Scale the pattern to the fraction of the given image.
        pat_w = int(w * fraction)
        pat_h = int(pat_w * nrow / ncol)
        # Fix bug that might appear in images with special proportions
        if pat_h > h:
            pat_h = int(h * fraction)
            pat_w = int(pat_h * ncol / nrow)
        pattern_scaled = cv2.resize(pattern, (pat_w, pat_h))
        # Match the scaled pattern with the image.
        res = cv2.matchTemplate(im, pattern_scaled, cv2.TM_SQDIFF_NORMED)
        # The function gives the map of squared difference, so optimal location
        # will be the one with minimum value.
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        # Store the info about the best scale where pattern fits the image.
        if found is None or min_val < found[0]:
            found = (min_val, min_loc, pat_h, pat_w)
    return found


def get_mask(original_mask, nrow, ncol, sensitivity=0.05):
    """Perform dilatation of the spots (and therefore reduction of the agar)."""
    # Calculate patch size x,y
    d_y = original_mask.shape[0] / nrow
    d_x = original_mask.shape[1] / ncol
    # Perform dilatation increasing the thickness by 5% of a patch size
    kernel = np.ones((int(d_y * sensitivity), int(d_x * sensitivity)), np.uint8)
    mymask = ~(cv2.dilate(~original_mask, kernel, iterations=1))
    return mymask


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
        logger.info("""Reference image not found. Calibration not performed.""")
        min_ref, max_ref = 0, 255
    return (min_ref, max_ref)


def show_grid_result(latest_image, min_loc, pat_h, pat_w, nrow, ncol, output_dir):
    """Create a new image showing the best grid match and the patches)."""
    to_show_grid = cv2.imread(latest_image)
    d_h = int(pat_h / nrow)
    d_w = int(pat_w / ncol)
    for i in range(nrow + 1):
        for j in range(ncol + 1):
            cv2.line(
                to_show_grid,
                (min_loc[0] + d_w * j, min_loc[1]),
                (min_loc[0] + d_w * j, min_loc[1] + d_h * (nrow)),
                (255, 0, 0),
                5,
            )
        cv2.line(
            to_show_grid,
            (min_loc[0], min_loc[1] + d_h * i),
            (min_loc[0] + d_w * (ncol), min_loc[1] + d_h * i),
            (255, 0, 0),
            5,
        )
    cv2.imwrite(os.path.join(output_dir, "Output_Images", "Grid_QC.png"), to_show_grid)
