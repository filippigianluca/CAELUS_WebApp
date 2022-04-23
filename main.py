#IMPORT LIBRARY


import json
import sqlite3
import pandas as pd
import numpy as np
import bokeh.models as bkm

from bokeh.io import curdoc
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row
from bokeh.models import HoverTool, LabelSet, ColumnDataSource,  DataRange1d, Select, DateRangeSlider, Slider
from bokeh.tile_providers import get_provider, STAMEN_TERRAIN, OSM, CARTODBPOSITRON
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.layouts import layout



# SQLite database of DRONES
db_file = '/Users/gianlucafilippi/GitHub/smart-o2c/MATLAB/Problems/CAELUS/AgentBasedModel/drones_sim.db'
# SQLite database of STATIONS
# db_file_stations = '/Users/gianlucafilippi/GitHub/smart-o2c/MATLAB/Problems/CAELUS/AgentBase/SQLlite/test_stationstype.db'
db_file_stations = '/Users/gianlucafilippi/GitHub/smart-o2c/MATLAB/Problems/CAELUS/AgentBasedModel/stations_sim.db'
# image url
# # image url
url_image = '/Users/gianlucafilippi/GitHub/CAELUS_DT/CAELUS_Interface_Optimiser_DT/Tracker/airplane.png'





#FUNCTION TO CONVERT GCS WGS84 TO WEB MERCATOR
#DATAFRAME
def wgs84_to_web_mercator(df, lon="lon", lat="lat"):
    k = 6378137
    df["x"] = df[lon] * (k * np.pi/180.0)
    df["y"] = np.log(np.tan((90 + df[lat]) * np.pi/360.0)) * k
    return df

#POINT
def wgs84_web_mercator_point(lon,lat):
    k = 6378137
    x= lon * (k * np.pi/180.0)
    y= np.log(np.tan((90 + lat) * np.pi/360.0)) * k
    return x,y

#AREA EXTENT COORDINATE WGS84
lon_min,lat_min=-8, 55 # -125.974,30.038
lon_max,lat_max= 0, 61 # -68.748,52.214

#COORDINATE CONVERSION
xy_min=wgs84_web_mercator_point(lon_min,lat_min)
xy_max=wgs84_web_mercator_point(lon_max,lat_max)

#COORDINATE RANGE IN WEB MERCATOR
x_range,y_range=([xy_min[0],xy_max[0]], [xy_min[1],xy_max[1]])


#REST API QUERY
# user_name=''
# password=''
# url_data='https://'+user_name+':'+password+'@opensky-network.org/api/states/all?'+'lamin='+str(lat_min)+'&lomin='+str(lon_min)+'&lamax='+str(lat_max)+'&lomax='+str(lon_max)




conn = sqlite3.connect(db_file)
conn_2 = sqlite3.connect(db_file_stations)



# stations_df_A = pd.read_sql_query("SELECT * from TrackingStations WHERE type = 'A' ", conn_2)
# stations_df_H = pd.read_sql_query("SELECT * from TrackingStations WHERE type = 'H' ", conn_2)
# stations_df_L = pd.read_sql_query("SELECT * from TrackingStations WHERE type = 'L' ", conn_2)
# stations_df_new = pd.read_sql_query("SELECT * from TrackingStations WHERE type = 'new' ", conn_2)


# wgs84_to_web_mercator(stations_df_A)
# wgs84_to_web_mercator(stations_df_H)
# wgs84_to_web_mercator(stations_df_L)
# wgs84_to_web_mercator(stations_df_new)

# stations_source_A=ColumnDataSource(stations_df_A)
# stations_source_H=ColumnDataSource(stations_df_H)
# stations_source_L=ColumnDataSource(stations_df_L)
# stations_source_new=ColumnDataSource(stations_df_new)




