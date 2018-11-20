# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 11:27:15 2018

Draw contours and isothermal layers on the map


@author: leizhao
"""
import os
import conda
conda_file_dir = conda.__file__
conda_dir = conda_file_dir.split('lib')[0]
proj_lib = os.path.join(os.path.join(conda_dir, 'share'), 'proj')
os.environ["PROJ_LIB"] = proj_lib
from mpl_toolkits.basemap import Basemap,cm
import matplotlib.pyplot as plt
import netCDF4
import datetime
import zlconvertions as zl

#HARDCODES
date_time='2018-11-12 12:00:00'
S_coordinate=0.2 #the value is [0,1]
#########################
date_time=datetime.datetime.strptime(date_time,'%Y-%m-%d %H:%M:%S') # transform time format
#find index of the nearest time about data
for i in range(0,7):
    url_time=(date_time-datetime.timedelta(hours=i)).strftime('%Y-%m-%d')#
    url=zl.get_doppio_url(url_time)
    #get the data 
    nc=netCDF4.Dataset(url)
    lons=nc.variables['lon_rho'][:]
    lats=nc.variables['lat_rho'][:]
    temp=nc.variables['temp']
    ocean_time=nc.variables['ocean_time']
    doppio_time=nc.variables['time']
    depth=nc.variables['h'][:]
    min_diff_time=abs(datetime.datetime(2017,11,1,0,0,0)+datetime.timedelta(hours=int(doppio_time[0]))-date_time)
    min_diff_index=0
    for i in range(1,157):
        diff_time=abs(datetime.datetime(2017,11,1,0,0,0)+datetime.timedelta(hours=int(doppio_time[i]))-date_time)
        if diff_time<min_diff_time:
            min_diff_time=diff_time
            min_diff_index=i
    if min_diff_time<datetime.timedelta(hours=1):
        break
 
#caculate the minmum of lat and lon and maximum of lat and lon
min_lat,max_lat,min_lon,max_lon=lats[0][0],lats[0][0],lons[0][0],lons[0][0]
for i in range(len(lons)):
    if min(lats[i])<min_lat:
        min_lat=min(lats[i])
    if min(lons[i])<min_lon:
        min_lon=min(lons[i])
    if max(lats[i])>max_lat:
        max_lat=max(lats[i])
    if max(lons[i])>max_lon:
        max_lon=max(lons[i])

#creat map
#Create a blank canvas       
fig=plt.figure(figsize=(8,8))
ax=fig.add_axes([0.1,0.1,0.9,0.9])
#Build a map background
map=Basemap(llcrnrlat=min_lat,urcrnrlat=max_lat,llcrnrlon=min_lon,urcrnrlon=max_lon,\
            resolution='i',projection='tmerc',lat_0=(max_lat+min_lat)/2,lon_0=(max_lon+min_lon)/2)
map.drawmapboundary(fill_color='aqua')
map.fillcontinents(color='coral',lake_color='white')
map.drawcoastlines()
map.drawstates()

#Draw contour lines and temperature maps
lon,lat=map(lons,lats)
clevs=[0,5,10,15,20,30,40,50,70,100,150,200,250,300,400,500,600,750,1000,2000,3000,4000]
dept_clevs=[10,20,40,80,200,500,1000,2000,4000]
dept_cs=map.contour(lon,lat,depth,dept_clevs,colors='black',linewith=0.5)
plt.clabel(dept_cs, inline = True, fontsize = 10)
temp_cs=map.contourf(lon,lat,temp[min_diff_index][int(S_coordinate/0.025)],8,cmap=cm.s3pcpn)
temp_cbar=map.colorbar(temp_cs,location='top',pad="5%")
temp_cbar.set_label('c')
plt.show()
fig.savefig(out_png_path, format='png', dpi=300, pad_inches = 0)
