import time
import requests

import jsons

from Slice import SliceDirection
from SliceRender import slicesToSVG
from TopoSlices import TopoSlices

# Notes:
#			* It's useful to remember that coordinates are written latitude,longitude
#			* Also, think of the "steps" as existing between the numbers, instead of the numbers themselves.
#					i.e. You take a "step" to get to the next number.

#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
# TODO:
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
#	* config: optional trace
#	* config: silent running
#	* config: save slices to file
#	* config: slice output length
# 	* config input EVERYTHING
# 	* config:input: validate inputs
# 
#	* iterative output w/ optional trace

#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
# VERSION
#  -----------------------------------------------------------------
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
	"slice_direction" : SliceDirection.NorthSouth,
	"num_NS_steps" : 4,
	"num_WE_steps" : 3,
	"north_edge" : 33.9613461003105,
	"west_edge" : -111.45394254239501,
	"south_edge" : 33.88319885879201,
	"east_edge" : -111.35075475268964,

	# system concerns
	"use_concurrency" : True,

	# svg concerns
	"slice_svg_length_inches" : 10,
	"vertical_scale" : 1,
	"svg_filename" : "TopoVSlicerPyTest"
}

# Mt. Ord:
# north west: 33.9613461003105, -111.45394254239501
# south east: 33.88319885879201, -111.35075475268964

#  -----------------------------------------------------------------
# system config
report_timings = 0


#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
# TYPES
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
class TTrace:
	def __init__(self, timer_name):
		self.trace_name = timer_name
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
		string_rep = f"Timer: {self.trace_name}  (total_time:{self.total_time()})\n"
		for cur_timing in self.timings:
			string_rep += f"\t{cur_timing['name']} : {cur_timing['time']}\n"
		return string_rep


#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
# CONSTANTS
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
FILE_KEY_APP = "app"
FILE_KEY_TOPOSLICES = "topo_slices"

#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
#	FUNCTIONS
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
def printConfiguration(config_to_print):
	print("config:")
	for (k,v) in config_to_print.items():
		print(f"\t{k} : {v}")

#  -----------------------------------------------------------------
# gets height of point in lat,long from USGS point query service
# for some reason the api uses x,y insead of long,lat
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
def getAppInfo():
	return {
		"name" : "TopoVSlicer",
		"version" : f"{MajorVersion}.{MinorVersion}"
	}

#  -----------------------------------------------------------------
def saveToFile(filename, topo_slices):

	# compose
	file_data_obj = { 
		FILE_KEY_APP : getAppInfo(),
		FILE_KEY_TOPOSLICES : topo_slices.toDataObj()
	}

	with open(filename, "wt") as file_obj:
		file_obj.write(jsons.dumps(file_data_obj, {"indent":3}))

#  -----------------------------------------------------------------
def loadFromFile(filename):
		raw_data = ""
		with open(filename, "rt") as file_obj:
			raw_data = file_obj.read()

		file_data_obj = jsons.loads(raw_data)

		topo_slices = TopoSlices()
		topo_slices.fromDataObj(file_data_obj[FILE_KEY_TOPOSLICES])

		return topo_slices

#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
# MAIN (FUNC)
#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
def main_func():
	print()
	print(f"==================== TopoVSlicer-Py ({MajorVersion}.{MinorVersion}) ====================")
	print()

	main_timer = TTrace("TopoVSlicerPy")
	main_timer.start()

	#  --------------
	# CONFIGURATION
	#  --------------
	# begin with defaults
	main_config = { k: v for (k,v) in default_config.items()}

	print("TODO: gather input config")

	printConfiguration(main_config)

	main_timer.mark("gather/print configuration")

	#  --------------
	# BEGIN WORK
	#  --------------
	main_slices = TopoSlices()

	save_filename = "test_tsv.tsv"

	print("loading from file: " + save_filename)
	main_slices = loadFromFile(save_filename)

	main_timer.mark("load from file")

	print("\nloaded...\n")
	print(main_slices)

	# main_slices.generateSlices(main_config)
	# main_timer.mark("generate slices")

	# main_slices.generateElevations(getHeight, main_config["use_concurrency"])
	# main_timer.mark("generate elevations")

	# print("generated:")
	# print(main_slices)

	# print("saving to file: " + save_filename)
	# saveToFile(save_filename, main_slices)

	# main_timer.mark("save to file")


	# print(main_slices)

	# one refactor at a time plz
	print("generating svg...")
	slicesToSVG(main_slices, main_config)
	main_timer.mark("generate svg")

	if report_timings:
		print()
		print(main_timer)


#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
# MAIN (ENTRY)
#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
if __name__ == '__main__':
	main_func()
