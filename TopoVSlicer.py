import time
import requests

# import svgwrite

from Slice import SliceDirection, Slice
from svg import sliceToSVG


# Notes:
#			* It's useful to remember that coordinates are written latitude,longitude
#			* Also, think of the "steps" as existing between the numbers, instead of the numbers themselves.
#					i.e. You take a "step" to get to the next number.

#  -----------------------------------------------------------------
# TODO:
#	Config:
# 	* input:
#		rect edges
#		slice direction
#		input num steps (both ways)
#		vertical scale
#	* validate inputs
#	
# TO_DONE:
#	* figure out how to install svgwriter or produce own module


#  -----------------------------------------------------------------
# VERSION
#  -----------------------------------------------------------------
MajorVersion = 0
MinorVersion = 1

#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
# DEFAULTS
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
default_config = {
	# slicer concerns
	"slice_dir" : SliceDirection.NorthSouth,
	"num_NS_steps" : 10,
	"num_EW_steps" : 10	,
	"vertical_scale" : 1,
	"north_edge" : 33.9613461003105,
	"west_edge" : -111.45394254239501,
	"south_edge" : 33.88319885879201,
	"east_edge" : -111.35075475268964,

	# svg concerns
	"output_svg_basename" : "TopoVSlicerPyTest"
}

# Mt. Ord:
# north west: 33.9613461003105, -111.45394254239501
# south east: 33.88319885879201, -111.35075475268964

#  -----------------------------------------------------------------
# system config
report_timings = 1


#  -----------------------------------------------------------------
# TYPES
#  -----------------------------------------------------------------
class Timer:
	def __init__(self, timer_name):
		self.timer_name = timer_name
		self.timings = []

	def start(self):
		self.last_mark = time.perf_counter()

	def mark(self, timing_name):
		mark_time = time.perf_counter()
		new_timing = {"name":timing_name, "time":mark_time - self.last_mark }
		self.timings.append(new_timing)
		self.last_mark = mark_time

	def total_time(self):
		return sum((cur_timing["time"] for cur_timing in self.timings), 0)

	def __repr__(self) -> str:
		string_rep = f"Timer: {self.timer_name}  (total_time:{self.total_time()})\n"
		for cur_timing in self.timings:
			string_rep += f"\t{cur_timing['name']} : {cur_timing['time']}\n"
		return string_rep



#  -----------------------------------------------------------------
def printConfiguration(config_to_print):
	print("config:")
	for (k,v) in config_to_print.items():
		print(f"\t{k} : {v}")

# -----------------------------------------------------------------
# returns step
def calcStep( start, end, num_steps):
	diff = end - start

	step = diff / (num_steps)

	return step

#  -----------------------------------------------------------------
# def sliceLine(start_x, start_y, end_x, end_y, num_steps):
# 	points = []

# 	x_diff = end_x - start_x
# 	y_diff = end_y - start_y

# 	x_step = x_diff / (num_steps)
# 	y_step = y_diff / (num_steps)

# 	cur_x = start_x
# 	cur_y = start_y

# 	# think of the "steps" as existing between the numbers, instead of the numbers themselves
# 	for cur_step in range(num_steps + 1):
# 		points.append( [cur_x,cur_y] )
# 		cur_x += x_step
# 		cur_y += y_step

# 	return points

#  -----------------------------------------------------------------
# gets height of point in lat,long from USGS point query service
# for some reason the api uses x,y insead of long,lat
# def getHeight(lat, long):
# 	api_url = f"https://epqs.nationalmap.gov/v1/json?x={long}&y={lat}&wkid=4326&units=Feet&includeDate=false"

# 	# print(api_url)

# 	api_response = requests.get(api_url)
# 	response_json = api_response.json()

# 	# print(response_json)
# 	# print(response_json.keys())

# 	return response_json["value"]

# expects length 2 array: lat_long_arr = [lat,long]
def getHeight(lat_long_arr):
	api_url = f"https://epqs.nationalmap.gov/v1/json?x={lat_long_arr[1]}&y={lat_long_arr[0]}&wkid=4326&units=Feet&includeDate=false"

	# print(api_url)

	api_response = requests.get(api_url)
	response_json = api_response.json()

	# print(response_json)
	# print(response_json.keys())

	return response_json["value"]


#  -----------------------------------------------------------------
def generateSlices(config):
	slices  = []

	# some messy looping shit, hey i drunk now, back off
	if config["slice_dir"] == SliceDirection.NorthSouth:
		# travel west -> east, taking those delicious north/south slices
		# so start lat and end lat are constant over the everything
		current_long = config["west_edge"]
		long_step = calcStep(config["west_edge"], config["east_edge"], config["num_EW_steps"])

		for current_step in range(config["num_EW_steps"] + 1):
			# do some shit
			current_slice = Slice(	config["north_edge"], current_long,
											config["south_edge"], current_long,
											config["num_NS_steps"],
											config["slice_dir"]);
			current_slice.generatePoints() 

			slices.append(current_slice)
			current_long += long_step
	else:
		# slicing west/east
		# so traveling north -> south, taking w/e slices
		current_lat = config["north_edge"]
		lat_step = calcStep(config["north_edge"], config["south_edge"], config["num_NS_steps"])

		for current_step in range(config["num_NS_steps"] + 1):
			current_slice = Slice(	current_lat, config["west_edge"],
											current_lat, config["east_edge"],
											config["num_EW_steps"],
											config["slice_dir"])
			current_slice.generatePoints()
			
			slices.append(current_slice)
			current_lat += lat_step

	return slices

#  ----------------------------------------------------------------------------
# MAIN (FUNC)
#  ----------------------------------------------------------------------------
def main_func():
	print()
	print(f"==================== TopoVSlicer-Py ({MajorVersion}.{MinorVersion}) ====================")
	print()

	main_timer = Timer("TopoVSlicerPy")
	main_timer.start()

	#  --------------
	# CONFIGURATION
	#  --------------
	# begin with defaults
	main_config = { k: v for (k,v) in default_config.items()}


	print("TODO: gather input config")


	#  --------------
	# easy to debug points
	# main_config["north_edge"] = 10
	# main_config["south_edge"] = 0
	# main_config["num_NS_steps"] = 10

	# main_config["west_edge"] = 10
	# main_config["east_edge"] = 0
	# main_config["num_EW_steps"] = 10

	# test east west
	# main_config["slice_dir"] = SliceDirection.WestEast

	printConfiguration(main_config)

	main_timer.mark("configuration")

	#  --------------
	# BEGIN WORK
	#  --------------
	main_slices = generateSlices(main_config)

	main_timer.mark("generate slices")

	# for cur_slice in main_slices:
	main_slices[0].set_use_concurrency()
	# main_slices[0].generateElevations(getHeight)

	main_timer.mark("generate elevations")

	# DEBUGGING, DEVELOPMENT, ETC.
	print(main_slices[0])

	sliceToSVG(main_slices[0], main_config)
	# for cur_slice in main_slices:
	# 	print(cur_slice)

	if report_timings:
		print()
		print(main_timer)


#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
# MAIN (SCRIPT)
#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
if __name__ == '__main__':
	main_func()
