


import bokeh.models as bkm
from bokeh.io import curdoc
from bokeh.layouts import layout
from bokeh.plotting import figure
from bokeh.models import HoverTool, LabelSet, ColumnDataSource
from bokeh.tile_providers import get_provider, STAMEN_TERRAIN, OSM
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler

# import requests
import json
import pandas as pd
import numpy as np
import sqlite3



# SQLite database of DRONES
# db_file = '/Users/gianlucafilippi/GitHub/smart-o2c/MATLAB/Problems/CAELUS/AgentBasedModel/drones_sim.db'
db_file = '/home/caelus/Documents/GitHub/CAELUS_Optimisation/src/ModelsMetrics/AgentBased/Data_Bases/drones_sim.db'
# SQLite database of STATIONS
# db_file_stations = '/Users/gianlucafilippi/GitHub/smart-o2c/MATLAB/Problems/CAELUS/AgentBase/SQLlite/test_stationstype.db'
# db_file_stations = '/Users/gianlucafilippi/GitHub/smart-o2c/MATLAB/Problems/CAELUS/AgentBasedModel/stations_sim.db'
db_file_stations = '/home/caelus/Documents/GitHub/CAELUS_Optimisation/src/ModelsMetrics/AgentBased/Data_Bases/stations_sim.db'
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




conn = sqlite3.connect(db_file)
conn_2 = sqlite3.connect(db_file_stations)


stations_df_A = pd.read_sql_query("SELECT * from TrackingStations WHERE type = 'A' ", conn_2)
stations_df_H = pd.read_sql_query("SELECT * from TrackingStations WHERE type = 'H' ", conn_2)
stations_df_L = pd.read_sql_query("SELECT * from TrackingStations WHERE type = 'L' ", conn_2)
stations_df_new = pd.read_sql_query("SELECT * from TrackingStations WHERE type = 'new' ", conn_2)

wgs84_to_web_mercator(stations_df_A)
wgs84_to_web_mercator(stations_df_H)
wgs84_to_web_mercator(stations_df_L)
wgs84_to_web_mercator(stations_df_new)

stations_source_A=ColumnDataSource(stations_df_A)
stations_source_H=ColumnDataSource(stations_df_H)
stations_source_L=ColumnDataSource(stations_df_L)
stations_source_new=ColumnDataSource(stations_df_new)



p=figure(x_range=x_range,y_range=y_range,
        x_axis_type='mercator',y_axis_type='mercator',
        sizing_mode='scale_width',plot_height=300, #width=300, #plot_height
        tools="pan, box_select, zoom_in, zoom_out, box_zoom, save, reset")
tile_prov=get_provider(OSM)
p.add_tile(tile_prov,level='image')





def read_data():
    flight_df = pd.read_sql_query("SELECT * from TrackingDrones", conn)
    flight_df_0 = pd.read_sql_query("SELECT * from TrackingDrones WHERE package = 0 ", conn)
    flight_df_1 = pd.read_sql_query("SELECT * from TrackingDrones WHERE package = 1 ", conn)

    wgs84_to_web_mercator(flight_df)
    wgs84_to_web_mercator(flight_df_0)
    wgs84_to_web_mercator(flight_df_1)

    flight_df=flight_df.fillna('No Data')
    flight_df_0=flight_df_0.fillna('No Data')
    flight_df_1=flight_df_1.fillna('No Data')

    # CONVERT TO BOKEH DATASOURCE AND STREAMING
    n_roll=len(flight_df.index)
    n_roll_0=len(flight_df_0.index)
    n_roll_1=len(flight_df_1.index)

    flight_source.stream(flight_df.to_dict(orient='list'),n_roll)
    flight_source_0.stream(flight_df_0.to_dict(orient='list'),n_roll_0)
    flight_source_1.stream(flight_df_1.to_dict(orient='list'),n_roll_1)




# define source
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


size_st = 15
pA = p.square('x','y',source=stations_source_A, size=size_st, color="black", alpha=0.5)
pH = p.square('x','y',source=stations_source_H, size=size_st, color="blue", alpha=0.5)
pL = p.square('x','y',source=stations_source_L, size=size_st, color="olive", alpha=0.5)
pnew = p.square('x','y',source=stations_source_new, size=size_st, color="green", alpha=0.5)

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

stA_hover = bkm.HoverTool(renderers=[pA],
                        tooltips=[('system', '@system'), ('station type','@type'), ('station ID','@numberID'),('latitude','@lat'),('longitude','@lon'), ('status', '@status'), ('storge_capacity', '@storge_capacity'), ('charging_capacity', '@charging_capacity')])
p.add_tools(stA_hover)
stH_hover = bkm.HoverTool(renderers=[pH],
                        tooltips=[('system', '@system'), ('station type','@type'), ('station ID','@numberID'),('latitude','@lat'),('longitude','@lon'), ('status', '@status'), ('storge_capacity', '@storge_capacity'), ('charging_capacity', '@charging_capacity')])
