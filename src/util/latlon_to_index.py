from rasterio.transform import rowcol

# Converts a geographic coordinate (lat, lon) into matrix indices (row, col) using the provided affine transform.
def latlon_to_index(lat, lon, transform):
    row, col = rowcol(transform, lon, lat)
    return row, col