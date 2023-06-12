# system
import jsons
import os
import asyncio
from aiohttp import ClientSession
import argparse

# support
from LogChannels import log
from GTimer import gtimer
from TimingTrace import TimingTrace

from HeightMap import HeightMap
from USGS_EPQS import USGS_EPQS

# slicing
from Slice import Slice, SliceDirection
from SliceRender import slicesToSVG
from TopoSlicer import generateTopoSlices

#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
# TODO:
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
#	* config: silence
# 	* config:input: validate inputs
#	* config: get rid of all the magic strings on config dict
#	* config: set async? probably not
#	* config: configurable slice async chunk size?
#	* config: specify height map filename
#	* optionally view height map stats
#	* config: svg layers/file
#	* svg: id numbers / directions / coordinates on layers
#	* leading zeros on slice names

# DONE:
#	* config: make job file required parameter
#	* config: slice output length
#	* slice job: read from file
#	* new name for main file, too close to TopoSlicer class name (went with EarthSlicer for now)
#	* iterative output w/ optional trace (ongoing)
#	* height map stats report
#	* report total height map queries?

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
	# app concerns
	# "slice_job_filename" : "earth_slice_default_job.json",
	"async_http" : True,
	"height_map_filename" : "height_map.json",
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

#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
#	VARIABLES
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------

#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
#	FUNCTIONS
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
#  ----------------------------------------------------------------------------
def getElevations(slices:list[Slice], height_map:HeightMap):
	#  ----------------------------------------
	# uses height map param, delegates misses to epqs (serial)
	def getHeightFromMap(lat_long_array):
			return height_map.get(lat_long_array[0], lat_long_array[1], USGS_EPQS.getHeight)

	for cur_slice in slices:
		log.slicer(f'slice: {cur_slice.name}')
		cur_slice.getElevations(getHeightFromMap)

#  ----------------------------------------------------------------------------
async def getElevationsAsync(slices:list[Slice], height_map:HeightMap):
	#  ----------------------------------------
	# uses height map passed in to parent func, delegates misses to epqs (async)
	async with ClientSession() as session:
		async def getHeightFromMapAsync(lat_long_array):
			return await height_map.getAsync(lat_long_array[0], lat_long_array[1], lambda lat_long_arr : USGS_EPQS.getHeightAsync(lat_long_arr, session))

		for cur_slice in slices:
			log.slicer(f'slice: {cur_slice.name}')
			await cur_slice.getElevationsAsync(getHeightFromMapAsync)

#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
# MAIN (FUNC)
#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
def main_func():
	log.addChannel("echo")
	log.addChannel("error", "Error: ")
	log.addChannel("debug", "debug: ")
	log.setChannel("debug", False)
	log.addChannel("todo", "TODO: ")

	main_timer = TimingTrace("TopoVSlicerPy")

	# --------------------------------------------------------------------------
	# get config defaults (some may get overridden later)
	main_config = { k: v for (k,v) in default_config.items()}

	# --------------------------------------------------------------------------
	# command line parsing
	# config consts (move somewhere sensible at some point)
	JOB_FILE_CONFIG_PARAM = "job_file"

	parser = argparse.ArgumentParser()
	parser.add_argument(JOB_FILE_CONFIG_PARAM, help="json file specifying an earth slice job") #refine this later

	args = parser.parse_args()

	if args.job_file:
		main_config["slice_job_filename"] = args.job_file[len(JOB_FILE_CONFIG_PARAM) + 1:] # go past param and equals sign

	log.todo("check for silent mode, turn off log channels")

	# --------------------------------------------------------------------------
	# print banner
	log.echo()
	log.echo(f"==================== TopoVSlicer-Py ({MajorVersion}.{MinorVersion}) ====================")
	log.echo()

	log.echo("config:")
	# print config
	for (k,v) in main_config.items():
		log.echo(f"\t{k} : {v}")

	# --------------------------------------------------------------------------
	# load job file
	log.echo()
	log.echo("loading job file")
	if os.path.isfile(main_config["slice_job_filename"]):
		raw_data = ""
		with open(main_config["slice_job_filename"], "rt") as slice_job_file_obj:
			raw_data = slice_job_file_obj.read()
			main_config["slice_job"] = jsons.loads(raw_data)
			log.echo("loaded")
	else:
		log.error(f"job file {main_config['slice_job_filename']} not found")

	log.todo("print this prettier")
	log.echo(f"slice job: {main_config['slice_job']}")

	# --------------------------------------------------------------------------
	# create height map
	main_timer.start()

	log.echo()
	log.echo("creating height map")
	main_height_map = HeightMap(name = "MHM")

	# have map file?
	if len(main_config["height_map_filename"]):
		log.echo(f"Loading height map from file: {main_config['height_map_filename']}")
		if os.path.isfile(main_config["height_map_filename"]):
			gtimer.startTimer("loadHmap")
			raw_data = ""
			with open(main_config["height_map_filename"], "rt") as height_map_file_obj:
				raw_data = height_map_file_obj.read()
				height_map_data_obj = jsons.loads(raw_data)
				main_height_map.fromDataObj(height_map_data_obj)
			gtimer.markTimer("loadHmap", "loadHMap")
			log.echo("loaded")
		else:
			log.echo("file not found")
	else:
		log.echo("No height map file specified.")

	log.echo()
	log.echo(str(main_height_map))

	main_timer.mark("load height map")

	# --------------------------------------------------------------------------
	# generate slices
	log.echo("generating slices")
	main_slices = generateTopoSlices(main_config["slice_job"])

	main_timer.mark("generate slices")

	# --------------------------------------------------------------------------
	# get elevations
	log.echo("getting elevations")

	if main_config["async_http"]:
		asyncio.run(getElevationsAsync(main_slices, main_height_map))
	else:
		getElevations(main_slices, main_height_map)

	main_timer.mark("generate elevations")

	# --------------------------------------------------------------------------
	# generate svg's
	log.echo("generating svg files")
	slicesToSVG(main_slices, main_config["slice_job"])
	main_timer.mark("generate svg")

	# --------------------------------------------------------------------------
	# write height map if changed
	if main_height_map.changed():
		log.echo(f"height map changed, saving")
		height_map_data_obj = main_height_map.toDataObj()

		with open(main_config["height_map_filename"], "wt") as height_map_file_obj:
			height_map_file_obj.write(jsons.dumps(height_map_data_obj, {"indent":3}))
			log.echo(f'height map saved to: {main_config["height_map_filename"]}')

	# --------------------------------------------------------------------------
	# height map final stats
	log.echo()
	log.echo(main_height_map.Stats())

	if report_timings:
		log.echo("")
		log.echo(main_timer)

		log.echo()
		log.echo(gtimer.report())


#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
# MAIN (ENTRY)
#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
if __name__ == '__main__':
	main_func()
