# routine for testing the "get_doppio" function
# Lei Zhao wrote most in late 2018
# modifications by JiM in early 2019

from datetime import datetime as dt
from datetime import timedelta
from dateutil import parser
import pandas as pd
import pytz
import glob
import numpy as np
import netCDF4
from conversions import c2f,dd2dm #

#HARDCODES ############
lat1=41.9
lon1=-70.25
depth1=99999#1. # 99999 bottom
#date1=dt.now()-timedelta(days=5) # had to subtract 5 days to get the latest file
date1=dt(2019,8,15,12,0,0)
####
def dist(lat1=0,lon1=0,lat2=0,lon2=0):
    """caculate the distance of two points, return miles"""
    conversion_factor = 0.62137119
    R = 6371.004
    lon1, lat1 = angle_conversion(lon1), angle_conversion(lat1)
    lon2, lat2 = angle_conversion(lon2), angle_conversion(lat2)
    l = R*np.arccos(np.cos(lat1)*np.cos(lat2)*np.cos(lon1-lon2)+\
                        np.sin(lat1)*np.sin(lat2))*conversion_factor
    return l
def angle_conversion(a):
    a = np.array(a)
    return a/180*np.pi
def get_doppio_url(date): # modification of Lei Zhao code to find the most recent DOPPIO url
    url='http://tds.marine.rutgers.edu/thredds/dodsC/roms/doppio/2017_da/his/runs/History_RUN_2018-11-12T00:00:00Z'
    return url.replace('2018-11-12',date)

def get_doppio(lat=0,lon=0,depth=99999,time='2018-11-12 12:00:00'):
    """
    notice:
        the format of time is like "%Y-%m-%d %H:%M:%S"
        the default depth is under the bottom depth
    the module only output the temperature of point location
    """
    import datetime
    #date_time=datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S') # transform time format
    date_time=time
    for i in range(0,7): # look back 7 hours for data
        url_time=(date_time-datetime.timedelta(hours=i)).strftime('%Y-%m-%d')#
        url=get_doppio_url(url_time)
        nc=netCDF4.Dataset(url)
        lons=nc.variables['lon_rho'][:]
        lats=nc.variables['lat_rho'][:]
        temp=nc.variables['temp']
        doppio_time=nc.variables['time']
        doppio_depth=nc.variables['h'][:]
        min_diff_time=abs(datetime.datetime(2017,11,1,0,0,0)+datetime.timedelta(hours=int(doppio_time[0]))-date_time)
        min_diff_index=0
        for i in range(1,157): # 6.5 days and 24
            diff_time=abs(datetime.datetime(2017,11,1,0,0,0)+datetime.timedelta(hours=int(doppio_time[i]))-date_time)
            if diff_time<min_diff_time:
                min_diff_time=diff_time
                min_diff_index=i
                
        min_distance=dist(lat1=lat,lon1=lon,lat2=lats[0][0],lon2=lons[0][0])
        index_1,index_2=0,0
        for i in range(len(lons)):
            for j in range(len(lons[i])):
                if min_distance>dist(lat1=lat,lon1=lon,lat2=lats[i][j],lon2=lons[i][j]):
                    min_distance=dist(lat1=lat,lon1=lon,lat2=lats[i][j],lon2=lons[i][j])
                    index_1=i
                    index_2=j
        if depth==99999:# case of bottom
            S_coordinate=1
        else:
            S_coordinate=float(depth)/float(doppio_depth[index_1][index_2])
        if 0<=S_coordinate<1:
            point_temp=temp[min_diff_index][39-int(S_coordinate/0.025)][index_1][index_2]# because there are 0.025 between each later
        elif S_coordinate==1:
            point_temp=temp[min_diff_index][0][index_1][index_2]
        else:
            return 9999
        if np.isnan(point_temp):
            continue
        if min_diff_time<datetime.timedelta(hours=1):
            break
    return point_temp
#
################
# MAIN PROGRAM

print 'looking for DOPPIO temp'
#modt_doppio=str(round(c2f(get_doppio(lat=df1[8][-1:].values[0],lon=df1[7][-1:].values[0],depth=9999,time=max(df1.datet).to_pydatetime())))) # this is what it looks like in "getlastfix.py"
modt_doppio=get_doppio(lat=lat1,lon=lon1,depth=depth1,time=date1)
print round(modt_doppio,2),round(c2f(modt_doppio)[0],2)

