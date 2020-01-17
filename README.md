# DOPPIO
There are two routines "get_doppio_test.py" and "get_doppio_test2.py" which access DOPPIO temperatures for a particular time, position, and depth. The latter one uses Lei Zhao's "fitting" method to interpolate multiple nearby nodes put, for the limited test that I made, the interpolation method didn't matter much.  It changed the temps by a few hundredths of a degree.

contour_depth_tem_doppio
Draw contours and isothermal layers on the map
STEP:
step 1: 
Find the file on the date of the input date. If the difference between the time of the data grid and the given time is less than one hour, then the grid with the minimum time difference of the data is used. If the minimum time difference of the data is greater than one hour, then Traverse the previous six days of the file and find data with a time difference of less than 1 hour. If both are greater than 1 hour, this uses the minimum time difference of the set of data grids
step 2:
Use data to find the boundaries of the map
step 3:
Draw isobath and temperature color map
