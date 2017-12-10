import PointClass
import urllib.request, os
import json
import math

lat1=input('Input origin latitude: ')#39.2673765
long1=input('Input origin longitude: ')#-76.7927129


lat2=input('Input destination latitude: ')#39.260154
long2=input('Input destination longitude: ')#-76.81309104

points = PointClass.Points(lat1,long1,lat2,long2)

points.format_url()
print(points.url)
points.request_points()
print(points.encodedPoints)

from URLGeneratingFunctions import decode, distance, calculate_initial_compass_bearing, PE

latlongpairs = decode(points.encodedPoints)

url_list=[]
myinfolist = []
url_base = 'https://maps.googleapis.com/maps/api/streetview?'
STREETVIEW_KEY = 'AIzaSyCHlfN7dKzFkNpujq8wRoDNHRJNJYq37Z8'

file = input('please enter file name for url list generated without the file extension.') + '.txt'
f = open(file, 'w')
WHEEL_CIR = 7/3.28 # circumference in feet converted to meters

correct_dis_latlong=[]

for i in range(0, len(latlongpairs)-1):
	dis =distance(latlongpairs[i][0],latlongpairs[i][1],latlongpairs[i+1][0],latlongpairs[i+1][1])
	if dis >= 1.05*WHEEL_CIR or dis <= 0.95*WHEEL_CIR:
	
		factor = round(dis/WHEEL_CIR)
		if factor > 4:
			factor = 4
		if factor % 2 ==0:
			tot_pts = factor+1
		else:
			tot_pts = factor
		correct_dis_latlong.append((latlongpairs[i][0],latlongpairs[i][1]))
		midlat = (latlongpairs[i][0]+latlongpairs[i+1][0])/2
		midlong = (latlongpairs[i][1]+latlongpairs[i+1][1])/2
		if tot_pts == 3:
			correct_dis_latlong.append((midlat, midlong))
		else:
			midlat1 = (latlongpairs[i][0]+midlat)/2
			midlong1 = (latlongpairs[i][1]+midlong)/2
			correct_dis_latlong.append((midlat1, midlong1))
			midlat2 = (midlat+latlongpairs[i+1][0])/2
			midlong2 = (midlong+latlongpairs[i+1][1])/2
			correct_dis_latlong.append((midlat, midlong))
			correct_dis_latlong.append((midlat2, midlong2))
correct_dis_latlong.append((latlongpairs[i+1][0],latlongpairs[i+1][1]))


for i in range(0, len(correct_dis_latlong)-1):
    bearing = round(calculate_initial_compass_bearing(correct_dis_latlong[i],correct_dis_latlong[i+1]))
    dis =distance(correct_dis_latlong[i][0],correct_dis_latlong[i][1],correct_dis_latlong[i+1][0],correct_dis_latlong[i+1][1])
    
    elevation1 = PE(correct_dis_latlong[i][0],correct_dis_latlong[i][1]).get_elevation()
    elevation2 = PE(correct_dis_latlong[i+1][0],correct_dis_latlong[i+1][1]).get_elevation()
    elevationgain = elevation2-elevation1
    pitch = round(math.degrees(math.asin(elevationgain/dis)),3) # check units!!
     # lat long distance elevationgain pitch bearing
    myinfolist.append([correct_dis_latlong[i][0],correct_dis_latlong[i][1], dis, elevationgain, pitch, bearing])
    url = url_base + 'location=' + str(round(correct_dis_latlong[i][0],6)) +',' +str(round(correct_dis_latlong[i][1],6))
    url = url + '&heading=' + str(bearing) + '&pitch=' + str(pitch) + '&fov=120&size=600x400' #+'&key='+STREETVIEW_KEY
    f.write(url +';'+str(100*elevationgain/dis) +'\n')
    
myinfolist.append([correct_dis_latlong[i+1][0],correct_dis_latlong[i+1][1],dis, elevationgain, pitch, bearing])
url = url_base + 'location=' + str(round(correct_dis_latlong[i+1][0],6)) +',' +str(round(correct_dis_latlong[i+1][1],6))
url = url + '&heading=' + str(bearing) + '&pitch=' + str(pitch) + '&fov=120&size=600x400' #+ '&key='+STREETVIEW_KEY
f.write(url+';'+str(100*elevationgain/dis)+'\n')
f.close()