This repo contains code and development for the Land Cover use case, providing spatial coverage of surveyed area, reasonable estimates on atmospheric contributions, and comparisons to a spectral library of known geologic materials.

## Directory structure:
    -src
        -utils (containing setup instructions, xml reader etc.)
        -lib (earth-sun distance lookup table, etc)
        -cal (atmospheric correction and other calibration code)
        -classification (land cover classification code)
        -entk_scripts (Ensemble pipeline scripts)

    -validation_suite (code to check installation and testing results)

The following scripts are used to calibrate raw WorldView-2 and -3 satellite image data into reflectance

rad.py - convert raw digital number tif input to top-of-atmosphere radiance. Output images end with rad.tif <br>

atmcorr_regr.py - uses .txt files of manually collected spectra from an image to run dark object subtraction and regress
ions and creates an output file with band averages representative of the atmosphere <br>

atmcorr_specmath.py - uses the output file from atmcorr_regr.py to atmospherically correct radiance image. Output images
 end with rad_atmcorr.tif <br>

refl.py - convert either radiance tif input to top-of-atmosphere reflectance or atmospherically corrected radiance tif i
nput  to atmospherically corrected reflectance. Output images end with either rad_refl.tif or rad_atmcorr_refl.tif <br>

Each script requires the same single argument, -ip (or --input_dir), for the input directory.<br>
> python rad.py -ip /path/to/input/files

The following scripts are used to classify the reflectance into types of landcover

class.py - create class masks based on spectral properties

shp.py - convert the class masks to shapefiles

