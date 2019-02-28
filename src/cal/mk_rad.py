import xml.etree.ElementTree as ET
import rasterio
import numpy as np
import math

tree=ET.parse('orthoWV02_13NOV131639373-M1BS-1030010029192A00_u16ns3031.xml')
root = tree.getroot()

# collect image metadata
bands = ['BAND_C','BAND_B','BAND_G','BAND_Y','BAND_R','BAND_RE','BAND_N','BAND_N2']

src = rasterio.open('In/orthoWV02_13NOV131639373-M1BS-1030010029192A00_u16ns3031.tif')
meta = src.meta
# Update meta to float64
meta.update({"driver": "GTiff",
             "compress": "LZW",
             "count": "8",
             "dtype": "float64",
             "bigtiff": "YES",
             "nodata": 255})

with rasterio.open('orthoWV02_13NOV131639373-M1BS-1030010029192A00_u16ns3031_rad.tif', 'w', **meta) as dst:
  i = 0
  for band in bands:
    rt = root[1][2].find(band)
    # collect band metadata
    abscalfactor = float(rt.find('ABSCALFACTOR').text)
    effbandwidth = float(rt.find('EFFECTIVEBANDWIDTH').text)
    print(bands[i])
    print(src.read(i+1)[0,0]," ",abscalfactor," ",effbandwidth)
    ### Read each layer and write it to stack
    rad = src.read(i+1)*abscalfactor/effbandwidth
    print(rad[0,0],rad.dtype)
    dst.write_band(i+1, rad)
    i += 1
