<h2><ul>A Jupyter notebook for large scale high-resolution Antarctic landcover classification</ul></h2>
Bradley Spitzbart, Mark Salvatore, Helen Eifert, Brian Szutu, Heather Lynch 
<br><br>
We present a Jupyter notebook as a demonstration of how to process high-resolution satellite imagery of Antarctica to determine the landcover classification.  This notebook works through the various steps from raw digital number GEOTIFF data to top-of-atmosphere radiance, conversion to surface radiance then surface reflectance.  Spectral ratios are then computed from the surface reflectance.    Ratios have been determined from ground observations to identify areas of water, ice, snow, and geologic features. 
<br><br>
This notebook is a simplification of Python code used for large scale processing on high performance computing (HPC) systems and can be extended for use on HPC and for non-Antarctic regions.
<br>
<h3>To run the notebook:</h3><br>
  main.ipynb calls the other notebooks in the correct order.  It takes one argument, a directory path to the raw input imagery.<br>
<h3> A schematic of the entire pipeline:</h3><br>
  ![Image of pipeline](https://github.com/iceberg-project/LandCover/edit/Feature/notebook/src/notebook/LandCover_pipeline.png)<br>
<h3>An example shapefile output where orange=shadow/water, pink=snow/ice, and purple=sunlit geology (original image coming soon pending licensing approval):</h3><br>
  ![Image of output](https://github.com/iceberg-project/LandCover/edit/Feature/notebook/src/notebook/LandCover_output.png)
  
