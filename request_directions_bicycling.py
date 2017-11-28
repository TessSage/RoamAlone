import urllib.request, os
import json
# for i in Tests:
key='AIzaSyCHlfN7dKzFkNpujq8wRoDNHRJNJYq37Z8 '
# url = r'https://maps.googleapis.com/maps/api/streetview?size=600x300&location=46.414382,10.013988&heading=151.78&pitch=-0.76&key=' + key
  # GetStreet(Add=i,SaveLoc=myloc)

save_location = r'/home/pi/RoamAlone/DummyData/test.json'
elevation_api_key='AIzaSyACBYdD8Ebw2qkdFXfP2fL6agJV1gVP7jM'
maps_key = 'AIzaSyCUsBnRueSQcjBWCLAxfiYcwsjsr1qaAsc'
# url = r'https://maps.googleapis.com/maps/api/elevation/json?locations=39.7391536,-104.9847034&key='+elevation_api_key
latitude = '39.100144'
longitude = '-76.461668'

lat2='39.111492'
long2='-76.499863'
parameters=(latitude) + ','+(longitude) +'&destination='+lat2+','+long2
parameters = parameters + '&mode=bicycling'+'&key='+maps_key
url = r'https://maps.googleapis.com/maps/api/directions/json?origin=' +parameters
print(url)
answer = urllib.request.urlretrieve(url, save_location)
print(answer)
