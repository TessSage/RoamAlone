def decode(point_str):
    '''Decodes a polyline that has been encoded using Google's algorithm
    http://code.google.com/apis/maps/documentation/polylinealgorithm.html
    
    This is a generic method that returns a list of (latitude, longitude) 
    tuples.
    
    :param point_str: Encoded polyline string.
    :type point_str: string
    :returns: List of 2-tuples where each tuple is (latitude, longitude)
    :rtype: list
    
    '''
            
    # sone coordinate offset is represented by 4 to 5 binary chunks
    coord_chunks = [[]]
    for char in point_str:
        
        # convert each character to decimal from ascii
        value = ord(char) - 63
        
        # values that have a chunk following have an extra 1 on the left
        split_after = not (value & 0x20)         
        value &= 0x1F
        
        coord_chunks[-1].append(value)
        
        if split_after:
                coord_chunks.append([])
        
    del coord_chunks[-1]
    
    coords = []
    
    for coord_chunk in coord_chunks:
        coord = 0
        
        for i, chunk in enumerate(coord_chunk):                    
            coord |= chunk << (i * 5) 
        
        #there is a 1 on the right if the coord is negative
        if coord & 0x1:
            coord = ~coord #invert
        coord >>= 1
        coord /= 100000.0
                    
        coords.append(coord)
    
    # convert the 1 dimensional list to a 2 dimensional list and offsets to 
    # actual values
    points = []
    prev_x = 0
    prev_y = 0
    for i in range(0, len(coords) - 1, 2):
        if coords[i] == 0 and coords[i + 1] == 0:
            continue
        
        prev_x += coords[i + 1]
        prev_y += coords[i]
        # a round to 6 digits ensures that the floats are the same as when 
        # they were encoded
        points.append((round(prev_y, 6), round(prev_x, 6)))
    
    return points

#my_asc = '_p~iF~ps|U_ulLnnqC_mqNvxq`@'
#mypoints='svsmF`}tqMmDnC_@Nc@H{@Mg@[Wc@_@aAa@i@}@q@c@tBU`BSlBSp@i@~@cHtHaCbCpAhDn@nCn@dETjAFLPrAPvAV|DRdG@|@ApAQbB[tAa@jAaCxEa@|@e@jAi@pBkCnMyAxHS|AItBe@zSEpDB~EHdMG~COpCc@zGI~@_@lC_DdOa@dBm@rBe@bAk@x@kH`IsD`E'
mypoints="svsmF`}tqMmDnC_@Nc@H{@Mg@[Wc@_@aAa@i@}@q@c@tBU`BSlBSp@i@~@cHtHaCbCpAhDn@nCn@dETjAFLPrAPvAV|DRdG@|@ApAQbB[tAa@jAaCxEa@|@e@jAi@pBkCnMyAxHS|AItBe@zSEpDB~EHdMG~COpCc@zGI~@_@lC_DdOa@dBm@rBe@bAk@x@kH`IsD`E"

print(mypoints)
mylatlongpairs = decode(mypoints)
print(mylatlongpairs)

import math
def calculate_initial_compass_bearing(pointA, pointB):
    """
    Calculates the bearing between two points.
    The formulae used is the following:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
    :Parameters:
      - `pointA: The tuple representing the latitude/longitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `pointB: The tuple representing the latitude/longitude for the
        second point. Latitude and longitude must be in decimal degrees
    :Returns:
      The bearing in degrees
    :Returns Type:
      float
    """
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])

    diffLong = math.radians(pointB[1] - pointA[1])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing

def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295     #Pi/180
    a = 0.5 - math.cos((lat2 - lat1) * p)/2 + math.cos(lat1 * p) * math.cos(lat2 * p) * (1 - math.cos((lon2 - lon1) * p)) / 2
    return 12742e3 * math.asin(math.sqrt(a)) #in m

import urllib.request, os
import json

ELEVATION_API_KEY = 'AIzaSyACBYdD8Ebw2qkdFXfP2fL6agJV1gVP7jM'
ELEVATION_URL_BASE = r'https://maps.googleapis.com/maps/api/elevation/json?' 
class PE():
    def __init__(self, latitude, longitude):
        self.Lat = latitude
        self.Long = longitude
        self.Elevation = 0

    def get_elevation(self):
        parameters= 'locations=' + str(self.Lat) + ',' + str(self.Long) + '&key=' + ELEVATION_API_KEY
        url = ELEVATION_URL_BASE +parameters
        req = urllib.request.Request(url)
        i=0
        with urllib.request.urlopen(req) as f:
            x = (f.read().decode('utf-8'))
            i +=1
        obj = json.loads(x)
        self.Elevation = obj['results'][0]['elevation']
        return self.Elevation

    def return_elevation(self):
        return self.Elevation
