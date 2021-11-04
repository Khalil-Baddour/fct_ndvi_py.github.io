# 1 - import librairies

from osgeo import gdal
import numpy as np
np.seterr(divide='ignore', invalid='ignore') # Set how floating-point errors are handled.
from math import*
import os

# 2 - definition of the function of the calculation of NDVI
def fct_ndvi (filename):
    
    ## A -- Open image
    data_set = gdal.Open(filename, gdal.GA_ReadOnly)      
    ## B -- get dimensions of image
    nb_col = data_set.RasterXSize
    nb_lignes = data_set.RasterYSize
    nb_band = data_set.RasterCount
    
    ## C -- convert data type from gdal to numpy style
    band = data_set.GetRasterBand(1)
    gdal_data_type = gdal.GetDataTypeName(band.DataType)
    numpy_data_type = gdal_data_type.lower()
        
    ## D -- Load the whole image into an numpy array with gdal
    
    # Initialize an empty array
    array = np.empty((nb_lignes, nb_col, nb_band), dtype=numpy_data_type) 
    
    # Fill the array
    for idx_band in range(nb_band):
        idx_band_gdal = idx_band + 1
        array[:, :, idx_band] = data_set.GetRasterBand(idx_band_gdal).ReadAsArray()
    # close data_set
    data_set = None
    band = None
    
    ## E -- Compute NDVI
    ir = array[:,:, 3].astype('float32') ## l'index 3 numpy correspond à la bande Infra-rouge de mon image test
    r = array[:,:, 0].astype('float32')  ## l'index 0 numpy correspond à la bande rouge mon image test 
    ndvi = (ir - r) / (ir + r)
    return ndvi

# 3 - application of the function to my test image & write image
my_folder = 'C:/Users/Etudiant/Desktop/my_folder'
my_image = os.path.join(my_folder, 'my_img_test.tif')
my_ndvi = fct_ndvi(my_image)
print(my_ndvi)


# 4 - save the result : write image
    # A- definition f the parameters
data_type_match = {'uint8': gdal.GDT_Byte,
                   'uint16': gdal.GDT_UInt16,
                   'uint32': gdal.GDT_UInt32,
                   'int16': gdal.GDT_Int16,
                   'int32': gdal.GDT_Int32,
                   'float32': gdal.GDT_Float32,
                   'float64': gdal.GDT_Float64}

out_ndvi = os.path.join(my_folder, 'my_ndvi_test.tif')

    # B- definition of a function to write an image
def write_image(out_filename, array, data_set=None, gdal_dtype=None,
                transform=None, projection=None, driver_name=None,
                nb_col=None, nb_ligne=None, nb_band=None):
    """
    Write a array into an image file.

    """
    # Get information from array if the parameter is missing
    nb_col = nb_col if nb_col is not None else array.shape[1]
    nb_ligne = nb_ligne if nb_ligne is not None else array.shape[0]
    array = np.atleast_3d(array)  # not asked in the instructions.
                                  # but it deals with the case a 2d
                                  # dimension array is passed.
    nb_band = nb_band if nb_band is not None else array.shape[2]


    # Get information from data_set if provided
    transform = transform if transform is not None else data_set.GetGeoTransform()
    projection = projection if projection is not None else data_set.GetProjection()
    gdal_dtype = gdal_dtype if gdal_dtype is not None \
        else data_set.GetRasterBand(1).DataType
    driver_name = driver_name if driver_name is not None \
        else data_set.GetDriver().ShortName

    # Create DataSet
    driver = gdal.GetDriverByName(driver_name)
    output_data_set = driver.Create(out_filename, nb_col, nb_ligne, nb_band,
                                    gdal_dtype)
    output_data_set.SetGeoTransform(transform)
    output_data_set.SetProjection(projection)

    # Fill it and write image
    for idx_band in range(nb_band):
        output_band = output_data_set.GetRasterBand(idx_band + 1)
        output_band.WriteArray(array[:, :, idx_band])  # not working with a 2d array.
                                                       
                                                       
        output_band.FlushCache()

    del output_band
    output_data_set = None

    # D- Save image
write_image(out_ndvi, my_ndvi, data_set=data_set,
            gdal_dtype=data_type_match['float32'])
