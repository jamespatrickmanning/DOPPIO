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
        except:
            continue
        lons=nc.variables['lon_rho'][:]
        lats=nc.variables['lat_rho'][:]
        temp=nc.variables['temp']
        doppio_time=nc.variables['time']
        doppio_depth=nc.variables['h'][:]
        min_diff_time=abs(datetime.datetime(2017,11,1,0,0,0)+datetime.timedelta(hours=int(doppio_time[0]))-date_time)
        min_diff_index=0
        for i in range(1,len(doppio_time)):
            diff_time=abs(datetime.datetime(2017,11,1,0,0,0)+datetime.timedelta(hours=int(doppio_time[i]))-date_time)
            if diff_time<min_diff_time:
                min_diff_time=diff_time
                min_diff_index=i
        #calculate the min,second small and third small distance and index
        min_distance=zl.dist(lat1=lat,lon1=lon,lat2=lats[0][0],lon2=lons[0][0])
#        secondmin_distance=min_distance
#        thirdmin_distance=min_distance
#        
        index_1,index_2=0,0
        secondindex_1,secondindex_2=0,0
        thirdindex_1,thirdindex_2=0,0
        fourthindex_1,fourthindex_2=0,0
        fifthindex_1,fifthindex_2=0,0
#        sixthindex_1,sixthindex_2=0,0
        for i in range(len(lons)):
            for j in range(len(lons[i])):
                distance=zl.dist(lat1=lat,lon1=lon,lat2=lats[i][j],lon2=lons[i][j])
                if min_distance>=distance:
#                    thirdmin_distance=secondmin_distance
#                    secondmin_distance=min_distance
                    min_distance=distance
#                    sixthindex_1,sixthindex_2=fifthindex_1,fifthindex_2
                    fifthindex_1,fifthindex_2=fourthindex_1,fourthindex_2
                    fourthindex_1,fourthindex_2=thirdindex_1,thirdindex_2
                    thirdindex_1,thirdindex_2=secondindex_1,secondindex_2
                    secondindex_1,secondindex_2=index_1,index_2
                    index_1,index_2=i,j
                    
        
       
        if depth==99999:
            S_coordinate=1
        else:
            S_coordinate=float(depth)/float(doppio_depth[index_1][index_2])
        if 0<=S_coordinate<1:
            layer_index=39-int(S_coordinate/0.025)
        elif S_coordinate==1:
            layer_index=39
        else:
            return 9999
        point=[[lats[index_1][index_2],lons[index_1][index_2],temp[min_diff_index][layer_index][index_1][index_2]],\
            [lats[secondindex_1][secondindex_2],lons[secondindex_1][secondindex_2],temp[min_diff_index][layer_index][secondindex_1][secondindex_2]],\
            [lats[thirdindex_1][thirdindex_2],lons[thirdindex_1][thirdindex_2],temp[min_diff_index][layer_index][thirdindex_1][thirdindex_2]],\
            [lats[fourthindex_1][fourthindex_2],lons[fourthindex_1][fourthindex_2],temp[min_diff_index][layer_index][fourthindex_1][fourthindex_2]],\
            [lats[fifthindex_1][fifthindex_2],lons[fifthindex_1][fifthindex_2],temp[min_diff_index][layer_index][fifthindex_1][fifthindex_2]]]
        point_temp=fitting(point,lat,lon)
        if np.isnan(point_temp):
            continue
        if min_diff_time<datetime.timedelta(hours=1):
            break
    return point_temp,index_1,index_2

def fitting(point,lat,lon):

#表示矩阵中的值
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

# 进行矩阵运算
# _mat1 设为 mat1 的逆矩阵
    m1=[[ISum,X1Sum,X2Sum],[X1Sum,X1_2Sum,X1X2Sum],[X2Sum,X1X2Sum,X2_2Sum]]
    mat1 = np.matrix(m1)
    m2=[[YSum],[X1YSum],[X2YSum]]
    mat2 = np.matrix(m2)
    _mat1 =mat1.getI()
    mat3 = _mat1*mat2

# 用list来提取矩阵数据
    m3=mat3.tolist()
    a0 = m3[0][0]
    a1 = m3[1][0]
    a2 = m3[2][0]
    y = a0+a1*lat+a2*lon

    return y