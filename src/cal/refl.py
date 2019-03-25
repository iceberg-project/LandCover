import xml.etree.ElementTree as ET
import rasterio
import numpy as np
import math
import os

# Imports the Earth-Sun distances in AU by date.
from earth_sun_dist import date_distance

# Prints the directory the script is in
print("Current directory: " + os.path.dirname(os.path.abspath(__file__)))

# Finds the current directory and appends a new folder to be made
working_dir = input("Please input the FULL path to the directory with the images: \n")

# Will keep asking the user to input a valid path. Use CTRL + C to manually terminate
# the program
while (not os.path.exists(working_dir)):
    working_dir = input("That path does not exist. Please input a path: \n")

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

for folder in folders:
    xml_file = ''
    xml_count = 0

    atmcorr_files = []
    atmcorr_count = 0

    folder_dir = os.path.join(working_dir, folder)

    for file in os.listdir(folder_dir):
        if file.endswith('.xml'):
            xml_file = file
            xml_count += 1
        elif file.endswith('atmcorr.tif'):
            atmcorr_files.append(file)
            atmcorr_count += 1
        else:
            continue

    output_dir = os.path.join(folder_dir, 'Output Files')
    if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    if xml_count!= 0 and atmcorr_count != 0:
        for f2 in atmcorr_files:
            refl_file_exists = os.path.isfile(os.path.join(output_dir, f2+'_atmcorr_refl.tif'))

            if not refl_file_exists:
#///////////
                date = folder[2:7]

                d = date_distance[date]

                tree=ET.parse(os.path.join(working_dir, folder, xml_file))
                root = tree.getroot()

                # collect image metadata
                bands = ['BAND_C','BAND_B','BAND_G','BAND_Y','BAND_R','BAND_RE','BAND_N','BAND_N2']
                rt = root[1][2].find('IMAGE')
                satid = rt.find('SATID').text
                meansunel = rt.find('MEANSUNEL').text

                if satid == 'WV02':
                    esun = [1758.2229,1974.2416,1856.4104,1738.4791,1559.4555,1342.0695,1069.7302,861.2866] # WV02
                if satid == 'WV03':
                    esun = [1803.9109,1982.4485,1857.1232,1746.5947,1556.9730,1340.6822,1072.5267,871.1058] # WV03

                src = rasterio.open(os.path.join(working_dir, folder, f2))
                meta = src.meta
                # Update meta to float64
                meta.update(dtype = rasterio.float64)
                with rasterio.open(os.path.join(output_dir, f2+'_refl.tif', 'w', **meta)) as dst:
                    i = 0
                    for band in bands:
                        rt = root[1][2].find(band)
                        # collect band metadata
                        abscalfactor = float(rt.find('ABSCALFACTOR').text)
                        effbandwidth = float(rt.find('EFFECTIVEBANDWIDTH').text)
                        print(bands[i])
                        print(src.read(i+1)[0,0]," ",abscalfactor," ",effbandwidth)
                        ### Read each layer and write it to stack
                        rad = src.read(i+1)*pi*(d^2)/(esun[i]*sin(meansunel))
                        print(rad[0,0],rad.dtype)
                        dst.write_band(i+1, rad)
                        i += 1

