the following scripts are used to classify calibrated surface reflectance WorldView-2 and -3 satellite image data into land cover unit shape files.

class.py - Executes parameter on refl.tif image that sums all 8 bands and uses thresholds to classify each pixel as one of three simple land cover types (shadow & water; geology; snow & ice). Output end with class_[unit type].tif <br>

shp.py - Converts output classified images into binary masks and then converts each array into a polygon shapefile. Output files end with class_[unit type].shp <br>

Each script requires the same single argument, -ip (or --input_dir), for the input directory. <br>

> python class.py -ip /path/to/input/files

Additional packages needed:

-rasterio <br>
-xml.etree.ElementTree <br>
-argparse <br>
-os <br>
-numpy <br>
-geopandas <br>
-cv2 <br>
-re <br>
-shapely.geometry 