p.add_tools(stH_hover)
stL_hover = bkm.HoverTool(renderers=[pL],
                        tooltips=[('system', '@system'), ('station type','@type'), ('station ID','@numberID'),('latitude','@lat'),('longitude','@lon'), ('status', '@status'), ('storge_capacity', '@storge_capacity'), ('charging_capacity', '@charging_capacity')])
p.add_tools(stL_hover)
stnew_hover = bkm.HoverTool(renderers=[pnew],
                        tooltips=[('system', '@system'), ('station type','@type'), ('station ID','@numberID'),('latitude','@lat'),('longitude','@lon'), ('status', '@status'), ('storge_capacity', '@storge_capacity'), ('charging_capacity', '@charging_capacity')])
p.add_tools(stnew_hover)



dr_empty = bkm.HoverTool(renderers=[pDroneEmpty],
                        tooltips=[('system', '@system'), ('drone ID','@numberID'),('latitude','@lat'),('longitude','@lon'),('package','@package'),('SOC','@SOC'),('Temperature of package','@T_package'), ('Drone status','@status')])
p.add_tools(dr_empty)
dr_full = bkm.HoverTool(renderers=[pDroneFull],
                        tooltips=[('system', '@system'), ('drone ID','@numberID'),('latitude','@lat'),('longitude','@lon'),('package','@package'),('SOC','@SOC'),('Temperature of package','@T_package'), ('Drone status','@status')])
p.add_tools(dr_full)


labels = LabelSet(x='x', y='y', text='textID',
            x_offset=5, y_offset=5, source=flight_source, render_mode='canvas',background_fill_color='white',text_font_size="8pt")
p.add_layout(labels)



# create a periodic update function
def update():

    flight_df = pd.read_sql_query("SELECT * from TrackingDrones", conn)
    flight_df_0 = pd.read_sql_query("SELECT * from TrackingDrones WHERE package = 0 ", conn)
    flight_df_1 = pd.read_sql_query("SELECT * from TrackingDrones WHERE package = 1 ", conn)

    wgs84_to_web_mercator(flight_df)
    wgs84_to_web_mercator(flight_df_0)
    wgs84_to_web_mercator(flight_df_1)

    flight_df=flight_df.fillna('No Data')
    flight_df_0=flight_df_0.fillna('No Data')
    flight_df_1=flight_df_1.fillna('No Data')

    # CONVERT TO BOKEH DATASOURCE AND STREAMING
    n_roll=len(flight_df.index)
    n_roll_0=len(flight_df_0.index)
    n_roll_1=len(flight_df_1.index)

    flight_source.stream(flight_df.to_dict(orient='list'),n_roll)
    flight_source_0.stream(flight_df_0.to_dict(orient='list'),n_roll_0)
    flight_source_1.stream(flight_df_1.to_dict(orient='list'),n_roll_1)









