
"""
Authors: Helen Eifert, Brad Spitzbart, Brian Szutu
Emails: he248@nau.edu, bradley.spitzbart@stonybrook.edu, bs886@nau.edu
License: Stony Brook University, Northern Arizona University
Copyright: 2018-2019
This script runs a set of band math parameters to identify land cover types.
It searches through the console specified directory for refl.tif images. If no refl.tif images exist, the script will not run.
The output will an image-sized array of values relating to different landcover classes.
"""

# Imports the necessary packages. Rasterio is used to access the band data in .tif files
import rasterio
import numpy as np
import math
import os
import argparse

def args_parser():
    """
    Reads in the image directory from the console
    Parameters:
    None
    Return:
    Returns the specified directory as a string
    """

    # Creates an object to take in the directory
    parser = argparse.ArgumentParser(description='Takes in a console-inputted\
                                                  directory containing the set \
                                                  of raw images')

    # Attaches the passed in directory to the variable input_dir and sets it
    # as a string
    parser.add_argument('-ip', '--input_dir', type=str, help=('The directory \
                                                               with the set of \
                                                               images'))

    # Returns the directory
    return parser.parse_args().input_dir

def main():
    """
    Main function. Searches all of the folders within the specified directory 
    for atmospherically corrected .tif images and their associated .xml files.
    Calls args_parser to see what directory was specified.
    Parameters:
    None
    Return:
    None
    """

    # Finds the current directory and appends a new folder to be made
    working_dir = args_parser()

    # Empty list holds all of the relevent folders in the directory
    # !!!NEW CHANGE!!!: Now puts the inputted directory into the folders list.
    # This makes it so the script searches for just images within
    # the inputted directory
    folder = [working_dir]
    
     # for each folder in the specified directory...
    for file in folder:
        # Initialize a variable to save the name of the .xml file.
        # Initialize a variable to count the number of .xml files.
        xml_file = ''
        xml_count = 0

        # Initialize a list to hold all of the corrected .tif images.
        # Initialize a varaible to count the number of corrected .tif files
        class_ready_files = []
        class_ready_count = 0

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
            elif file.endswith('refl.tif') and ('P1BS' not in file):
                # append it to the list of corrected images...
                class_ready_files.append(file)
                # and add 1 to the image count
                class_ready_count += 1
            else:
                continue

        # A remnant of where the script saved the newly processed images.
        # Easier and safer to just set it equal to the new place to be saved
        # to.
        output_dir = folder_dir

        # If there was an xml and at least one corrected image detected...
        if xml_count != 0 and class_ready_count != 0:

            # for each detected corrected image...
            for f2 in class_ready_files:
                # Check to see if the image was already processed
                class_file_exists = os.path.isfile(os.path.join(output_dir,
                                                  f2.replace('.tif',
                                                             '_class.tif')))

                # If it wasn't processed...
                if not class_file_exists:
                    
                    tree = ET.parse(os.path.join(working_dir, folder, xml_file))
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
                    bands = ['BAND_C', 'BAND_B', 'BAND_G', 'BAND_Y', 'BAND_R',
                             'BAND_RE', 'BAND_N', 'BAND_N2']
                    rt = root[1][2].find('IMAGE')

                    i = 0
                    sum = 0

                    for _ in bands:
                        # Read each layer and write it to stack
                        sum = sum + src.read(i + 1) 
                        # print(refl[0,0],sum.dtype)
                        i += 1

                    dst = rasterio.open(os.path.join(output_dir,
                                       f2.replace('.tif', '_class.tif')),
                                       'w', **meta)
                    dst.write(sum)
                    dst.close()
                    # Prints that this specific parameter has been run
                    print(f2 + ' has been processed.')
                    
                    ## not sure if this is in the right spot or if it needs
                    ## to be within the for loop
                    ## also not sure if it is the right format
                    # set parameters with numpy where function
                    snow_and_ice = np.where(sum >= 3)
                    geology = np.where(1 < sum > 3)
                    shadow_and_water = np.where(sum <= 1)
                    
                    ## i imagine there is one more step to write these 
                    ## arrays into a new image, but i'm unsure how to 
                    ## best assign new values without canceling their
                    ## existing values
          
                # If the class.tif file already exists, print out a message
                # saying so
                elif class_file_exists:
                    print(f2.replace('.tif', '_class.tif') + ' already exists!')
        # If there are no .xml files, print out a message saying so
        elif xml_count == 0:
            print('There are no .xml files in ' + folder + '!')
        # If there are no raw .tif files to be analyzed, print out a message
        # saying so
        elif refl_ready_count == 0:
            print('There are no corrected .tif images in ' + folder + '!')
        else:
            continue
    
# If the script was directly called, start it
if __name__ == '__main__':
    main()
