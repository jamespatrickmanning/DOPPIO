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
import zlconversions as zl
import doppio_modules as dm

#HARDCODES
input_date_time='2018-11-12 12:00:00'
input_lat=41.784712
input_lon=-69.231081
input_depth=0   #If you enter 99999, the default output bottom temperature,enter 0 will output the temperature of surface
output_path='/home/jmanning/Desktop/testout/doppio/'
#########################
date_time=datetime.datetime.strptime(input_date_time,'%Y-%m-%d %H:%M:%S') # transform time format
#find index of the nearest time about data
for i in range(0,7):
    url_time=(date_time-datetime.timedelta(hours=i)).strftime('%Y-%m-%d')#
    url=zl.get_doppio_url(url_time)
    #get the data 
    nc=netCDF4.Dataset(url)
    lons=nc.variables['lon_rho'][:]
    lats=nc.variables['lat_rho'][:]
    temp=nc.variables['temp']
    doppio_time=nc.variables['time']
    doppio_depth=nc.variables['h'][:]
    min_diff_time=abs(datetime.datetime(2017,11,1,0,0,0)+datetime.timedelta(hours=int(doppio_time[0]))-date_time) #Set initial value
    min_diff_index=0  #Set initial value
    for i in range(0,157):
        diff_time=abs(datetime.datetime(2017,11,1,0,0,0)+datetime.timedelta(hours=int(doppio_time[i]))-date_time)
        if diff_time<min_diff_time:
            min_diff_time=diff_time
            min_diff_index=i
    if min_diff_time<datetime.timedelta(hours=1):  #if min_diff_time less 1 hour, out of the loop
        break

#caculate the minmum of lat and lon and maximum of lat and lon, these vaves are the ledge of map
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
#find the nearest point, and record the index 
min_distance=zl.dist(lat1=input_lat,lon1=input_lon,lat2=lats[0][0],lon2=lons[0][0])#set initial value
index_1,index_2=0,0 #set the initial index of min_distance
for i in range(len(lons)):
    for j in range(len(lons[i])):
        if min_distance>zl.dist(lat1=input_lat,lon1=input_lon,lat2=lats[i][j],lon2=lons[i][j]):
            min_distance=zl.dist(lat1=input_lat,lon1=input_lon,lat2=lats[i][j],lon2=lons[i][j])
            index_1=i
            index_2=j
if input_depth==99999:   #if input_depth=99999, we need output the bottom layer
    S_coordinate=1   #1 represent the bottom layer, 0 represent the surface layer
else:
    S_coordinate=float(input_depth)/float(doppio_depth[index_1][index_2])
#caculate the temperature of the point that I want
if 0<=S_coordinate<1:
    point_temp=temp[min_diff_index][39-int(S_coordinate/0.025)][index_1][index_2]
elif S_coordinate==1:
    point_temp=temp[min_diff_index][39][index_1][index_2]
#creat map
#Create a blank canvas       
fig=plt.figure(figsize=(20,20))
ax=fig.add_axes([0.1,0.1,0.85,0.9])
#Build a map background
map=Basemap(llcrnrlat=int(min_lat)-0.3,urcrnrlat=int(max_lat)+1,llcrnrlon=int(min_lon),urcrnrlon=int(max_lon)+1,\
            resolution='i',projection='tmerc',lat_0=(max_lat+min_lat)/2,lon_0=(max_lon+min_lon)/2)
map.drawmapboundary(fill_color='white')
map.fillcontinents(color='coral',lake_color='white')
map.drawcoastlines()
map.drawstates()

#Draw contour lines and temperature maps
#drawcontour lines od depth 
lon,lat=map(lons,lats)
dept_clevs=[10,20,30,40,50,60,70,80,100,300,1000,2000,4000]
dept_cs=map.contour(lon,lat,doppio_depth,dept_clevs,colors='black',linewith=0.3)
plt.clabel(dept_cs, inline = True, fontsize = 10)
#draw the contour of temperature 
if 0<=S_coordinate<1:
    temp_cs=map.contourf(lon,lat,temp[min_diff_index][39-int(S_coordinate/0.025)],15,cmap=cm.StepSeq)
elif S_coordinate==1:
    temp_cs=map.contourf(lon,lat,temp[min_diff_index][39],15,cmap=cm.cm.StepSeq)
else:
    print ("the depth is out of the depth of bottom")
temp_cbar=map.colorbar(temp_cs,location='right',pad="1%")
temp_cbar.set_label('unit:℃')
#calculate the temperature of the point that we need
point_temp=dm.get_doppio(lat=input_lat,lon=input_lon,depth=input_depth,time=input_date_time)
#draw thw point in the map and write the temperature in the lable
lat_point=[input_lat]
lon_point=[input_lon]
x,y=map(lon_point,lat_point)
if point_temp==9999:
    citys=['the depth is out of the bottom depth']
else:
    citys=[str(round(point_temp,2))]
plt.plot(x,y,'ro')
plt.text(x[0]+12500,y[0]-25000,citys[0],bbox=dict(facecolor='yellow',alpha=0.5))
plt.savefig(output_path+'contour_depth_tem_doppio.png',dpi=300)
#plt.show()
