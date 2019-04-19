"""
Authors: Brad Spitzbart, Brian Szutu
Emails: bradley.spitzbart@stonybrook.edu, bs886@nau.edu
License: Stony Brook University, Northern Arizona University
Copyright: 2018-2019

This script is a more generalized version of Brad Spitzbart's reflectance script.
It searches through the folders in the console specified directory for
atmospherically corrected .tif images and their corresponding .xml files.
If no .tif or .xml files exist in a folder, the script will not run
for that folder and will continue to the next folder.

The reflectance image will be outputted in the same folder as the
atmospherically corrected image.
"""

import xml.etree.ElementTree as ET
import rasterio
import numpy as np
import math
import os
import argparse

# Imports a dictionary containing the Earth-Sun distance in AU depending
# on the date
from earth_sun_dist import date_distance

def args_parser():
    """
    Reads in the image directory from the console

    Parameters:
    None
    
    Return:
    Returns the specified directory as a string
    """

    # Creates an object to take in the directory
    parser = argparse.ArgumentParser(description='Takes in a console-inputted directory ' +
                                     'containing the set of raw images')

    # Attaches the passed in directory to the variable input_dir and sets it as a string
    parser.add_argument('-ip', '--input_dir', type=str, help=('The directory ' +
                                       'with the set of images'))

    # Returns the directory
    return parser.parse_args().input_dir


def main():
    """
    Main function. Searches all of the folders within the specified directory for
    atmospherically corrected .tif images and their associated .xml files.
    Calls args_parser to see what directory was specified.

    Parameters:
    None

    Return:
    None
    """
    
    # Finds the current directory and appends a new folder to be made
    working_dir = args_parser()

    # Empty list holds all of the relevent folders in the directory
    folders = []

    # for each file/folder in the directory...
    for file in os.listdir(working_dir):
        # if there is a . or the something is named Output Files...
        if "." in file or file == 'Output Files':
            # ...Don't do anything with them
            continue
        else:
            # Else, append the thing being looked at into the folders list
            folders.append(file)

    # for each folder in the specified directory...
    for folder in folders:
        # Initialize a variable to save the name of the .xml file.
        # Initialize a variable to count the number of .xml files.
        xml_file = ''; xml_count = 0

        # Initialize a list to hold all of the corrected .tif images.
        # Initialize a varaible to count the number of corrected .tif files
        refl_ready_files = []; refl_ready_count = 0

        # Stores the subfolder directory
        folder_dir = os.path.join(working_dir, folder)

        # for each file in the subfolder...
        for file in os.listdir(folder_dir):
            # if the file is an .xml file and is NOT related to a P1BS image...
            if file.endswith('.xml') and ('P1BS' not in file):
                # save the name of the file...
                xml_file = file
                # and add 1 to the xml count
                xml_count += 1
            # if the file is a corrected image and is NOT a P1BS image...
            elif file.endswith('atmcorr.tif') and ('P1BS' not in file):
                # append it to the list of corrected images...
                refl_ready_files.append(file)
                # and add 1 to the image count
                refl_ready_count += 1
            else:
                continue

        # Rerunning the loop to check for rad.tif files...
        for file in os.listdir(folder_dir):
            # if there isn't an atmospherically corrected image...
            if (file.endswith('rad.tif') and ('P1BS' not in file)
                and file.replace('rad.tif', 'rad_atmcorr.tif') not in refl_ready_files):
                # use the radiance image to convert it to reflectance...
                refl_ready_files.append(file)
                # and add 1 to the image count
                refl_ready_count += 1
            else:
                continue

        # A remnant of where the script saved the newly processed images.
        # Easier and safer to just set it equal to the new place to be saved
        # to.
        output_dir = folder_dir

        # If there was an xml and at least one corrected image detected...
        if xml_count!= 0 and refl_ready_count != 0:

            # for each detected corrected image...
            for f2 in refl_ready_files:
                # Check to see if the image was already processed
                refl_file_exists = os.path.isfile(os.path.join(output_dir, f2.replace('.tif', '_refl.tif')))

                # If it wasn't processed...
                if not refl_file_exists:

                    # Finds the date of the image by looking at the folder name
                    date = folder[2:7]

                    # Finds the associated Earth-Sun distance in AU from the
                    # imported dictionary
                    d = date_distance[date]

                    tree=ET.parse(os.path.join(working_dir, folder, xml_file))
                    root = tree.getroot()
                    
                    src = rasterio.open(os.path.join(working_dir, folder, f2))
                    meta = src.meta
                    # Update meta to float64
                    meta.update({"driver": "GTiff",
                        "count": "8",
                        "dtype": "float32",
                        "bigtiff": "YES",
                        "nodata": 255})
                    
                    # collect image metadata
                    bands = ['BAND_C','BAND_B','BAND_G','BAND_Y','BAND_R','BAND_RE','BAND_N','BAND_N2']
                    rt = root[1][2].find('IMAGE')
                    satid = rt.find('SATID').text
                    meansunel = np.float32(rt.find('MEANSUNEL').text)
                    
                    if satid == 'WV02':
                        esun = [1758.2229,1974.2416,1856.4104,1738.4791,1559.4555,1342.0695,1069.7302,861.2866] # WV02
                    if satid == 'WV03':
                        esun = [1803.9109,1982.4485,1857.1232,1746.5947,1556.9730,1340.6822,1072.5267,871.1058] # WV03

                    with rasterio.open(os.path.join(output_dir, f2.replace('.tif', '_refl.tif')), 'w', **meta) as dst:
                        i = 0

                        # The commented out print statement was a part of Spitzbart's
                        # script. If it is needed, it can be commented back in -Brian
                        for band in bands:
                            ### Read each layer and write it to stack
                            refl = src.read(i+1)*math.pi*(d**2)/(esun[i]*math.degrees(math.sin(meansunel)))
                            # print(refl[0,0],refl.dtype)
                            dst.write_band(i+1, refl)
                            i += 1

                    dst.close()
                    # Prints that a certain image was successfully converted to reflectance
                    print(f2 + ' has been processed.')
                    
                        # If the refl.tif file already exists, print out a message saying so
                elif refl_file_exists:
                    print(f2.replace('.tif', '_refl.tif') + ' already exists!')
        # If there are no .xml files, print out a message saying so
        elif xml_count == 0:
            print('There are no .xml files in ' + folder + '!')
        # If there are no raw .tif files to be analyzed, print out a message saying so
        elif refl_ready_count == 0:
            print('There are no corrected .tif images in ' + folder + '!')
        else:
            continue

                    

# If the script was directly called, start it
if __name__ == '__main__':
    main()
