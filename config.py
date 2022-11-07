# gpd.GeoDataFrame for Gig Harbor
MAP_JSON = '/Users/abuckley/Documents/flask/data/tax_parcel.geojson'

# centered latitude and longitude coordinates for Gig Harbor
COORDS = (47.31476173672931, -122.61719553658574)

# columns to use to calculate nieghborhood stats
NEIGHBORHOOD_ATTRIBUTES = ['taxable_value','year_built', 'square_feet', 'land_acres',
                     'bedrooms', 'bathrooms', 'attached_garage_square_feet']
