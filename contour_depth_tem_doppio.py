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
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import netCDF4
import datetime
import zlconversions as zl
import doppio_modules as dm
import numpy as np
#HARDCODES
input_date_time='2018-11-11 12:00:00'
input_lat=41.784712
input_lon=-69.231081
input_depth=0   #If you enter 99999, the default output bottom temperature,enter 0 will output the temperature of surface
output_path='/home/jmanning/Desktop/testout/doppio/'
#########################
date_time=datetime.datetime.strptime(input_date_time,'%Y-%m-%d %H:%M:%S') # transform time format
#find index of the nearest time about data
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

if (max_lon-min_lon)>(max_lat-min_lat):
    max_lat=max_lat+((max_lon-min_lon)-(max_lat-min_lat))/2.0
    min_lat=min_lat-((max_lon-min_lon)-(max_lat-min_lat))/2.0
else:
    max_lon=max_lon+((max_lat-min_lat)-(max_lon-min_lon))/2.0
    min_lon=min_lon-((max_lat-min_lat)-(max_lon-min_lon))/2.0
point_temp,index_1,index_2=dm.get_doppio(lat=input_lat,lon=input_lon,depth=input_depth,time=input_date_time)
if input_depth==99999:   #if input_depth=99999, we need output the bottom layer
    S_coordinate=1   #1 represent the bottom layer, 0 represent the surface layer
else:
    S_coordinate=float(input_depth)/float(doppio_depth[index_1][index_2])

#creat map
#Create a blank canvas       
fig=plt.figure(figsize = (20, 20))
fig.suptitle('DOPPIO model bottom temp(deg C) ',fontsize=24, fontweight='bold')

#Draw contour lines and temperature maps in detail
ax1=fig.add_axes([0.02,0.02,0.9,0.9])
service = 'Ocean_Basemap'
map=Basemap(llcrnrlat=input_lat-0.3,urcrnrlat=input_lat+0.3,llcrnrlon=input_lon-0.3,urcrnrlon=input_lon+0.3,\
            resolution='f',projection='tmerc',lat_0=input_lat,lon_0=input_lon,epsg = 4269)
map.arcgisimage(service=service, xpixels = 5000, verbose= False)

#label the latitude and longitude
parallels = np.arange(0.,90,0.1)
map.drawparallels(parallels,labels=[1,0,0,0],fontsize=25,linewidth=0.0)
# draw meridians
meridians = np.arange(180.,360.,0.1)
map.drawmeridians(meridians,labels=[0,0,0,1],fontsize=25,linewidth=0.0)
lon,lat=map(lons,lats)
dept_clevs=range(0,1000,10)
dept_cs=map.contour(lon,lat,doppio_depth,dept_clevs,colors='black')
plt.clabel(dept_cs, inline = True, fontsize =20,fmt="%1.0f")
if 0<=S_coordinate<1:
    temp_cs=map.contourf(lon,lat,temp[min_diff_index][39-int(S_coordinate/0.025)],7)#,cmap=cm.StepSeq)
elif S_coordinate==1:
    temp_cs=map.contourf(lon,lat,temp[min_diff_index][39],7)#,cmap=cm.StepSeq)
else:
    print ("the depth is out of the depth of bottom")
temp_cbar=map.colorbar(temp_cs,location='right',pad="1%")
#temp_cbar.tick_params(labelsize=25)
#plt.rcParams['font.family'] = 'Times New Roman'
#plt.rcParams['font.size'] = 20
#for l in temp_cbar.ax.yaxis.get_ticklabels():
#    l.set_family('Times New Roman')
temp_cbar.set_label('unit:C',size=25)
if point_temp==9999:
    citys=['the depth is out of the bottom depth']
else:
    citys=[str(round(point_temp,2))]
lat_point=[input_lat]
lon_point=[input_lon]
x,y=map(lon_point,lat_point)
plt.plot(x,y,'ro')
plt.text(x[0]+0.02,y[0]-0.01,citys[0],bbox=dict(facecolor='yellow',alpha=0.5),fontsize =30)

ax2=fig.add_axes([0.06,0.7,0.2,0.2])
#Build a map background
map1=Basemap(llcrnrlat=int(min_lat),urcrnrlat=int(max_lat)+1,llcrnrlon=int(min_lon),urcrnrlon=int(max_lon)+1,\
            resolution='f',projection='tmerc',lat_0=(max_lat+min_lat)/2,lon_0=(max_lon+min_lon)/2,epsg = 4269)
map1.arcgisimage(service=service, xpixels = 5000, verbose= False)

# draw parallels.
if 6>=max_lat-min_lat>2:
    step=1
elif max_lat-min_lat>6:
    step=int((max_lat-min_lat)/5)
else:
    step=0.5
parallels = np.arange(0.,90.,step)
map1.drawparallels(parallels,labels=[1,0,0,0],fontsize=10,linewidth=0.0)
# draw meridians
meridians = np.arange(180.,360.,step)
map1.drawmeridians(meridians,labels=[0,0,0,1],fontsize=10,linewidth=0.0)
x,y=map1(lon_point,lat_point)
#Draw contour lines and temperature maps
#drawcontour lines od depth 
plt.plot(x,y,'ro')
plt.savefig(output_path+'contour_depth_tem_doppio2.png',dpi=300)
plt.show()