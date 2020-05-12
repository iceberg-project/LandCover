# Authors: Brad Spitzbart, Brian Szutu
# Emails: bradley.spitzbart@stonybrook.edu, bs886@nau.edu
# License: Stony Brook University, Northern Arizona University
# Copyright: 2018-2019

# This script is a more generalized version of Brad Spitzbart's raw to radiance script.
# It searches through the console specified directory for raw .tif images and their
# corresponding .xml files. If no .tif or .xml files exist in a folder,
# the script will not run.

# The radiance image will be outputted in the same folder as the original raw image.

# Imports the necessary packages. Rasterio is used to access the band data in .tif files
# ET is used to access the contents of .xml files.
import xml.etree.ElementTree as ET
import rasterio
import numpy as np
import math
import os
import argparse


def args_parser():
    # Reads in the image directory from the console

    # Parameters:
    # None
    
    # Return:
    # Returns the specified directory as a string

    # Creates an object to take in the directory
    parser = argparse.ArgumentParser(description='Takes in a console-inputted directory ' +
                                     'containing the set of raw images')

    # Attaches the passed in directory to the variable input_dir and sets it as a string
    parser.add_argument('-ip', '--input_dir', type=str, help=('The directory ' +
                                       'with the set of images'))

    # Returns the directory
    return parser.parse_args().input_dir

def main():
    # Main function. Searches all of the folders within the specified directory for
    # raw .tif images and their associated .xml files. Calls args_parser to
    # see what directory was specified.

    # Parameters:
    # None

    # Return:
    # None

    # Saves the specified directory to a variable
    working_dir = args_parser()

    # Initializes an empty list for the directory of image files
    folders = [working_dir]

    # #uncomment this block if images are in subfolders:
    # #folders = [working_dir] to folders = []
    # #searches through subdirectories of input directory
    
    # # for each file/folder in the specified directory...
    # for file in os.listdir(working_dir):
        # # if there is a . or the file is named Output Files...
        # if "." in file or file == 'Output Files':
            # # ...don't do anything
            # continue
        # # else, append the file to the folders list
        # else:
            # folders.append(file)

    # for each folder in the folders list...
    for folder in folders:
        # Initialize a variable to save the name of the .xml file.
        # Initialize a variable to count the number of .xml files.
        xml_file = ''; xml_count = 0

        # Initialize a list to hold all of the raw .tif images.
        # Initialize a varaible to count the number of .tif files
        tif_files = []; tif_count = 0


        ##uncomment this block if images are in subfolders:
        ##folder_dir = working_dir
        ##searches through subdirectories of input directory
        
        ## Saves the directory of the folder
        #folder_dir = os.path.join(working_dir, folder)

        folder_dir = working_dir

        # for each file inside of the folder...
        for file in os.listdir(folder_dir):
            # if the image is a raw image...
            if (file.endswith('.tif') and ('rad' not in file)
                and ('atmcorr' not in file) 
                and ('refl' not in file)
                and ('P1BS' not in file)):
                # ...append it to the list of raw images
                tif_files.append(file)
                # ...and add 1 to the .tif count
                tif_count += 1
            # if the file is a .xml file...
            elif file.endswith('.xml') and ('P1BS' not in file):
                # ...save the file to be used
                xml_file = file
                # ...and add 1 to the .xml count
                xml_count += 1
            else:
                continue
    
        # If there are .xml and .tif files...
        if xml_count != 0 and tif_count != 0:
            # for each .tif file in the folder...
            for f in tif_files:
                # Sees if an output file for the raw image being analyzed exists...
                rad_file_exists = os.path.isfile(os.path.join(folder_dir, f.replace('.tif', '_rad.tif')))

                # If the radiance image doesn't exist, use Spitzbart's script to make one
                if not rad_file_exists:
                    tree=ET.parse(os.path.join(folder_dir, xml_file))
                    root = tree.getroot()

                    # collect image metadata
                    bands = ['BAND_C','BAND_B','BAND_G','BAND_Y','BAND_R','BAND_RE','BAND_N','BAND_N2']

                    src = rasterio.open(os.path.join(folder_dir, f))
                    meta = src.meta
                    rt = root[1][2].find('IMAGE')
                    satid = rt.find('SATID').text
                    
                    # gain correction values
                    if satid == 'WV02':
                        gain = [1.151,0.988,0.936,0.949,0.952,0.974,0.961,1.002] # WV02
                    if satid == 'WV03':
                        gain = [0.905,0.940,0.938,0.962,0.964,1.000,0.961,0.978] # WV03
                    
                    #offset correction values
                    if satid == 'WV02':
                        offset = [-7.478,-5.736,-3.546,-3.564,-2.512,-4.120,-3.300,-2.891] # WV02
                    if satid == 'WV03':
                        offset = [-8.604,-5.809,-4.996,-3.649,-3.021,-4.521,-5.522,-2.992] # WV03
                    
                    # Update meta to float64
                    meta.update({"driver": "GTiff",
                        "compress": "LZW",
                        "count": "8",
                        "dtype": "float32",
                        "bigtiff": "YES",
                        "nodata": 255})

                    # Creates the rad.tif file to be written into
                    with rasterio.open(os.path.join(folder_dir, f.replace('.tif', '_rad.tif')),
                                       'w', **meta) as dst:
                        i = 0

                        # The commented out print statements were a part of Spitzbart's
                        # script. If they are needed, they can be commented back in -Brian
                        for band in bands:
                            rt = root[1][2].find(band)
                            print(type(rt))
                            # collect band metadata
                            abscalfactor = np.float32(rt.find('ABSCALFACTOR').text)
                            effbandwidth = np.float32(rt.find('EFFECTIVEBANDWIDTH').text)

                            # print(bands[i])
                            # print(src.read(i+1)[0,0]," ",abscalfactor," ",effbandwidth)

                            ### Read each layer and write it to stack
                            rad = np.float32(gain[i])*src.read(i + 1)*(abscalfactor/effbandwidth)+np.float32(offset[i])
                            #print(rad[0,0],rad.dtype)
                            dst.write_band(i + 1, rad)
                            i += 1
                    dst.close()
                    print(f + ' has been processed.')

                # If the rad.tif file already exists, print out a message saying so
                elif rad_file_exists:
                    print(f.replace('.tif', '_rad.tif') + ' already exists!')
        # If there are no .xml files, print out a message saying so
        elif xml_count == 0:
            print('There are no .xml files in ' + folder + '!')
        # If there are no raw .tif files to be analyzed, print out a message saying so
        elif tif_count == 0:
            print('There are no raw .tif images in ' + folder + '!')
        else:
            continue

# If the script was directly called, run the script
if __name__ == '__main__':
    main()
