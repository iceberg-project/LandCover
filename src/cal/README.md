the following scripts are used to calibrate raw WorldView-2 and -3 satellite image data into reflectance 

rad.py - convert raw digital number tif input to top-of-atmosphere radiance. Output images end with rad.tif <br>

atmcorr_regr.py - uses .txt files of manually collected spectra from an image to run dark object subtraction and regressions and creates an output file with band averages representative of the atmosphere <br>

atmcorr_specmath.py - uses the output file from atmcorr_regr.py to atmospherically correct radiance image. If no files exist from atmocorr_regr.py, a reference spectrum, atmcorr_temp.txt, located in the lib directory is used. Output images end with rad_atmcorr.tif <br>

refl.py - convert either radiance tif input to top-of-atmosphere reflectance or atmospherically corrected radiance tif input  to atmospherically corrected reflectance. Output images end with either rad_refl.tif or rad_atmcorr_refl.tif <br>

Each script requires the same single argument, -ip (or --input_dir), for the input directory.<br>
> python rad.py -ip /path/to/input/files

Additional packages needed:
- rasterio
- xml.etree.ElementTree
- argparse
- os
- numpy
- math
- sys
- scipy stats
