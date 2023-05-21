import jsons
import os

from LogChannels import LogChannels

from TimingTrace import TimingTrace
from getHeightUSGS import getHeightUSGS

from HeightMap import HeightMap
from getHeightUSGS import getHeightUSGS

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
#	* file stats report

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
	"number_of_elevations" : 10,			# number of elevation points read along a slice (includes first/last)
	"number_of_slices" : 3,					# number of slices taken
	"north_edge" : 33.9613461003105,
	# "west_edge" : -111.45394254239501,
	"west_edge" : -111.411012,
	"south_edge" : 33.88319885879201,
	"east_edge" :  -111.405557, # -111.35075475268964,

	# system concerns
	"use_concurrency" : False,
	"height_map_filename" : "height_map.json",

	# svg concerns
	"slice_svg_length_inches" : 10,
	"vertical_scale" : 1,
	"svg_filename" : "MtOrdTight"
}

# Mt. Ord:
# north west: 33.9613461003105, -111.45394254239501
# south east: 33.88319885879201, -111.35075475268964

# tight box across Mt. Ord:
# west : -111.411012
# east :  -111.405557

#  -----------------------------------------------------------------
# system config
report_timings = True


#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
# TYPES
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------


#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
# CONSTANTS
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
FILE_KEY_APP = "app"
FILE_KEY_TOPOSLICES = "topo_slices"

#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
#	VARIABLES
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
log = LogChannels()
log.addChannel("echo")
log.addChannel("debug", "debug")
log.addChannel("todo", "TODO")
log.addChannel("hmap", "hmap")
log.setChannel("hmap", False)
log.addChannel("Slicer", "Slicer")
log.setChannel("Slicer", False)

main_height_map = HeightMap(name = "MHM", log_fn = log.hmap)

#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
#	FUNCTIONS
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
def printConfiguration(config_to_print, fnPrint):
	fnPrint("config:")
	for (k,v) in config_to_print.items():
		fnPrint(f"\t{k} : {v}")

#  -----------------------------------------------------------------
# def getAppInfo():
# 	return {
# 		"name" : "TopoVSlicer",
# 		"version" : f"{MajorVersion}.{MinorVersion}"
# 	}

# #  -----------------------------------------------------------------
# def saveToFile(filename, topo_slices):
# 	# compose
# 	file_data_obj = { 
# 		FILE_KEY_APP : getAppInfo(),
# 		FILE_KEY_TOPOSLICES : topo_slices.toDataObj()
# 	}

# 	with open(filename, "wt") as file_obj:
# 		file_obj.write(jsons.dumps(file_data_obj, {"indent":3}))

# #  -----------------------------------------------------------------
# def loadFromFile(filename):
# 		raw_data = ""
# 		with open(filename, "rt") as file_obj:
# 			raw_data = file_obj.read()

# 		file_data_obj = jsons.loads(raw_data)

# 		topo_slices = TopoSlices()
# 		topo_slices.fromDataObj(file_data_obj[FILE_KEY_TOPOSLICES])

# 		return topo_slices

#  ----------------------------------------------------------------------------
def loadHeightMapFromFile(filename, height_map):
	# have map file?
	if os.path.isfile(filename):
		log.echo(f'using height map file {filename}')
		raw_data = ""
		with open(filename, "rt") as height_map_file_obj:
			raw_data = height_map_file_obj.read()
			height_map_data_obj = jsons.loads(raw_data)
			height_map.fromDataObj(height_map_data_obj)
	else:
		log.echo(f'height map file {filename} not found')

#  ----------------------------------------------------------------------------
def mainGetHeightFromMap(lat_long_array):
	return main_height_map.get(lat_long_array[0], lat_long_array[1], lambda : getHeightUSGS(lat_long_array))

#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
# MAIN (FUNC)
#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
def main_func():
	log.echo()
	log.echo(f"==================== TopoVSlicer-Py ({MajorVersion}.{MinorVersion}) ====================")
	log.echo()

	main_timer = TimingTrace("TopoVSlicerPy")
	main_timer.start()

	#  --------------
	# CONFIGURATION
	#  --------------
	# begin with defaults
	main_config = { k: v for (k,v) in default_config.items()}

	# easy debugging
	# main_config["south_edge"] = 0.0
	# main_config["north_edge"] = 10.0
	# main_config["west_edge"] = 10.0
	# main_config["east_edge"] = 0.0

	log.todo("gather input config")

	printConfiguration(main_config, log.echo)

	main_timer.mark("gather/print configuration")

	#  --------------
	# BEGIN WORK
	#  --------------

	# ---------------
	# load height map
	log.echo()
	loadHeightMapFromFile(main_config["height_map_filename"], main_height_map)

	log.echo("checking h. map...")
	log.echo(str(main_height_map))

	main_timer.mark("load height map")

	# ---------------
	# make slices
	main_slices = TopoSlices(log_fn = log.Slicer)

	# save_filename = "mt_ord_tight.tsv"

	# ---- generate slices ----
	main_slices.generateSlices(main_config)

	main_timer.mark("generate slices")

	log.echo("getting elevations...")

	main_slices.generateElevations(mainGetHeightFromMap, main_config["use_concurrency"])

	main_timer.mark("generate elevations")

	log.todo("save height map if changed")
	# log.echo("saving height map...")

# 		file_obj.write(jsons.dumps(file_data_obj, {"indent":3}))

	# height_map_data_obj = main_height_map.toDataObj()

	# with open(main_config["height_map_filename"], "wt") as height_map_file_obj:
	# 	height_map_file_obj.write(jsons.dumps(height_map_data_obj, {"indent":3}))
	# 	log.echo(f'height map saved to: {main_config["height_map_filename"]}')

	# print(main_slices)

	# one refactor at a time plz
	# log.echo("generating svg...")
	# slicesToSVG(main_slices, main_config)
	# main_timer.mark("generate svg")

	if report_timings:
		log.echo("")
		log.echo(main_timer)


#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
# MAIN (ENTRY)
#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
if __name__ == '__main__':
	main_func()
