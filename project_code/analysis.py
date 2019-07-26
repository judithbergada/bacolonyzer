"""Functions to compute the outputs that will be saved.
"""

import numpy as np
import pandas


def measure_outputs(im, mask, pat_h, pat_w, nrow, ncol, FILE, spots,
                   correction):
    '''
    Add intensity measures and other measurements to a final dictionary.
    This dictionary will be outputed as a data-frame.
    '''
    # Outputs will be saved in a dictionary with the following features
    outputs_dict = {}
    allrows, allcols, allintensities, allareas = [], [], [], []
    allcolonymeans, allcolonyvariance, allbackgroundmeans = [], [], []

    # Extract the windows for each spot. First get the window widht and heigh.
    d_x = int(pat_h / nrow)
    d_y = int(pat_w / ncol)

    # Maximum intensity that we can see in a grayscale image is 255
    intMax = 255

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
                colonyMean_patch = np.mean(spot_intensities / intMax)
                # Compute the variance of the intensity
                colonyVariance_patch = np.var(spot_intensities / intMax)
                # Compute all intensity values normalized by the size of window
                intens_patch = np.sum(spot_intensities) / (tile.size * intMax)
            else:  # If there aren't colonies in the window, intensities are 0
                colonyMean_patch = colonyVariance_patch = intens_patch = 0

            # Compute agar information (agar is the opposite to the mask)
            bkgrnd = tile[~spots_patch]

            # If there is background in the patch, compute mean of intensities
            if bkgrnd.size > 1:
                backgroundMean_patch = np.mean(bkgrnd / intMax)
            else:  # If there is no background in the patch, intensities are 0
                backgroundMean_patch = 0

            # Save all variables in the final lists
            allrows.append(i + 1)
            allcols.append(j + 1)
            allintensities.append(intens_patch)
            allareas.append(area_patch)
            allcolonymeans.append(colonyMean_patch)
            allcolonyvariance.append(colonyVariance_patch)
            allbackgroundmeans.append(backgroundMean_patch)

    # Save final outputs
    outputs_dict["Row"] = allrows
    outputs_dict["Column"] = allcols
    outputs_dict["Intensity"] = allintensities
    outputs_dict["Area"] = allareas
    outputs_dict["ColonyMean"] = allcolonymeans
    outputs_dict["ColonyVariance"] = allcolonyvariance
    outputs_dict["BackgroundMean"] = allbackgroundmeans
    fname = FILE.split(".")[0].split("/")[-1]
    outputs_dict["Barcode"] = [fname[0:15]] * len(allrows)
    outputs_dict["Filename"] = [fname] * len(allrows)
    # Convert dictionary to data frame
    outputs_df = pandas.DataFrame(outputs_dict)
    return outputs_df