#FLIGHT TRACKING FUNCTION
def flight_tracking(doc):

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

    # init bokeh column data source
    # flight_source_0 = ColumnDataSource({
    #     'system':[], 'textID':[], 'numberID':[], 'info':[], 'lon':[], 'lat':[], 'x':[], 'y':[], 'package':[], 'SOC':[], 'T_package':[], 'status':[] #, 'url':[], 'true_track':[], 'rot_angle':[]
    # })
    # flight_source_1 = ColumnDataSource({
    #     'system':[], 'textID':[], 'numberID':[], 'info':[], 'lon':[], 'lat':[], 'x':[], 'y':[], 'package':[], 'SOC':[], 'T_package':[], 'status':[] #, 'url':[], 'true_track':[], 'rot_angle':[]
    # })    
    # flight_source = ColumnDataSource({
    #     'system':[], 'textID':[], 'numberID':[], 'info':[], 'lon':[], 'lat':[], 'x':[], 'y':[], 'package':[], 'SOC':[], 'T_package':[], 'status':[] #, 'url':[], 'true_track':[], 'rot_angle':[]
    # })  
    # UPDATING FLIGHT DATA
    def update():
        # response=requests.get(url_data).json()
        
        #CONVERT TO PANDAS DATAFRAME
        # col_name=['id','lat','lon']
       
        # flight_df=pd.DataFrame(response['states']) 
        # flight_df=flight_df.loc[:,0:16] 
        # flight_df.columns=col_name
        # wgs84_to_web_mercator(flight_df)
        # flight_df=flight_df.fillna('No Data')
        # flight_df['rot_angle']=flight_df['true_track']*-1

        
        # conn.close
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
        


    #CALLBACK UPATE IN AN INTERVAL
    doc.add_periodic_callback(update, 1000) #5000 ms/10000 ms for registered user . 
     
    #PLOT AIRCRAFT POSITION
    p=figure(x_range=x_range,y_range=y_range,
            x_axis_type='mercator',y_axis_type='mercator',
            sizing_mode='scale_width',plot_height=300, #width=300, #plot_height
            tools="pan, box_select, zoom_in, zoom_out, box_zoom, save, reset")
    tile_prov=get_provider(OSM)
    p.add_tile(tile_prov,level='image')


    

    size_st = 15
    pA = p.square('x','y',source=stations_source_A, size=size_st, color="black", alpha=0.5)
    pH = p.square('x','y',source=stations_source_H, size=size_st, color="blue", alpha=0.5)
    pL = p.square('x','y',source=stations_source_L, size=size_st, color="olive", alpha=0.5)
    pnew = p.square('x','y',source=stations_source_new, size=size_st, color="green", alpha=0.5)


    # p.circle('x','y',source=flight_source,fill_color='black',hover_color='yellow',size=10,fill_alpha=0.8,line_width=0)
    # p.circle('x','y',source=flight_source_0,fill_color='black',hover_color='yellow',size=5,fill_alpha=0.8,line_width=0)
    # p.circle('x','y',source=flight_source_1,fill_color='red',hover_color='yellow',size=5,fill_alpha=0.8,line_width=0)
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
    
    # stA_hover = bkm.HoverTool(renderers=[pA],
    #                         tooltips=tooltips_station_str)
    # p.add_tools(stA_hover)
    # stH_hover = bkm.HoverTool(renderers=[pH],
    #                         tooltips=tooltips_station_str)
    # p.add_tools(stH_hover)
    # stL_hover = bkm.HoverTool(renderers=[pL],
    #                         tooltips=tooltips_station_str)
    # p.add_tools(stL_hover)
    # stnew_hover = bkm.HoverTool(renderers=[pnew],
    #                         tooltips=tooltips_station_str)
    # p.add_tools(stnew_hover)

    stA_hover = bkm.HoverTool(renderers=[pA],
                            tooltips=[('system', '@system'), ('station type','@type'), ('station ID','@numberID'),('latitude','@lat'),('longitude','@lon'), ('status', '@status'), ('storge_capacity', '@storge_capacity'), ('charging_capacity', '@charging_capacity')])
    p.add_tools(stA_hover)
    stH_hover = bkm.HoverTool(renderers=[pH],
                            tooltips=[('system', '@system'), ('station type','@type'), ('station ID','@numberID'),('latitude','@lat'),('longitude','@lon'), ('status', '@status'), ('storge_capacity', '@storge_capacity'), ('charging_capacity', '@charging_capacity')])
    p.add_tools(stH_hover)
    stL_hover = bkm.HoverTool(renderers=[pL],
                            tooltips=[('system', '@system'), ('station type','@type'), ('station ID','@numberID'),('latitude','@lat'),('longitude','@lon'), ('status', '@status'), ('storge_capacity', '@storge_capacity'), ('charging_capacity', '@charging_capacity')])
    p.add_tools(stL_hover)
    stnew_hover = bkm.HoverTool(renderers=[pnew],
                            tooltips=[('system', '@system'), ('station type','@type'), ('station ID','@numberID'),('latitude','@lat'),('longitude','@lon'), ('status', '@status'), ('storge_capacity', '@storge_capacity'), ('charging_capacity', '@charging_capacity')])
    p.add_tools(stnew_hover)






    # DRONES
    # dr_empty = bkm.HoverTool(renderers=[pDroneEmpty],
    #                         tooltips=[('system', '@system'), ('drone ID','@numberID'),('(latitude, longitude)','($lat, $lon)'),('package','@package'),('SOC','@SOC'),('Temperature of package','@T_package'), ('Drone status','@status')])
    # p.add_tools(dr_empty)
    # dr_full = bkm.HoverTool(renderers=[pDroneFull],
    #                         tooltips=[('system', '@system'), ('drone ID','@numberID'),('(latitude, longitude)','($lat, $lon)'),('package','@package'),('SOC','@SOC'),('Temperature of package','@T_package'), ('Drone status','@status')])
    # p.add_tools(dr_full)
    dr_empty = bkm.HoverTool(renderers=[pDroneEmpty],
                            tooltips=[('system', '@system'), ('drone ID','@numberID'),('latitude','@lat'),('longitude','@lon'),('package','@package'),('SOC','@SOC'),('Temperature of package','@T_package'), ('Drone status','@status')])
    p.add_tools(dr_empty)
    dr_full = bkm.HoverTool(renderers=[pDroneFull],
                            tooltips=[('system', '@system'), ('drone ID','@numberID'),('latitude','@lat'),('longitude','@lon'),('package','@package'),('SOC','@SOC'),('Temperature of package','@T_package'), ('Drone status','@status')])
    p.add_tools(dr_full)

    #HOVER INFORMATION AND LABEL
    # my_hover=HoverTool()
    # my_hover.tooltips=[('drone ID number','@id'),('latitude','@lat'),('longitude','@lon'),('package loaded','@package')]
    # p.add_tools(my_hover)

    labels = LabelSet(x='x', y='y', text='textID',
                x_offset=5, y_offset=5, source=flight_source, render_mode='canvas',background_fill_color='white',text_font_size="8pt")
    p.add_layout(labels)
    
    doc.title='REAL TIME FLIGHT TRACKING'
    doc.add_root(p)
    
# SERVER CODE
apps = {'/': Application(FunctionHandler(flight_tracking))}
server = Server(apps, port=8084) #define an unused port
server.start()