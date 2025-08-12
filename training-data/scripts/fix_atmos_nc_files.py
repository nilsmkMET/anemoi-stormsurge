import sys

def round_to_nearest_3600(data_array):
    """
    Rounds each value in a list to the nearest multiple of 3600.


    Args:
    data_array: A list of numbers (integers or floats).


    Returns:
    A new list with each number rounded to the nearest 3600.
    """
    # The core logic is to divide by 3600, round to the nearest whole number,
    # and then multiply by 3600 again.
    # A list comprehension provides a concise way to apply this to every item.
    rounded_list = [int(round(value / 3600.0) * 3600) for value in data_array]
    return rounded_list

def add_latlon_rho(atm_file, grd_file):
    """
    Adds latitude and longitude rho points to a netCDF file.
    Args:
        nc_file (str): Path to the netCDF file.
    """
    import os
    os.system(f"ncks -A -v lat_rho,lon_rho {grd_file} {atm_file}")

def add_latlon_standard_name(atm_file):
    """ 
    Adds standard names for latitude and longitude variables in a netCDF file.
    Args:
        atm_file (str): Path to the netCDF file.
    """
    import netCDF4
    ds = netCDF4.Dataset(atm_file, 'r+')
    if 'lat_rho' in ds.variables:
        ds.variables['lat_rho'].standard_name = 'latitude'
        # ds.sync()
        print("Added standard name 'latitude' to 'lat_rho'.")
    if 'lon_rho' in ds.variables:
        ds.variables['lon_rho'].standard_name = 'longitude'
        # ds.sync()
        print("Added standard name 'longitude' to 'lon_rho'.")
    if 'lat_u' in ds.variables:
        ds.variables['lat_u'].standard_name = 'latitude'
        # ds.sync()
        print("Added standard name 'latitude' to 'lat_u'.")
    if 'lon_u' in ds.variables:
        ds.variables['lon_u'].standard_name = 'longitude'
        # ds.sync()
        print("Added standard name 'longitude' to 'lon_u'.")
    if 'lat_v' in ds.variables:
        ds.variables['lat_v'].standard_name = 'latitude'
        # ds.sync()
        print("Added standard name 'latitude' to 'lat_v'.")
    if 'lon_v' in ds.variables:
        ds.variables['lon_v'].standard_name = 'longitude'
        # ds.sync()
        print("Added standard name 'longitude' to 'lon_v'.")
    ds.sync()
    ds.close()

def add_latlon_standard_name_nco(atm_file, latlonuv_file):
    import os
    """
    Adds standard names for latitude and longitude variables in a netCDF file using nco.
    Args:
        atm_file (str): Path to the netCDF file.
    """
    tmp_file = atm_file + '.fixedlatlonuv'
    os.system(f"ncks -x -v lat_u,lon_u,lat_v,lon_v {atm_file} {tmp_file}")
    os.system(f"ncks -A -v lat_u,lat_v,lon_u,lon_v {latlonuv_file} {tmp_file}")

def add_latlon_standard_name_xarray(atm_file):
    """
    Adds standard names for latitude and longitude variables using xarray.
    This version uses the robust read-modify-write pattern to save changes.

    Args:
        atm_file (str): Path to the netCDF file.
    """
    
    import xarray as xr
    import os
    
    tmp_file = atm_file + '.tmp'

    # 1. Open the original dataset for reading
    with xr.open_dataset(atm_file, decode_times=False) as ds:
        
        vars_to_update = {
            'lat_rho': 'latitude', 'lon_rho': 'longitude',
            'lat_u': 'latitude', 'lon_u': 'longitude',
            'lat_v': 'latitude', 'lon_v': 'longitude',
        }
        
        # 2. Modify the attributes on the in-memory dataset
        for var_name, standard_name in vars_to_update.items():
            if var_name in ds:
                ds[var_name].attrs['standard_name'] = standard_name
                print(f"Set standard_name for '{var_name}' to '{standard_name}'.")

        # 3. Write the entire modified dataset to a new temporary file
        print("\nWriting changes to a temporary file...")
        ds.to_netcdf(tmp_file)

    # 4. Replace the original file with the new, corrected one
    os.replace(tmp_file, atm_file)
    print("Original file has been updated successfully.")

def fix_timevar(nc_file):
    """
    Fixes the time variable type in a netCDF file to be double.
    Ensures that the time variable is rounded to the nearest hour.
    Args:
        nc_file (str): Path to the netCDF file.
    """
    import os
    import netCDF4
    # Use ncap2 to change the time variable type to double
    # This is a workaround for some netCDF files that have time as float32
    # which can cause issues in some applications.
    os.system(f"ncap2 -O -s 'time=double(time)' {nc_file} {nc_file}.tmp")
    os.system(f"mv {nc_file}.tmp {nc_file}")
    print(f"Converted time variable in {nc_file} to double precision.")
    # Open the netCDF file and round the time to nearest hour.
    with netCDF4.Dataset(nc_file, 'r+') as ds:
        timevar = ds.variables['time']
        tmpvar  = round_to_nearest_3600(timevar[:])
        timevar[:] = tmpvar
        ds.sync()


####################################################################
# Ensure the script is run with the correct number of arguments
if len(sys.argv) != 4:
    print("Usage: python fix_nc_files.py <atm_file> <grd_file> <latlonuv_file>")
    sys.exit(1)

atm_file      = sys.argv[1]
grd_file      = sys.argv[2]
latlonuv_file = sys.argv[3]

print(f"Processing atmospheric file: {atm_file}")
print(f"Using grid file: {grd_file}")
print(f"Using latlonuv file: {latlonuv_file}")

if True:
    # Check if lat_rho and lon_rho on atmospheric file
    import netCDF4
    with netCDF4.Dataset(atm_file, 'r') as ds:
        if 'lat_rho' in ds.variables and 'lon_rho' in ds.variables:
            print("lat_rho and lon_rho already exist in the atmospheric file.")
            pass
        else:
            print("lat_rho and lon_rho do not exist in the atmospheric file, adding them from the grid file.")
            # Add latitude and longitude rho points to the atmospheric file
            add_latlon_rho(atm_file, grd_file)
            print(f"Added latitude and longitude rho points from {grd_file} to {atm_file}.")
    with netCDF4.Dataset(atm_file, 'r+') as ds:
        # Add standard names for latitude and longitude variables
        ds.variables['lat_rho'].standard_name = 'latitude'
        ds.variables['lon_rho'].standard_name = 'longitude'
        ds.sync()

if False:
    # Fix the time variable type and round it to the nearest hour
    fix_timevar(atm_file)
    print(f"Fixed time variable in {atm_file} to double and rounded to nearest hour.")
if False:
    # Add standard names for latitude and longitude variables
    # add_latlon_standard_name(atm_file)
    # add_latlon_standard_name_xarray(atm_file)
    add_latlon_standard_name_nco(atm_file, latlonuv_file)
    print(f"Added standard names for latitude and longitude variables in {atm_file}.")

print(f"Processed {atm_file} with grid file {grd_file} and {latlonuv_file}.")