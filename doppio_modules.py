#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 09:10:47 2018


feb27 2019
update the method of calculate the layer_index in function of get doppio
March 6 2019
update the method of calculate the nearest point with point
@author: jmanning
"""

import netCDF4
import datetime
import zlconversions as zl
import numpy as np

def get_doppio(lat=0,lon=0,depth=99999,time='2018-11-12 12:00:00'):
    """
    notice:
        the format of time is like "%Y-%m-%d %H:%M:%S"
        the depth is under the bottom depth
    the module only output the temperature of point location
    """
    date_time=datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S') # transform time format
    for m in range(0,7):
        try:
            url_time=(date_time-datetime.timedelta(days=m)).strftime('%Y-%m-%d')#
            url=zl.get_doppio_url(url_time)
            #get the data 
            nc=netCDF4.Dataset(url)
            lons=nc.variables['lon_rho'][:]
            lats=nc.variables['lat_rho'][:]
            temp=nc.variables['temp']
            doppio_time=nc.variables['time']
            doppio_depth=nc.variables['h'][:]
            doppio_rho=nc.variables['s_rho'][:]
        except:
            continue
        min_diff_time=abs(datetime.datetime(2017,11,1,0,0,0)+datetime.timedelta(hours=int(doppio_time[0]))-date_time)
        min_diff_index=0
        for i in range(1,len(doppio_time)):
            diff_time=abs(datetime.datetime(2017,11,1,0,0,0)+datetime.timedelta(hours=int(doppio_time[i]))-date_time)
            if diff_time<min_diff_time:
                min_diff_time=diff_time
                min_diff_index=i
        #calculate the min,second small and third small distance and index
        target_distance=zl.dist(lat1=lats[0][0],lon1=lons[0][0],lat2=lats[0][1],lon2=lons[0][1])
        index_1,index_2=zl.find_nd(target=target_distance,lat=lat,lon=lon,lats=lats,lons=lons)

        #calculate the optimal layer index
        h_distance=depth+doppio_rho[0]*doppio_depth[index_1][index_2]  #specify the initial distanc of high
        layer_index=0  #specify the initial layer index        
        for i in range(len(doppio_rho)):
            if abs(depth+doppio_rho[0]*doppio_depth[index_1][index_2])<=h_distance:
                h_distance=depth+doppio_rho[i]*doppio_depth[index_1][index_2]
                layer_index=i
        if depth>doppio_depth[index_1][index_2]:
            print ("the depth is out of the depth of bottom:"+str(doppio_depth[index_1][index_2]))
        if index_1==0:
            index_1=1
        if index_1==len(lats)-1:
            index_1=len(lats)-2
        if index_2==0:
            index_2=1
        if index_2==len(lats[0])-1:
            index_2=len(lats[0])-2
        point=[[lats[index_1][index_2],lons[index_1][index_2],temp[min_diff_index][layer_index][index_1][index_2]],\
            [lats[index_1-1][index_2],lons[index_1-1][index_2],temp[min_diff_index][layer_index][index_1-1][index_2]],\
            [lats[index_1+1][index_2],lons[index_1+1][index_2],temp[min_diff_index][layer_index][index_1+1][index_2]],\
            [lats[index_1][index_2-1],lons[index_1][index_2-1],temp[min_diff_index][layer_index][index_1][index_2-1]],\
            [lats[index_1][index_2+1],lons[index_1][index_2+1],temp[min_diff_index][layer_index][index_1][index_2+1]]]

        point_temp=fitting(point,lat,lon)
        print(point_temp)

        if np.isnan(point_temp):
            continue
        if min_diff_time<datetime.timedelta(hours=1):
            break
    return point_temp,layer_index

def fitting(point,lat,lon):

#represent the value of matrix
    ISum = 0.0
    X1Sum = 0.0
    X2Sum = 0.0
    X1_2Sum = 0.0
    X1X2Sum = 0.0
    X2_2Sum = 0.0
    YSum = 0.0
    X1YSum = 0.0
    X2YSum = 0.0

    for i in range(0,len(point)):
        
        x1i=point[i][0]
        x2i=point[i][1]
        yi=point[i][2]

        ISum = ISum+1
        X1Sum = X1Sum+x1i
        X2Sum = X2Sum+x2i
        X1_2Sum = X1_2Sum+x1i**2
        X1X2Sum = X1X2Sum+x1i*x2i
        X2_2Sum = X2_2Sum+x2i**2
        YSum = YSum+yi
        X1YSum = X1YSum+x1i*yi
        X2YSum = X2YSum+x2i*yi

#  matrix operations
# _mat1 is the mat1 inverse matrix
    m1=[[ISum,X1Sum,X2Sum],[X1Sum,X1_2Sum,X1X2Sum],[X2Sum,X1X2Sum,X2_2Sum]]
    mat1 = np.matrix(m1)
    m2=[[YSum],[X1YSum],[X2YSum]]
    mat2 = np.matrix(m2)
    _mat1 =mat1.getI()
    mat3 = _mat1*mat2

# use list to get the matrix data
    m3=mat3.tolist()
    a0 = m3[0][0]
    a1 = m3[1][0]
    a2 = m3[2][0]
    y = a0+a1*lat+a2*lon

    return y

