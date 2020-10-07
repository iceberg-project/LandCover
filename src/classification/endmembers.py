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
from matplotlib import pyplot as plt


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

def band_extractor(image_dir):
    """
    Extracts the band data from the image at the given file address.
    It then transforms the the 3D numpy array representing the
    band data into a 2D array so that the pysptools endmember
    finder can take the data. The 2D array is dimensioned pixel x band.

    Parameters:
    image_dir - the file address of the image

    Return:
    Returns the dimensions of the image with the band data. The band
    data is formatted as a 2D array, whose dimensions are pixel x band.
    """

    # Variables used to hold the band data and the image dimensions,
    # respectively
    band_data = []
    image_dim = 0

    # Opens the image
    src = rasterio.open(image_dir)

    # Gets and saves the dimensions of the image
    image_dim = src.read(1).shape
    
    # For each band (from bands 1 through 8)...
    for band in range(1, 9):
        # Save the band data in the array above
       band_data.append(src.read(band).ravel())

    # Closes the image
    src.close()

    # At this point, the data is now in a 2D array that looks like this:
    # [[1st pixel, 2nd pixel, 3rd pixel, ... nth pixel], \\1st band
    #  [1st pixel, 2nd pixel, 3rd pixel, ... nth pixel], \\2nd band
    #   ...
    # This was done by combining the rows together so that the first pixel
    # of the next row is right next to the last pixel of the current row

    # Turns the list into a numpy array
    band_data = np.array(band_data)

    # Swaps the rows and columns of the array. It is now pixel x band.
    band_data = band_data.transpose(1, 0)

    # Returns the band data and image dimensions
    return (band_data, image_dim)



def main():
    
    working_dir = args_parser()

    # working_dir = 'C:/Users/Brian/Documents/Salvatore Research/test_image'

    # A list that contains all of the "_class" .tif files
    class_files = []
    # Keeps track of the number of the "_class" files
    class_count = 0
    
    for file in os.listdir(working_dir):
        if (file.endswith('_class.tif')):
            class_files.append(file)
            class_count += 1
        else:
            continue

    if class_count != 0:
        # For each detected _class.tif image file...
        for image in class_files:
            endmember_exist = os.path.isfile(
                os.path.join(working_dir,
                             image.replace('.tif', '_endmember.tif')))

            if not endmember_exist:
                # The file address of the image
                image_dir = os.path.join(working_dir, image)
                (band_data, image_dim) = band_extractor(image_dir)
                

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

