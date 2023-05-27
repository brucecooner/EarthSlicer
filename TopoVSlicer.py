# system
import jsons
import os
import asyncio
from aiohttp import ClientSession

# support
from LogChannels import log
from TimingTrace import TimingTrace

from HeightMap import HeightMap
from USGS_EPQS import USGS_EPQS

# slicing
from Slice import SliceDirection
from SliceRender import slicesToSVG
from TopoSlicer import TopoSlicer

#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
# TODO:
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
#	* new name for main file, too close to TopoSlicer class name
#	* config: optional trace
#	* config: silent running
#	* config: save slices to file
#	* config: slice output length
# 	* config input EVERYTHING
# 	* config:input: validate inputs
#	* config: get rid of all the magic strings on config dict
#	* config: read from file
# 
#	* iterative output w/ optional trace (ongoing)
#	* height map stats report

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
	"async_http" : True,
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
log.addChannel("echo")
log.addChannel("debug", "debug")
log.addChannel("todo", "TODO")

#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
#	FUNCTIONS
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------

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
def getElevations(slicer:TopoSlicer, height_map:HeightMap):
	#  ----------------------------------------
	# uses height map passed in to parent func, but delegates to epqs (serial) for misses
	def getHeightFromMap(lat_long_array):
			return height_map.get(lat_long_array[0], lat_long_array[1], USGS_EPQS.getHeight)

	slicer.getElevations(elevation_func = getHeightFromMap)

#  ----------------------------------------------------------------------------
async def getElevationsAsync(slicer:TopoSlicer, height_map:HeightMap):
	log.debug("getElevationsAsync()")

	async with ClientSession() as session:
		async def getHeightFromMapAsync(lat_long_array):
			return await height_map.getAsync(lat_long_array[0], lat_long_array[1], lambda lat_long_arr : USGS_EPQS.getHeightAsync(lat_long_arr, session))

		await slicer.getElevationsAsync(elevation_func = getHeightFromMapAsync)


#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
# MAIN (FUNC)
#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
async def main_func():
	log.echo()
	log.echo(f"==================== TopoVSlicer-Py ({MajorVersion}.{MinorVersion}) ====================")
	log.echo()

	main_timer = TimingTrace("TopoVSlicerPy")
	main_timer.start()

	# --------------------------------------------------------------------------
	# CONFIGURATION
	# --------------------------------------------------------------------------
	# begin with defaults
	main_config = { k: v for (k,v) in default_config.items()}

	# debug overrides
	save_filename = "mt_ord_tight.tsv"

	# easy debugging
	# main_config["south_edge"] = 0.0
	# main_config["north_edge"] = 10.0
	# main_config["west_edge"] = 10.0
	# main_config["east_edge"] = 0.0

	log.todo("gather config from command line")

	# print config
	for (k,v) in main_config.items():
		log.echo(f"\t{k} : {v}")

	main_timer.mark("gather/print configuration")

	# --------------------------------------------------------------------------
	# BEGIN WORK
	# --------------------------------------------------------------------------

	# --------------------------------------------------------------------------
	# create height map
	log.echo("creating height map")
	main_height_map = HeightMap(name = "MHM")
	log.todo("height map load returns status")
	loadHeightMapFromFile(main_config["height_map_filename"], main_height_map)

	log.echo()
	log.echo("loaded height map (maybe)")
	log.echo(str(main_height_map))

	main_timer.mark("load height map")

	# --------------------------------------------------------------------------
	# create slicer
	log.echo("creating slicer")
	main_slicer = TopoSlicer()

	# --------------------------------------------------------------------------
	# generate slices
	log.echo("generating slices")
	main_slicer.generateSlices(main_config)

	main_timer.mark("generate slices")

	# --------------------------------------------------------------------------
	# get elevations
	log.echo("getting elevations")

	if main_config["async_http"]:
		await getElevationsAsync(main_slicer, main_height_map)
	else:
		getElevations(main_slicer, main_height_map)

	main_timer.mark("generate elevations")

	# log.echo("saving height map...")

# 		file_obj.write(jsons.dumps(file_data_obj, {"indent":3}))

	log.todo("better logic around saving height map! (dirty bit)")
	height_map_data_obj = main_height_map.toDataObj()

	with open(main_config["height_map_filename"], "wt") as height_map_file_obj:
		height_map_file_obj.write(jsons.dumps(height_map_data_obj, {"indent":3}))
		log.echo(f'height map saved to: {main_config["height_map_filename"]}')

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
	asyncio.run(main_func())
