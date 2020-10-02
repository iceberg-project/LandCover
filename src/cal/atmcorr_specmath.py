"""
Authors: Brian Szutu
Emails: bs886@nau.edu
License: Northern Arizona University
Copyright: 2018-2019

This script performs band math on each rad.tif image using the outputted
average atmospheric correction values in the .txt outputted by atmcorr_regr.py.
The band math is as follows:
s1 - s2.
s1 is the band data at a certain band between bands 1 and 7, inclusive.
s2 is the corresponding average atmospheric correction value for that
specific band.

The spectral-mathed image will be outputted in the same folder as the
radiance image.

The script should be called from console and the inputted directory should
contain the images, relevent .xml, etc that need to be processed
"""

from glob import glob

import os
import argparse
import xml.etree.ElementTree as ET
import numpy as np
import rasterio


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
    parser.add_argument('-ip', '--input_dir', type=str, default='./',
                        help=('The directory with the set of images'))
    parser.add_argument('-op', '--output_dir', type=str, default='./',
                        help=('The output directory'))
    parser.add_argument('-t', '--atm_temp', type=str, default='',
                        help=('The path to the atmospheric correction lookup table'))

    # Returns the passed in directory
    return parser.parse_args()


def avgs_finder(atmotxt_dir, missing_txt):
    """
    Finds the average atmospheric correction values for bands 1 to 7.
    Returns them as a list. Will return the temporary spectra values
    if the atmcorr_regr.py output file is missing.

    Parameters:
    atmotxt_dir - the directory of the .txt file with the average
                  atmospheric correction values
    missing_txt - a boolean. True if the directory is missing the
                  atmcorr_regr.py output file, False otherwise

    Return:
    A list containing the average atmospheric correction values of
    bands 1 through 7
    """

    # Initializes an empty list to store the average correction
    # values
    averages = []

    if not missing_txt:
        # Opens the .txt document 
        with open(atmotxt_dir, 'r') as atmo_txt:
            # Stores each line as its own list inside a larger list
            # Splitting is done due to the formatting in the file
            text = [line.strip().replace("\n", "").split(": ")
                    for line in atmo_txt]
        # Closes the file
        atmo_txt.close()
    else:
        # Opens the .txt document 
        with open(atmotxt_dir, 'r') as atmo_txt:
            # Stores each line as its own list inside a larger list
            # Splitting is done due to the formatting in the file
            text = [line.strip().replace("\n", "").split()
                    for line in atmo_txt]
        # Closes the file
        atmo_txt.close()

    # Sets a counter variable for reading the last lines.
    n = -7

    # Variable specifies the last line to be read. The atmcorr_temp.txt
    # file contains band 8, which is considered to equal 0. The output
    # of atmcorr_regr.py doesn't have this band.
    last_line = -1
    if missing_txt:
        # Doesn't include the temporary text file's last line
        last_line = -2
        # Sets the counter variable to account for the extra line
        n = -8
    
    # while loop goes through the last seven lines of the saved
    # .txt file
    while n <= last_line:
        # Appends the averages to the initialized averages list
        # Row n, column 1 due to the splitting from earlier
        averages.append(float(text[n][1]))
        
        # Adds 1 to the counter
        n += 1

    return averages


def spec_mather(rad_dir, averages):
    """
    Does the spectral band math to the image. A new image is created
    as a result, with its name being the name of the rad.tif image but
    with _specmath after rad. The band math is as follows:
    s1 - s2.
    s1 is the band data of one of the bands of the original rad.tif image
    while s2 is the corresponding average band atmospheric correction value

    Parameters:
    rad_dir    - the directory of the rad.tif image
    averages   - a list holding the average atmospheric correction values of
                 bands 1 through 7
    """

    # Opens the rad.tif image
    src = rasterio.open(rad_dir)

    # Gets the metadata of the image
    meta = src.meta

    # Creates the specmath.tif image to be written onto
    with rasterio.open(rad_dir.replace('.tif', '_atmcorr.tif'),
                       'w', **meta) as dst:
        # for bands 1 through 7...
        for i in range(7):
            # Calculate the band-mathed value
            spec = np.float32(src.read(i + 1) - averages[i])
            # and write it into the new image
            dst.write_band(i + 1, spec)
            
        dst.write_band(8, np.float32(src.read(8)))

    # Close the file
    dst.close


def main():
    """
    The main function. Calls the other functions.

    Paramters:
    None

    Return:
    None
    """

    # Saves the specified directory to a variable
    args = args_parser()
    path = os.path.realpath(__file__)
    def_atmcorr = '/'.join([x for x in  path.split('/')[:-2]]) + \
                  '/lib/atmcorr_temp.txt'
    working_dir = args.input_dir
    output_dir = args.output_dir
    avg_txt = args.atm_temp
    # Initialize variables to hold the atmcorr_regr.py output .txt and
    # the rad.tif image.
    # xml_file saves the name of the .xml file associated with the raw image

    image_files = glob(os.path.join(working_dir + '*_rad.tif'))


    # For each file in the folder...
    for image_file in image_files:
        # if the file is a rad.tif image that doesn't contain
        # P1BS, save it
        
        if ('P1BS') not in image_file:
            rad_file = image_file
        else:
            continue
    # Checks to see if the specmath.tif image exists
        specmath_file_exists = os.path.isfile(os.path.join(working_dir,
                                    rad_file.replace('.tif', '_atmcorr.tif')))

    # If the specmath.tif image doesn't exist, create it
        if not specmath_file_exists and avg_txt != '':
            # Saves the directory of the atmcorr_regr.py file
            # atmotxt_dir = os.path.join(working_dir, file_name + '.txt')
            # Calls avgs_finder to retrieve the averages from the file
            averages = avgs_finder(avg_txt, False)
            # Saves the directory of the rad.tif image
            rad_dir = os.path.join(output_dir, rad_file)
            # Calls spec_mather to do the band math and write
            # it to the new file
            spec_mather(rad_dir, averages)

            print(rad_file + ' has been processed!')

        elif specmath_file_exists:
            print(rad_file.replace('.tif', '_atmcorr.tif') + ' already exists!')

        # If the output text file from atmcorr_regr.py doesn't exist in the
        # specified directory, use the values in atmcorr_temp.txt in lib
        # instead
        elif avg_txt == '':
            print('atmcorr_regr.py has not been run yet in the directory or ' +
                    'its output file is missing. Using the temporary ' +
                    'spectra values...')
            # Uses the file containing the temporary spectra instead
            # atmotxt_temp = '../lib/atmcorr_temp.txt'
            # Calls avgs_finder to retrieve the averages from the file
            averages = avgs_finder(def_atmcorr, True)
            # Saves the directory of the rad.tif image
            rad_dir = os.path.join(output_dir, rad_file)
            # Calls spec_mather to do the band math and write
            # it to the new file
            spec_mather(rad_dir, averages)


if __name__ == '__main__':
    main()

