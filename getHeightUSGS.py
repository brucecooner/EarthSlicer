import requests

#  -----------------------------------------------------------------
# gets height of point in lat,long from USGS point query service
# for some reason the api uses x,y insead of long,lat
# expects length 2 array: lat_long_arr = [lat,long]
def getHeightUSGS(lat_long_arr):
	api_url = f"https://epqs.nationalmap.gov/v1/json?x={lat_long_arr[1]}&y={lat_long_arr[0]}&wkid=4326&units=Feet&includeDate=false"

	# print(api_url)

	api_response = requests.get(api_url)
	response_json = api_response.json()

	# print(response_json)
	# print(response_json.keys())

	return response_json["value"]
