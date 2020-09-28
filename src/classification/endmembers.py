"""
Author: Brian Szutu
Email: bs886@nau.edu


This script is used to find the endmembers of each pixel of the WV2 .tif images
present within the user-specified directory/folder. There are two packages that
are used that need to be manually installed: rasterio and pysptools. rasterio
is used to access the band data within each WV2 .tif image and pysptools
is used as the endmember finder.

The output file is sent to the folder the used image resides in.

This script is safe to run multiple times in the same directory.
"""

import os
import argparse
import numpy as np
import rasterio
import pysptools.abundance_maps.amaps as amaps


def args_parser():
    """
    Reads the image directory passed in from console.
    Parameters:
    None
    Return:
    Returns a directory that has the images to be analyzed within it
    """

    # Creates an ArgumentParser object to hold the console input
    parser = argparse.ArgumentParser()
    
    # Adds an argument to the parser created above. Holds the
    # inputted directory as a string
    parser.add_argument('-ip', '--input_dir', type=str,
                        help='The directory containing the images.')

    # Returns the passed in directory
    return parser.parse_args().input_dir

def endmember_finder():

    return a

def band_extractor():

    return b



def main():
    
    working_dir = args_parser()

    # A list that contains all of the "_class" .tif files
    class_files = []
    # Keeps track of the number of the "_class" files
    class_count = 0
    
    for file in os.listdir(working_dir):
        if (file.endswith('_class.tif'):
            class_files.append(file)
            class_count += 1
        else:
            continue

    if class_count != 0:
        for image in class_files:
            endmember_exist = os.path.isfile(
                os.path.join(working_dir,
                             image.replace('.tif', '_endmember.tif')))

            if not endmember_exist:

                # Run endmember stuff

            else:
                continue

    """
    test = np.array([[4, 2, 4],
                    [3, 3, 3]])
    print(test.shape)
    end_test = np.array([[2, 1, 2],
                        [1, 2, 1]])

    abundance_test = amaps.NNLS(test, end_test)
    print(abundance_test)
    """

main()