Dependancies:
# This file may be used to create an environment using:
# $ conda create --name <env> --file <this file>
# platform: linux-64
@EXPLICIT
https://conda.anaconda.org/conda-forge/linux-64/_libgcc_mutex-0.1-main.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/ca-certificates-2019.11.28-hecc5488_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/ld_impl_linux-64-2.33.1-h53a641e_7.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libgfortran-ng-7.3.0-hdf63c60_2.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libstdcxx-ng-9.2.0-hdf63c60_0.tar.bz2
https://conda.anaconda.org/conda-forge/noarch/poppler-data-0.4.9-1.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libgcc-ng-9.2.0-hdf63c60_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/tbb-2018.0.5-h2d50403_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/bzip2-1.0.8-h516909a_2.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/expat-2.2.5-he1b5a44_1004.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/freexl-1.0.5-h14c3975_1002.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/geos-3.8.0-he1b5a44_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/giflib-5.1.7-h516909a_1.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/gmp-6.1.2-hf484d3e_1000.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/graphite2-1.3.13-hf484d3e_1000.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/icu-64.2-he1b5a44_1.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/jpeg-9c-h14c3975_1001.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/json-c-0.13.1-h14c3975_1001.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/lame-3.100-h14c3975_1001.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libffi-3.2.1-he1b5a44_1006.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libiconv-1.15-h516909a_1005.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libllvm9-9.0.0-hc9558a2_3.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libopenblas-0.3.7-h5ec1e0e_5.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libspatialindex-1.9.3-he1b5a44_1.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libuuid-2.32.1-h14c3975_1000.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libxkbcommon-0.9.1-hebb1f50_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/lz4-c-1.8.3-he1b5a44_1001.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/ncurses-6.1-hf484d3e_1002.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/nettle-3.4.1-h1bed415_1002.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/nspr-4.24-he1b5a44_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/openssl-1.1.1d-h516909a_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/pcre-8.43-he1b5a44_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/pixman-0.38.0-h516909a_1003.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/pthread-stubs-0.4-h14c3975_1001.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/tzcode-2019a-h516909a_1002.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/x264-1!152.20180806-h14c3975_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/xorg-kbproto-1.0.7-h14c3975_1002.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/xorg-libice-1.0.10-h516909a_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/xorg-libxau-1.0.9-h14c3975_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/xorg-libxdmcp-1.1.3-h516909a_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/xorg-renderproto-0.11.1-h14c3975_1002.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/xorg-xextproto-7.3.0-h14c3975_1002.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/xorg-xproto-7.0.31-h14c3975_1007.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/xz-5.2.4-h14c3975_1001.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/zlib-1.2.11-h516909a_1006.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/boost-cpp-1.70.0-h8e57a91_2.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/gettext-0.19.8.1-hc5be6a0_1002.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/gnutls-3.6.5-hd3a4fd2_1002.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/hdf4-4.2.13-hf30be14_1003.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/hdf5-1.10.5-nompi_h3c11f04_1104.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/jasper-1.900.1-h07fcdf6_1006.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libblas-3.8.0-14_openblas.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libclang-9.0.0-default_hde54327_4.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libedit-3.1.20170329-hf8c457e_1001.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libpng-1.6.37-hed695b0_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libssh2-1.8.2-h22169c7_2.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libxcb-1.13-h14c3975_1002.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libxml2-2.9.10-hee79883_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/openh264-1.8.0-hdbcaa40_1000.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/readline-8.0-hf8c457e_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/tk-8.6.10-hed695b0_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/xerces-c-3.2.2-h8412b87_1004.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/xorg-libsm-1.2.3-h84519dc_1000.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/zstd-1.4.4-h3b9ef0a_1.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/freetype-2.10.0-he983fc9_1.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/kealib-1.4.10-h58c409b_1005.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/krb5-1.16.4-h2fd8d38_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libcblas-3.8.0-14_openblas.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libkml-1.3.0-h4fcabce_1010.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/liblapack-3.8.0-14_openblas.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libtiff-4.1.0-hc3755c2_1.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/sqlite-3.30.1-hcee41ef_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/xorg-libx11-1.6.9-h516909a_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/ffmpeg-4.1.3-h167e202_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/fontconfig-2.13.1-h86ecdb6_1001.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libcurl-7.65.3-hda55be3_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/liblapacke-3.8.0-14_openblas.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libpq-11.5-hd9ab2ff_2.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libwebp-1.0.2-hf4e8a37_4.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/nss-3.47-he751ad9_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/openjpeg-2.3.1-h981e76c_3.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/proj-6.2.1-hc80f0dc_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/python-3.8.0-h357f687_5.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/xorg-libxext-1.3.4-h516909a_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/xorg-libxrender-0.9.10-h516909a_1002.tar.bz2
https://conda.anaconda.org/conda-forge/noarch/affine-2.3.0-py_0.tar.bz2
https://conda.anaconda.org/conda-forge/noarch/attrs-19.3.0-py_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/certifi-2019.11.28-py38_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/cfitsio-3.470-hb60a0a2_2.tar.bz2
https://conda.anaconda.org/conda-forge/noarch/click-7.0-py_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/curl-7.65.3-hf8cf82a_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/geotiff-1.5.1-hbd99317_7.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/glib-2.58.3-py38h6f030ca_1002.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libspatialite-4.3.0a-h343d7df_1033.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/numpy-1.17.3-py38h95a1406_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/postgresql-11.5-hc63931a_2.tar.bz2
https://conda.anaconda.org/conda-forge/noarch/pyparsing-2.4.5-py_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/pyproj-2.4.2.post1-py38h12732c1_0.tar.bz2
https://conda.anaconda.org/conda-forge/noarch/pytz-2019.3-py_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/rtree-0.9.3-py38h7b0cdae_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/six-1.13.0-py38_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/cairo-1.16.0-hfb77d84_1002.tar.bz2
https://conda.anaconda.org/conda-forge/noarch/click-plugins-1.1.1-py_0.tar.bz2
https://conda.anaconda.org/conda-forge/noarch/cligj-0.5.0-py_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/dbus-1.13.6-he372182_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/gstreamer-1.14.5-h36ae1b5_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libdap4-3.20.4-hd3bb157_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libnetcdf-4.7.1-nompi_h94020b1_102.tar.bz2
https://conda.anaconda.org/conda-forge/noarch/python-dateutil-2.8.1-py_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/setuptools-42.0.2-py38_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/shapely-1.6.4-py38h5d51c17_1007.tar.bz2
https://conda.anaconda.org/conda-forge/noarch/snuggs-1.4.7-py_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/tiledb-1.7.0-hcde45ca_2.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/gst-plugins-base-1.14.5-h0935bb2_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/harfbuzz-2.4.0-h9f30f68_3.tar.bz2
https://conda.anaconda.org/conda-forge/noarch/munch-2.5.0-py_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/pandas-0.25.3-py38hb3f55d8_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/poppler-0.67.0-h14e79db_8.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/wheel-0.33.6-py38_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libgdal-3.0.2-h30a29e3_5.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/pip-19.3.1-py38_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/qt-5.12.5-hd8c4c69_1.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/gdal-3.0.2-py38hbb6b9fb_5.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/libopencv-4.1.2-py38_2.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/rasterio-1.1.1-py38h900e953_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/fiona-1.8.13-py38h900e953_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/py-opencv-4.1.2-py38h5ca1d4c_2.tar.bz2
https://conda.anaconda.org/conda-forge/noarch/geopandas-0.6.2-py_0.tar.bz2
https://conda.anaconda.org/conda-forge/linux-64/opencv-4.1.2-py38_2.tar.bz2
