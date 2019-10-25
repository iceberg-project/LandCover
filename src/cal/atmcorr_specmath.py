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
    parser.add_argument('-ip', '--input_dir', type=str,
                        help='The directory containing the images.')

    # Returns the passed in directory
    return parser.parse_args().input_dir


def avgs_finder(atmotxt_dir):
    """
    Finds the average atmospheric correction values for bands 1 to 7.
    Returns them as a list

    Parameters:
    atmotxt_dir - the directory of the .txt file with the average
                  atmospheric correction values

    Return:
    A list containing the average atmospheric correction values of
    bands 1 through 7
    """

    # Initializes an empty list to store the average correction
    # values
    averages = []

    # Opens the .txt document 
    with open(atmotxt_dir, 'r') as atmo_txt:
        # Stores each line as its own list inside a larger list
        # Splitting is done due to the formatting in the file
        text = [line.strip().replace("\n", "").split(": ")
                for line in atmo_txt]
    # Closes the file
    atmo_txt.close()

    # Sets a counter variable
    n = -7
    
    # while loop goes through the last seven lines of the saved
    # .txt file
    while n < 0:
        # Appends the averages to the initialized averages list
        # Row n, column 1 due to the splitting from earlier
        averages.append(float(text[n][1]))
        
        # Adds 1 to the counter
        n += 1

    return averages


def spec_mather(rad_dir, averages, folder_dir):
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
    folder_dir - the directory of the image's folder
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

    # Gets the working directory from the console input
    working_dir = args_parser()

    # Initializes an empty list to hold all of the relevant folders
    # in the specified directory
    # !!!NEW CHANGE!!!: Now puts the inputted directory into the folders list.
    # This makes it so the script searches for just images within
    # the inputted directory
    folders = [working_dir]

    """

    #UNCOMMENT THIS BLOCK AND REMOVE CHANGE:
    #folders = [working_dir] to folders = []
    #IN ORDER TO SEARCH THROUGH THE SUBDIRECTORIES OF THE INPUTTED
    #DIRECTORY
    
    # for each file in the specified directory...
    for file in os.listdir(working_dir):
        # if the file is NOT a folder
        if "." in file:
            continue
        # if the file is a folder...
        else:
            # append it to the folders list
            folders.append(file)
    """

    # for each folder in the folders list...
    for folder in folders:
        # Initialize variables to hold the atmcorr_regr.py output .txt and
        # the rad.tif image.
        # xml_file saves the name of the .xml file associated with the raw image
        avg_txt = ''
        rad_file = ''
        xml_file = ''

        # Saves the directory of the folder
        folder_dir = os.path.join(working_dir, folder)

        # Looks for an xml file in the image folder
        for file in os.listdir(folder_dir):
            if file.endswith('.xml'):
                xml_file = file

        # Placeholder atmcorr_regr.py file output name if there was no
        # xml file when it was run
        file_name = 'NO_XML_PRESENT'

        # If there is an xml file, then the atmcorr_regry.py file has
        # a specific name, which was determined by the source image
        # name in the xml
        if xml_file != '':
            # Look into the xml for a branch called SOURCE_IMAGE
            tree = ET.parse(os.path.join(folder_dir, xml_file))
            root = tree.getroot()
            rt = root[1].find('SOURCE_IMAGE').text

            # And lop off some stuff for the atmcorr_regr.py output name
            file_name = rt[5:19]

        # For each file in the folder...
        for file in os.listdir(folder_dir):
            # if the file is a rad.tif image that doesn't contain
            # P1BS, save it
            if file.endswith('rad.tif') and ('P1BS') not in file:
                rad_file = file
            # if the file is the output .txt from atmcorr_regr.py,
            # save it
            elif file == file_name + '.txt':
                avg_txt = file
            # else continue
            else:
                continue
        # Checks to see if the specmath.tif image exists
        specmath_file_exists = os.path.isfile(os.path.join(folder_dir,
                                                           rad_file.replace('.tif', '_atmcorr.tif')))

        # If the specmath.tif image doesn't exist, create it
        if not specmath_file_exists and avg_txt != '':
            # Saves the directory of the atmcorr_regr.py file
            atmotxt_dir = os.path.join(folder_dir, file_name + '.txt')
            # Calls avgs_finder to retrieve the averages from the file
            averages = avgs_finder(atmotxt_dir)
            # Saves the directory of the rad.tif image
            rad_dir = os.path.join(folder_dir, rad_file)
            # Calls spec_mather to do the band math and write
            # it to the new file
            spec_mather(rad_dir, averages, folder_dir)

            print(rad_file + ' has been processed!')

        elif specmath_file_exists:
            print(rad_file.replace('.tif', '_atmcorr.tif') + ' already exists!')
            
        elif avg_txt == '':
            print('atmcorr_regr.py has not been run yet in the directory.')

        elif rad_file == '':
            print('There are no radiance images in ' +
                  folder_dir + '!')

            
if __name__ == '__main__':
    main()
