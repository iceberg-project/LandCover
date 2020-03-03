# -*- coding: utf-8 -*-

"""
Authors: Helen Eifert, Brad Spitzbart, Brian Szutu
Emails: he248@nau.edu, bradley.spitzbart@stonybrook.edu, bs886@nau.edu
License: Stony Brook University, Northern Arizona University
Copyright: 2018-2019
This script takes different band math parameter output files from the class.py 
script and converts them into shapefiles for mapping needs.
"""

# Imports the necessary packages. Rasterio is used to access the band data in .tif files
import rasterio
import numpy as np
import math
import os
import argparse
import xml.etree.ElementTree as ET
import geopandas as gpd
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
    folders = [working_dir]
    
     # for each folder in the specified directory...
    for folder in folders:
        # Initialize a list to hold all of the corrected .tif images.
        # Initialize a varaible to count the number of corrected .tif files
        shp_ready_files = []
        shp_ready_count = 0

        # Stores the subfolder directory
        # folder_dir = os.path.join(working_dir, folder)
        folder_dir = folder

        # for each file in the subfolder...
        for file in os.listdir(folder_dir):
            if file.endswith('class.tif') and ('P1BS' not in file):
                # append it to the list of corrected images...
                shp_ready_files.append(file)
                # and add 1 to the image count
                shp_ready_count += 1
            else:
                continue

        # A remnant of where the script saved the newly processed images.
        # Easier and safer to just set it equal to the new place to be saved
        # to.
        output_dir = folder_dir

        # If there was an xml and at least one corrected image detected...
        if shp_ready_count != 0:

            # for each detected corrected image...
            for f2 in class_ready_files:
                # Check to see if the image was already processed
                shp_file_exists = os.path.isfile(os.path.join(output_dir,
                                                  f2.replace('.tif',
                                                             '_shp.tif'))) 
                
                 # If it wasn't processed...
                if not shp_file_exists:
                    
                    src = rasterio.open(os.path.join(folder, f2))
                    # print(src.size)
                    meta = src.meta
                    # Update meta to float64
                    meta.update({"driver": "GTiff",
                                 "count": 1,
                                 "dtype": "float32",
                                 "bigtiff": "YES",
                                 "nodata": 255})

                    dst = rasterio.open(os.path.join(output_dir,
                                       f2.replace('.tif', '_class.tif')),
                                       'w', **meta)
                    # dmeta = dst.meta
                    #dst.meta.update({"count": "1"})

                    


                    # Converting arrays to shapefiles
                    classied_df = gpd.GeoDataFrame(crs=src.crs)
                    labels = ['snow_and_ice', 'shadow_and_water', 'geology']
                    for idx, mask in enumerate([snow_and_ice, shadow_and_water, geology]):
                        pols = polygonize_raster(mask, src.transform)
                        if pols:
                            classified_df = classied_df.append({'geometry': pols,
                                                                'label': labels[idx]}, 
                                                                ignore_index=True)
                    
                    classified_df.to_file('classified.shp')
                    dst.write(classified_df)
                    dst.close()
                    # Prints that parameter has been converted
                    print(f2 + ' has been processed.')
       
        # If there are no class .tif files to be analyzed, print out a message
        # saying so
        elif shp_ready_count == 0:
            print('There are no classified .tif images in ' + folder + '!')
        else:
            continue
    
# If the script was directly called, start it
if __name__ == '__main__':
    main()
