"""Functions to compute the outputs that will be saved.
"""

import numpy as np
import pandas


def measure_outputs(im, mask, pat_h, pat_w, nrow, ncol, file_name, spots,
                    correction):
    """Add intensity measures and other measurements to a final dictionary.
    This dictionary will be outputed as a data-frame.
    """
    # Outputs will be saved in a dictionary with the following features
    allrows, allcols, allintensities, allareas = [], [], [], []
    allcolonymeans, allcolonyvariance, allbackgroundmeans = [], [], []

    # Extract the windows for each spot. First get the window widht and heigh.
    d_x = int(pat_h / nrow)
    d_y = int(pat_w / ncol)

    # Maximum intensity that we can see in a grayscale image is 255
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
    # TODO(judithbergada): this could be improved by calling
    # os.path.basename().split('.')[0]. Is more elegant and reliable.
    # Also check the method os.path.splitext which makes the separation of the
    # file extension and the file name. Your way of handle it may find some
    # problems with names with more than one dot.
    fname = file_name.split(".")[0].split("/")[-1]
    return pandas.DataFrame({
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
