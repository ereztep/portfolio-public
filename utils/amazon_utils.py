import numpy as np
import pandas as pd
from pystac_client import Client
from shapely import geometry
import rioxarray



# def scale_values(values):
#     # # Get the minimum and maximum values
#     max_value_allowed = 5000
#     # min_value = np.min(values)
#     # max_value = np.max(values)
#     # # Calculate the range of the values
#     # value_range = max_value - min_value
#     if max_value_allowed-np.min(values) == 0:
#         print(np.max(values)-np.min(values))
#         return None

#     # Scale the values to a range of 0 to 1
#     scaled_values = np.rint(255*((values - np.min(values)) / (np.max(values)-np.min(values))))
#     scaled_values = np.where(scaled_values >= 255, 255, scaled_values)

#     return  scaled_values
#     # return  (min_value, max_value, value_range) # scaled_values_int


def scale_values(values):
    # Get the minimum and maximum values
    max_value_allowed = 5000
    min_value = np.min(values)
    max_value = np.max(values)
    # Calculate the range of the values
    value_range = max_value_allowed - min_value
    # Scale the values to a range of 0 to 1
    scaled_values = np.array([255*((value - min_value) / value_range) for value in values]).astype(int)
    scaled_values = np.where(scaled_values >= 255, 255, scaled_values)

    return  scaled_values

def chipping(mosaic,dist,overlap):

    # calculate longitudes of top left corner
    vec_x = int((1-overlap)*dist)*np.arange(0,int(mosaic.shape[0]//int((1-overlap)*dist)),1)
    vec_x[-1] = mosaic.shape[0]-dist

    # calculate latitudes of top left corner
    vec_y = int((1-overlap)*dist)*np.arange(0,int(mosaic.shape[1]//int((1-overlap)*dist)),1)
    vec_y[-1] = mosaic.shape[1]-dist

    # create the data frame with longitude and latitude of both corners of the chip
    chip_df = pd.DataFrame(data=np.array(np.meshgrid(vec_x,vec_y)).T.reshape(len(vec_x)*len(vec_y),2), columns=['x_top_left', 'y_top_left'])

    chip_df['x_bottom_right'] = chip_df.apply(lambda x: x['x_top_left']+dist , axis=1)
    chip_df['y_bottom_right'] = chip_df.apply(lambda x: x['y_top_left']+dist , axis=1)

    chip_df['rgb'] = chip_df.apply(lambda x: mosaic[x['x_top_left']:x['x_bottom_right'],x['y_top_left']:x['y_bottom_right'],:]  , axis=1)

    return chip_df

def aws_sentinel_retrieve_item(max_items, cloud_cover,start_date,end_date,area):

    search = Client.open("https://earth-search.aws.element84.com/v0").search(
        collections=["sentinel-s2-l2a-cogs"],
        intersects=geometry.Point(area[0],area[1]),
        max_items=max_items,
        datetime=f"{start_date}/{end_date}",
        query=[f"eo:cloud_cover<{cloud_cover}"]
        # resolution  =10
    )

    # create dataframe with main metadata and thumbnails

    if search.matched() < 1:
        return 'failed'

    items = search.get_all_items()

    item = items[pd.DataFrame(data = {'cloud_cover' : [item.properties['eo:cloud_cover'] for item in items]}).sort_values(by='cloud_cover').index[0]]

    del items

    return item

def aws_sentinel_chip(item,area):

    geom = item.geometry['coordinates'][0]

    lon_geom = [i[0] for i in geom]
    lat_geom = [i[1] for i in geom]

    max_lon = max(lon_geom)
    min_lon = min(lon_geom)
    max_lat = max(lat_geom)
    min_lat = min(lat_geom)

    ind_item = (-min_lon+area[0])//((-min_lon+max_lon)/61)*61 + (-min_lat+area[1])//((-min_lat+max_lat)/61)

    # Merge each colour band independently and group them into a RGB array

    mosaic_red = rioxarray.open_rasterio(item.assets["B04"].href).values
    mosaic_green = rioxarray.open_rasterio(item.assets["B03"].href).values
    mosaic_blue = rioxarray.open_rasterio(item.assets["B02"].href).values

    mosaic_rgb = np.stack([mosaic_red.reshape((mosaic_red.shape[1],mosaic_red.shape[2])),
                           mosaic_green.reshape((mosaic_green.shape[1],mosaic_green.shape[2])),
                           mosaic_blue.reshape((mosaic_blue.shape[1],mosaic_blue.shape[2]))],
                          axis=2)

    print(f'red : max - {np.max(mosaic_red)} , min - {np.min(mosaic_red)} ')
    print(f'green : max - {np.max(mosaic_green)} , min - {np.min(mosaic_green)} ')
    print(f'blue : max - {np.max(mosaic_blue)} , min - {np.min(mosaic_blue)} ')

    del mosaic_blue
    del mosaic_green
    del mosaic_red

    mosaic_rgb = chipping(mosaic_rgb,256,0.3)

    mosaic_rgb = mosaic_rgb.iloc[int(ind_item)]['rgb']

    # print(mosaic_rgb)

    for i in range(3):
        print(i)
        mosaic_rgb[:,:,i] = scale_values(mosaic_rgb[:,:,i])

    return   mosaic_rgb
