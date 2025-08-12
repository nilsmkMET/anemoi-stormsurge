import sys

def add_latlon_standard_name(nc_file):
    """ 
    Adds standard names for latitude and longitude variables in a netCDF file.
    Args:
        nc_file (str): Path to the netCDF file.
    """
    import netCDF4
    with netCDF4.Dataset(nc_file, 'r+') as ds:
        if 'lat_rho' in ds.variables:
            ds.variables['lat_rho'].standard_name = 'latitude'
        if 'lon_rho' in ds.variables:
            ds.variables['lon_rho'].standard_name = 'longitude'
        ds.sync()


# Ensure the script is run with the correct number of arguments
if len(sys.argv) != 2:
    print("Usage: python fix_ocean_nc_files.py <ocn_file>")
    sys.exit(1)

ocn_file = sys.argv[1]

print(f"Processing ocean file: {ocn_file}")

# Add standard names for latitude and longitude variables
add_latlon_standard_name(ocn_file)
print(f"Added standard names for latitude and longitude variables in {ocn_file}.")

print(f"Processed {ocn_file}.")