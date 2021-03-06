
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
import xml.etree.ElementTree as ET
import cv2
from shapely.geometry import Polygon, LineString, Point 

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

    parser.add_argument('-ip', '--input_dir', type=str,
                        help=('The directory with the set of images'))
    parser.add_argument('-op', '--output_dir', type=str, default='./',
                        help=('The output directory'))

    # Returns the passed in directory
    return parser.parse_args()

def main():
    """
    Main function. Searches all of the folders within the specified directory 
    for atmospherically corrected reflectance .tif images and their associated 
    .xml files. Calls args_parser to see what directory was specified.
    Parameters:
    None
    Return:
    None
    """
    # Finds the current directory and appends a new folder to be made
    args = args_parser()
    working_dir = args.input_dir
    output_dir = args.output_dir

    # Initialize a variable to save the name of the .xml file.
    # Initialize a variable to count the number of .xml files.
    xml_file = ''
    xml_count = 0

    # Initialize a list to hold all of the corrected .tif images.
    # Initialize a varaible to count the number of corrected .tif files
    class_ready_files = []
    class_ready_count = 0

    # Stores the subfolder directory
    # folder_dir = os.path.join(working_dir, folder)
    folder_dir = working_dir

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
                
                tree = ET.parse(os.path.join(working_dir, xml_file))
                root = tree.getroot()
                
                src = rasterio.open(os.path.join(working_dir, f2))
                # print(src.size)
                meta = src.meta
                # Update meta to float64
                meta.update({"driver": "GTiff",
                                "count": 1,
                                "dtype": "float32",
                                "bigtiff": "YES",
                                "nodata": 255})
                
                # collect image metadata
                bands = ['BAND_C', 'BAND_B', 'BAND_G', 'BAND_Y', 'BAND_R',
                            'BAND_RE', 'BAND_N', 'BAND_N2']
                rt = root[1][2].find('IMAGE')

                i = 0
                sum_bands = np.zeros((1,src.height,src.width),dtype=np.float32)

                for _ in bands:
                    # Read each layer and write it to stack
                    sum_bands = sum_bands + src.read(i + 1) 
                    i += 1

                dst = rasterio.open(os.path.join(output_dir,
                                    f2.replace('.tif', '_sumbands.tif')),
                                    'w', **meta)
                # dmeta = dst.meta
                #dst.meta.update({"count": "1"})
                dst.write(sum_bands)
                dst.close()
                # Prints that this specific parameter has been run
                print(f2 + ' has been processed.')
                
                # Classification of pixels by passing a condition
                # over the sum array and outputs a new array with
                # 1 values where true and 0 values where false
                meta.update({"dtype": "int32"})
                snow_and_ice = np.int32(np.where(sum_bands >= 3, 1, 0))
                #print(snow_and_ice)
                dst = rasterio.open(os.path.join(output_dir,
                                                    f2.replace('.tif', '_class_snow.tif')),
                                                    'w', **meta)
                dst.write(snow_and_ice)
                dst.close()

                shadow_and_water = np.int32(np.where((sum_bands > 0) & (sum_bands <= 1), 1, 0))
                #print(shadow_and_water)
                dst = rasterio.open(os.path.join(output_dir,
                                                    f2.replace('.tif', '_class_water.tif')),
                                                    'w', **meta)
                dst.write(shadow_and_water)
                dst.close()
                
                geology = np.int32(np.where((sum_bands > 1) & (sum_bands < 3), 1, 0))
                #or, geology = np.where((snow_and_ice == 0) & (shadow_and_water == 0), 1, 0)

                #print(geology)
                dst = rasterio.open(os.path.join(output_dir,
                                                    f2.replace('.tif', '_class_geology.tif')),
                                                    'w', **meta)
                dst.write(geology)
                dst.close()


    # If there are no .xml files, print out a message saying so
    elif xml_count == 0:
        print('There are no .xml files in ' + working_dir + '!')
    # If there are no raw .tif files to be analyzed, print out a message
    # saying so
    elif class_ready_count == 0:
        print('There are no corrected .tif images in ' + working_dir + '!')
    
# If the script was directly called, start it
if __name__ == '__main__':
    main()