url_list=[]
myinfolist = []
url_base = 'https://maps.googleapis.com/maps/api/streetview?'
stretview_key = 'AIzaSyCHlfN7dKzFkNpujq8wRoDNHRJNJYq37Z8'

f = open('testing_url_list.txt', 'w')
wheel_cir = 7/3.28 # meters

correct_dis_latlong=[]
for i in range(0, len(mylatlongpairs)-1):
	dis =distance(mylatlongpairs[i][0],mylatlongpairs[i][1],mylatlongpairs[i+1][0],mylatlongpairs[i+1][1])
	if dis >= 1.05*wheel_cir or dis <= 0.95*wheel_cir:
	
		factor = round(dis/wheel_cir)
		if factor > 4:
			factor = 4
		if factor % 2 ==0:
			tot_pts = factor+1
		else:
			tot_pts = factor
		correct_dis_latlong.append((mylatlongpairs[i][0],mylatlongpairs[i][1]))
		midlat = (mylatlongpairs[i][0]+mylatlongpairs[i+1][0])/2
		midlong = (mylatlongpairs[i][1]+mylatlongpairs[i+1][1])/2
		if tot_pts == 3:
			correct_dis_latlong.append((midlat, midlong))
		else:
			midlat1 = (mylatlongpairs[i][0]+midlat)/2
			midlong1 = (mylatlongpairs[i][1]+midlong)/2
			correct_dis_latlong.append((midlat1, midlong1))
			midlat2 = (midlat+mylatlongpairs[i+1][0])/2
			midlong2 = (midlong+mylatlongpairs[i+1][1])/2
			correct_dis_latlong.append((midlat, midlong))
			correct_dis_latlong.append((midlat2, midlong2))
correct_dis_latlong.append((mylatlongpairs[i+1][0],mylatlongpairs[i+1][1]))
			

for i in range(0, len(correct_dis_latlong)-1):
    bearing = round(calculate_initial_compass_bearing(correct_dis_latlong[i],correct_dis_latlong[i+1]))
    #print('bearing',bearing)
    dis =distance(correct_dis_latlong[i][0],correct_dis_latlong[i][1],correct_dis_latlong[i+1][0],correct_dis_latlong[i+1][1])
    #print('distance: ', dis)

    
    elevation1 = PE(correct_dis_latlong[i][0],correct_dis_latlong[i][1]).get_elevation()
    # elevation1 = PE1.return_elevation()
    elevation2 = PE(correct_dis_latlong[i+1][0],correct_dis_latlong[i+1][1]).get_elevation()
    # elevation2 = PE2.return_elevation()
    elevationgain = elevation2-elevation1
    #print('elevation gain', elevationgain)
    pitch = round(math.degrees(math.asin(elevationgain/dis)),3) # check units!!
     # lat long distance elevationgain pitch bearing
    myinfolist.append([correct_dis_latlong[i][0],correct_dis_latlong[i][1], dis, elevationgain, pitch, bearing])
    url = url_base + 'location=' + str(round(correct_dis_latlong[i][0],6)) +',' +str(round(correct_dis_latlong[i][1],6))
    url = url + '&heading=' + str(bearing) + '&pitch=' + str(pitch) + '&fov=120&size=600x400' +'&key='+stretview_key
    f.write(url +';'+str(100*elevationgain/dis) +'\n')
    print(url)
    
myinfolist.append([correct_dis_latlong[i+1][0],correct_dis_latlong[i+1][1],dis, elevationgain, pitch, bearing])
url = url_base + 'location=' + str(round(correct_dis_latlong[i+1][0],6)) +',' +str(round(correct_dis_latlong[i+1][1],6))
url = url + '&heading=' + str(bearing) + '&pitch=' + str(pitch) + '&fov=120&size=600x400' + '&key='+stretview_key
f.write(url+';'+str(100*elevationgain/dis)+'\n')
f.close()
