#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 09:10:47 2018

@author: jmanning
"""

import netCDF4
import datetime
import zlconversions as zl
import numpy as np
import pandas as pd

def get_doppio(lat=0,lon=0,depth=99999,time='2018-11-12 12:00:00'):
    """
    notice:
        the format of time is like "%Y-%m-%d %H:%M:%S"
        the depth is under the bottom depth
    the module only output the temperature of point location
    """
    date_time=datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S') # transform time format
    for i in range(0,7):
        url_time=(date_time-datetime.timedelta(hours=i)).strftime('%Y-%m-%d')#
        url=zl.get_doppio_url(url_time)
        nc=netCDF4.Dataset(url)
        lons=nc.variables['lon_rho'][:]
        lats=nc.variables['lat_rho'][:]
        temp=nc.variables['temp']
        doppio_time=nc.variables['time']
        doppio_depth=nc.variables['h'][:]
        min_diff_time=abs(datetime.datetime(2017,11,1,0,0,0)+datetime.timedelta(hours=int(doppio_time[0]))-date_time)
        min_diff_index=0
        for i in range(1,157):
            diff_time=abs(datetime.datetime(2017,11,1,0,0,0)+datetime.timedelta(hours=int(doppio_time[i]))-date_time)
            if diff_time<min_diff_time:
                min_diff_time=diff_time
                min_diff_index=i
                
        min_distance=zl.dist(lat1=lat,lon1=lon,lat2=lats[0][0],lon2=lons[0][0])
        index_1,index_2=0,0
        for i in range(len(lons)):
            for j in range(len(lons[i])):
                if min_distance>zl.dist(lat1=lat,lon1=lon,lat2=lats[i][j],lon2=lons[i][j]):
                    min_distance=zl.dist(lat1=lat,lon1=lon,lat2=lats[i][j],lon2=lons[i][j])
                    index_1=i
                    index_2=j
        if depth==99999:
            S_coordinate=1
        else:
            S_coordinate=float(depth)/float(doppio_depth[index_1][index_2])
        if 0<=S_coordinate<1:
            point_temp=temp[min_diff_index][39-int(S_coordinate/0.025)][index_1][index_2]
        elif S_coordinate==1:
            point_temp=temp[min_diff_index][39][index_1][index_2]
        else:
            return 9999
        if np.isnan(point_temp):
            continue
        if min_diff_time<datetime.timedelta(hours=1):
            break
    return point_temp
#def output_hour_data(file):
#    df=zl.skip_to(file,'HEADING')  #only get the data in file
#    hour_df=pd.DataFrame(data=None,columns=['HEADING','Datet(GMT)','Lat','Lon','Temperature(C)','Depth(m)'])
#    for i in range(len(df)):
#        time=datetime.datetime.strptime(df[],'%Y-%m-%d %H:%M:%S')
#        hour_time=datetime.datetime.strptime(time.strftime('%Y-%m-%d %H'),'%Y-%m-%d %H')
#        if time-hour_time==datetime.timedelta(hours=0):
            
            
            
        
        