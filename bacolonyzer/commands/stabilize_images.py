"""Definition of all commands available in BaColonyzer."""
import logging
import os

import cv2
import numpy as np
from tqdm import tqdm

from bacolonyzer import analysis, filesystem, utils
from bacolonyzer.commands import abstract

logger = logging.getLogger(__name__)


class StabilizeImagesCommand(abstract.AbstractCommand):

    _SUBCOMMAND = 'stabilize_images'
    _DESCRIPTION = """\
    Rotate and adjust images in order to stabilize any movements that might
    occur during the experiment. A new folder is created with the new images.
    """

    def register_arguments(self, parser):
        parser.add_argument(
            "-d",
            "--directory",
            type=str,
            help="""Directory in which to search for image files that need to be
            stabilized.
            Default: current directory.""",
            default=".")
        parser.add_argument(
            "-o",
            "--output_directory",
            type=str,
            help="""New directory where the modified images will be stored.
            If directory does not exist, it will be created. If it exists,
            images will be overwritten.
            Default: ./corrected_images.""",
            default="./corrected_images/")
        parser.add_argument(
            "-q",
            "--quiet",
            help="""Suppresses messages printed during the analysis.
            Default: show messages.""",
            action="store_true")

    def run(self, args):
        # Setup logger
        if args.quiet:
            logging.basicConfig(format="%(message)s", level=logging.INFO)
        else:
            logging.basicConfig(format="%(message)s", level=logging.DEBUG)

        if not os.path.exists(args.output_directory):
            os.mkdir(args.output_directory)

        input_directory = filesystem.get_directory(args.directory)
        output_directory = filesystem.get_directory(args.output_directory)

        # Input and output image paths. Read from inputs and write to outputs.
        input_images_paths = filesystem.get_all_images(input_directory)
        output_images_paths = [
            os.path.join(args.output_directory, os.path.basename(p))
            for p in input_images_paths
        ]

        # Load first frame to use as first reference and save it as it is.
        prev, prev_gray = load_image_color_gray(input_images_paths[0])
        cv2.imwrite(output_images_paths[0], prev)

        # Get image sizes
        h, w, _ = prev.shape

        # Initial Affine Transformation matrix.
        M = np.eye(2, 3, dtype=np.float32)

        # Method for stabilization:
        logger.debug('Starting stabilizing images.')

        for input_img_path, output_img_path in tqdm(
                zip(input_images_paths[1:], output_images_paths[1:])):

            # Compute previous image features.
            prev_pts = cv2.goodFeaturesToTrack(prev_gray,
                                               maxCorners=400,
                                               qualityLevel=0.001,
                                               minDistance=20,
                                               blockSize=5,
                                               useHarrisDetector=True)
            # Upload new image at each step
            curr, curr_gray = load_image_color_gray(input_img_path)

            # Calculate optical flow (i.e. track feature points)
            curr_pts, status, err = cv2.calcOpticalFlowPyrLK(
                prev_gray, curr_gray, prev_pts, None)

            # Sanity check
            assert prev_pts.shape == curr_pts.shape

            # Filter only valid points
            idx = np.where(status == 1)[0]
            prev_pts = prev_pts[idx]
            curr_pts = curr_pts[idx]

            # Estimate the transformation that is needed
            M_iter, _ = cv2.estimateAffinePartial2D(prev_pts, curr_pts)
            # Update global Affine transformation matrix
            M[:2, :2] = np.dot(M[:2, :2], M_iter[:2, :2])
            M[:, 2:] += M_iter[:, 2:]

            # Stabilize image
            img_stabilized = cv2.warpAffine(curr,
                                            M, (w, h),
                                            flags=cv2.WARP_INVERSE_MAP)

            # Write stabilized image to new folder and update img to consider
            cv2.imwrite(output_img_path, img_stabilized)
            prev_gray = curr_gray

        logger.debug('Finished stabilizing images.')


def load_image_color_gray(img_path):
    """Read an original image of the time-series as well as the
    black-and-white version of this image.
    """
    img_color = cv2.imread(img_path, cv2.IMREAD_COLOR)
    img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
    return img_color, img_gray
