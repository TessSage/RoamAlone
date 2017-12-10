import urllib.request, os
import json

class Points():
	def __init__(self,lat1=0,long1=0,lat2=0,long2=0):
		self.Key = key='AIzaSyCUsBnRueSQcjBWCLAxfiYcwsjsr1qaAsc'
		self.url = r'https://maps.googleapis.com/maps/api/directions/json?'
		self.parameters = ''
		self.originLat=lat1
		self.originLong=long1
		self.destLat=lat2
		self.destLong=long2
		self.encodedPoints = ''
	
	def format_url(self,lat1=0,long1=0,lat2=0,long2=0):
		if lat1==0:
			# use initialized parameters
			self.parameters = 'origin=' + str(self.originLat) + ',' + str(self.originLong)
			self.parameters += '&destination=' + str(self.destLat) + ',' + str(self.destLong)
		else:
			self.parameters = 'origin='+str(lat1) + ','+str(long1)
			self.parameters += 'destination='+str(lat2) + ','+str(long2)


		self.parameters += '&mode=bicycling'+'&key='+self.Key
		self.url += self.parameters

	def request_points(self):
		req = urllib.request.Request(self.url)
		i=0
		with urllib.request.urlopen(req) as f:
			x = (f.read().decode('utf-8'))
			i +=1
		obj = json.loads(x)
		self.encodedPoints = obj['routes'][0]['overview_polyline']['points']