#FLIGHT TRACKING FUNCTION
def flight_tracking(doc):

    station_name_db = {
        'system':[],   
        'textID':[], 
        'numberID':[], 
        'info':[], 
        'type':[], 
        'lon':[], 
        'lat':[], 
        'x':[], 
        'y':[], 
        'status':[], 
        'storge_capacity':[], 
        'charging_capacity':[], 
        'infrastructure_chargin':[], 
        'infrastructure_takeoff_landing':[], 
        'infrastructure_drone_storage':[]
    }
    stations_source_A=ColumnDataSource(station_name_db)
    stations_source_H=ColumnDataSource(station_name_db)
    stations_source_L=ColumnDataSource(station_name_db)
    stations_source_new=ColumnDataSource(station_name_db)


    drone_name_db = {
        'system':[], 
        'textID':[], 
        'numberID':[], 
        'info':[], 
        'lon':[], 
        'lat':[], 
        'x':[], 
        'y':[], 
        'package':[], 
        'SOC':[], 
        'T_package':[], 
        'status':[] #, 'url':[], 'true_track':[], 'rot_angle':[]
    }
    flight_source_0 = ColumnDataSource(drone_name_db)
    flight_source_1 = ColumnDataSource(drone_name_db)    
    flight_source = ColumnDataSource(drone_name_db)  





    # UPDATING FLIGHT DATA
    def update():

        # db_file = '/Users/gianlucafilippi/GitHub/smart-o2c/MATLAB/Problems/CAELUS/AgentBase/SQLlite/test_drones.db'
        # conn = sqlite3.connect(db_file)
        flight_df = pd.read_sql_query("SELECT * from TrackingDrones", conn)
        flight_df_0 = pd.read_sql_query("SELECT * from TrackingDrones WHERE package = 0 ", conn)
        flight_df_1 = pd.read_sql_query("SELECT * from TrackingDrones WHERE package = 1 ", conn)

        wgs84_to_web_mercator(flight_df)
        wgs84_to_web_mercator(flight_df_0)
        wgs84_to_web_mercator(flight_df_1)

        flight_df=flight_df.fillna('No Data')
        flight_df_0=flight_df_0.fillna('No Data')
        flight_df_1=flight_df_1.fillna('No Data')
    

        # flight_df['rot_angle']=flight_df['true_track']*-1
        # icon_url='https://www.shutterstock.com/image-vector/vector-illustration-airplane-icon-dark-color-2040032426' # 'https:...' #icon url
        # flight_df['url']=icon_url
        # flight_df.head()

        # CONVERT TO BOKEH DATASOURCE AND STREAMING
        n_roll=len(flight_df.index)
        n_roll_0=len(flight_df_0.index)
        n_roll_1=len(flight_df_1.index)

        flight_source.stream(flight_df.to_dict(orient='list'),n_roll)
        flight_source_0.stream(flight_df_0.to_dict(orient='list'),n_roll_0)
        flight_source_1.stream(flight_df_1.to_dict(orient='list'),n_roll_1)
        



        ###########################################################
        stations_df_A = pd.read_sql_query("SELECT * from TrackingStations WHERE type = 'A' ", conn_2)
        stations_df_H = pd.read_sql_query("SELECT * from TrackingStations WHERE type = 'H' ", conn_2)
        stations_df_L = pd.read_sql_query("SELECT * from TrackingStations WHERE type = 'L' ", conn_2)
        stations_df_new = pd.read_sql_query("SELECT * from TrackingStations WHERE type = 'new' ", conn_2)

        wgs84_to_web_mercator(stations_df_A)
        wgs84_to_web_mercator(stations_df_H)
        wgs84_to_web_mercator(stations_df_L)
        wgs84_to_web_mercator(stations_df_new)

        stations_df_A=stations_df_A.fillna('No Data')
        stations_df_H=stations_df_H.fillna('No Data')
        stations_df_L=stations_df_L.fillna('No Data')
        stations_df_new=stations_df_new.fillna('No Data')

        n_roll_A=len(stations_df_A.index)
        n_roll_H=len(stations_df_H.index)
        n_roll_L=len(stations_df_L.index)
        n_roll_new=len(stations_df_new.index)

        stations_source_A.stream(stations_df_A.to_dict(orient='list'),n_roll)
        stations_source_H.stream(stations_df_H.to_dict(orient='list'),n_roll_0)
        stations_source_L.stream(stations_df_L.to_dict(orient='list'),n_roll_1)
        stations_source_new.stream(stations_df_new.to_dict(orient='list'),n_roll_1)





    #CALLBACK UPATE IN AN INTERVAL
    doc.add_periodic_callback(update, 1000) #5000 ms/10000 ms for registered user . 


    #PLOT AIRCRAFT POSITION
    p=figure(x_range=x_range,y_range=y_range,
            x_axis_type='mercator',y_axis_type='mercator',
            sizing_mode='scale_width',plot_height=350, #width=300, #plot_height
            tools="pan, box_select, zoom_in, zoom_out, box_zoom, save, reset")


    def plot_stations(size_st, alpha_st):
        
        pA = p.square('x','y',source=stations_source_A, size=size_st, color="black", alpha = alpha_st)
        pH = p.square('x','y',source=stations_source_H, size=size_st, color="blue", alpha = alpha_st)
        pL = p.square('x','y',source=stations_source_L, size=size_st, color="olive", alpha = alpha_st)
        pnew = p.square('x','y',source=stations_source_new, size=size_st, color="green", alpha = alpha_st)

        return pA, pH, pL, pnew
        
    size_st = 10
    alpha_st = 0.5
    pA, pH, pL, pnew = plot_stations(size_st, alpha_st)


    # provider = 'OSM'
    # provider_select = Select(value=provider, title='Map Provider', options=['STAMEN_TERRAIN', 'OSM'])
    def update_prov(attrname, old, new):
        if provider_select.value == 'OSM':
            tile_prov=get_provider(OSM)
            p.add_tile(tile_prov,level='image')
        elif provider_select.value == 'STAMEN_TERRAIN':
            tile_prov=get_provider(STAMEN_TERRAIN)
            p.add_tile(tile_prov,level='image')
        else:
            tile_prov=get_provider(CARTODBPOSITRON)
            p.add_tile(tile_prov,level='image')
        return tile_prov


    # def update_slider(attrname, old, new):
    #     size_st = amplitude.value
    #     plot_stations(size_st, 1)




    tile_prov=get_provider(OSM)
    p.add_tile(tile_prov,level='image')


 


    pDroneEmpty = p.circle('x','y',source=flight_source_0,fill_color='black',hover_color='yellow',size=10,fill_alpha=0.8,line_width=0)
    pDroneFull = p.circle('x','y',source=flight_source_1,fill_color='red',hover_color='yellow',size=10,fill_alpha=0.8,line_width=0)

    # p.image_url(url='url', x='x', y='y',source=flight_source,anchor='center',angle_units='deg',angle='rot_angle',h_units='screen',w_units='screen',w=400,h=400)
    

    # STATIONS HOVER
    tooltips_station_str = [('system', '@system'), 
                            ('station ID', '@numberID'), 
                            ('info', '@info'), 
                            ('station type', '@type'), 
                            ('longitude', '@lon'), 
                            ('latitude', '@lat'), 
                            ('status', '@status'), 
                            ('storge capacity', '@storge_capacity'), 
                            ('charging capacity', '@charging_capacity'), 
                            ('infrastructure chargin', '@infrastructure_chargin'),
                            ('infrastructure takeoff landing', '@infrastructure_takeoff_landing'),
                            ('infrastructure drone storage', '@infrastructure_drone_storage')
                            ]
    


    stA_hover = bkm.HoverTool(renderers=[pA], tooltips=tooltips_station_str)
    stH_hover = bkm.HoverTool(renderers=[pH],  tooltips=tooltips_station_str)
    stL_hover = bkm.HoverTool(renderers=[pL],  tooltips=tooltips_station_str)
    stnew_hover = bkm.HoverTool(renderers=[pnew],  tooltips=tooltips_station_str)
    dr_empty = bkm.HoverTool(renderers=[pDroneEmpty],  tooltips=tooltips_station_str)
    dr_full = bkm.HoverTool(renderers=[pDroneFull], tooltips=tooltips_station_str)

    p.add_tools(stA_hover)
    p.add_tools(stH_hover)
    p.add_tools(stL_hover)
    p.add_tools(stnew_hover)
    p.add_tools(dr_empty)
    p.add_tools(dr_full)




    labels = LabelSet(x='x', y='y', text='textID',
                x_offset=5, y_offset=5, source=flight_source, render_mode='canvas',background_fill_color='white',text_font_size="8pt")
    p.add_layout(labels)
    


    # Set Up Select
    provider_select = Select(value='OSM', 
                            title='Map Provider', 
                            options=['STAMEN_TERRAIN', 'OSM','CARTODBPOSITRON'])
    provider_select.on_change('value', update_prov)




    # Set Up Slider for stations size 
    amplitude_select = Slider(title="stations' dimention", 
                        value=pA.glyph.size, 
                        start=0.0, 
                        end=15.0, 
                        step=0.1)
    amplitude_select.js_link("value", pA.glyph, "size")
    amplitude_select.js_link("value", pH.glyph, "size")
    amplitude_select.js_link("value", pL.glyph, "size")
    amplitude_select.js_link("value", pnew.glyph, "size")



    # Set Up Slider for stations transparency 
    alpha_select = Slider(title="stations' tranparency", 
                        value=pA.glyph.fill_alpha, 
                        start=0.0, 
                        end=1.0, 
                        step=0.01)
    alpha_select.js_link("value", pA.glyph, "fill_alpha")
    alpha_select.js_link("value", pH.glyph, "fill_alpha")
    alpha_select.js_link("value", pL.glyph, "fill_alpha")
    alpha_select.js_link("value", pnew.glyph, "fill_alpha")



    # layout
    control_layout = column(provider_select, amplitude_select, alpha_select)
    plot_layout = row(p, control_layout)



    doc.title='REAL TIME FLIGHT TRACKING'
    doc.add_root(plot_layout)

    





def main_fun():
    flight_tracking(curdoc())
    
main_fun()

# # SERVER CODE
# apps = {'/': Application(FunctionHandler(flight_tracking))}
# server = Server(apps, port=8084) #define an unused port
# server.start()