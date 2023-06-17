# system
from enum import Enum
import jsons
import os
import asyncio
from aiohttp import ClientSession
import argparse

# support
from support.LogChannels import log
from support.GTimer import gtimer
from support.ClassFromDict import ClassFromDict

from HeightMap import HeightMap
from USGS_EPQS import USGS_EPQS

# slicing
from SliceJobConfig import SliceJobConfig
from SVGConfig import SVGConfig
from Slice import Slice
from SliceRender import slicesToSVG
from TopoSlicer import generateTopoSlices

#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
# TODO:
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
#	* svg: smooth nodes
#	* config: silence option
# 	* config:input: validate inputs
#	* config: set async? probably not
#	* config: configurable slice async chunk size?
#	* config: specify height map filename?
#	* optionally view height map stats
#	* config: svg layers/file
#	* svg: id numbers / directions / coordinates on layers
#	* leading zeros on slice names
#	* far future: flatten areas
#	* progress feedback when getting lots of elevations

# DONE:
#	* config: get rid of all the magic strings on config dict
#	* config: break slice job into slice config / svg config
#	* move support stuff into utils/ folder
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
# TYPES
#  -----------------------------------------------------------------


#  -----------------------------------------------------------------
# CONSTANTS
#  -----------------------------------------------------------------
SliceJobFileKeys = ClassFromDict({"SliceJob":"slices", "SVG":"svg"})
CommandLineParams = ClassFromDict({"JobFilename": "job_file"})

#  -----------------------------------------------------------------
#	VARIABLES
#  -----------------------------------------------------------------

#  -----------------------------------------------------------------
#	FUNCTIONS
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

# --------------------------------------------------------------------------
# returns ( True/False, error message on failure|job file bits)
# how does this know the key names of parts of the job?
def loadJobFile(job_filename):
	if os.path.isfile(job_filename):
		log.echo(f"loading job file: {job_filename}")
		with open(job_filename, "rt") as slice_job_file_obj:
			raw_data = slice_job_file_obj.read()
			main_obj = jsons.loads(raw_data)

			# pick pieces out of main obj
			return_dict = {}
			# slice job is required
			if not SliceJobFileKeys.SliceJob in main_obj:
				return (False, f"job file did not contain slice config key '{SliceJobFileKeys.SliceJob}'")
		
			return_dict[SliceJobFileKeys.SliceJob] = main_obj[SliceJobFileKeys.SliceJob]
			# svg is actually optional
			if SliceJobFileKeys.SVG in main_obj:
				return_dict[SliceJobFileKeys.SVG] = main_obj[SliceJobFileKeys.SVG]

			return (True, return_dict)

	# file was not found
	return (False, f"job file not found: {job_filename}")

#  ----------------------------------------------------------------------------
def quitWithError(error_msg):
	log.echo()
	log.echo("ERROR: " + error_msg)
	log.echo("quitting")
	quit(1)

#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
# MAIN (FUNC)
#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
def main_func():
	gtimer.startTimer("main")

	log.addChannel("echo")
	log.addChannel("error", "Error: ")
	log.addChannel("debug", "debug: ")
	log.setChannel("debug", False)
	log.addChannel("todo", "TODO: ")

	# --------------------------------------------------------------------------
	# get config defaults (some may get overridden later)
	main_config = { k: v for (k,v) in default_config.items()}

	# --------------------------------------------------------------------------
	# command line parsing
	parser = argparse.ArgumentParser()
	parser.add_argument(CommandLineParams.JobFilename, help="json file specifying an earth slice job") #refine this later

	args = parser.parse_args()

	if args.job_file:
		main_config["slice_job_filename"] = args.job_file

	log.todo("check for silent mode, turn off log channels")

	# --------------------------------------------------------------------------
	# print banner
	log.echo()
	log.echo(f"==================== TopoVSlicer-Py ({MajorVersion}.{MinorVersion}) ====================")
	log.echo()

	log.echo("main config:")
	# print config
	for (k,v) in main_config.items():
		log.echo(f"   {k} : {v}")

	# --------------------------------------------------------------------------
	# load job file
	log.echo()
	load_job_file_result = loadJobFile(main_config["slice_job_filename"])
	if not load_job_file_result[0]:
		log.echo()
		quitWithError(load_job_file_result[1])

	job_file_objects = load_job_file_result[1]

	# --------------------------------------------------------------------------
	# get slice job config
	try:
		main_slice_job = SliceJobConfig(job_file_objects[SliceJobFileKeys.SliceJob])
	except Exception as exc:
		quitWithError(f"{exc}")

	log.echo(f"slice job:")
	log.echo(f"{main_slice_job}")

	# --------------------------------------------------------------------------
	# get svg config (if present)
	main_svg_config = None
	if SliceJobFileKeys.SVG in job_file_objects:
		try:
			main_svg_config = SVGConfig(job_file_objects[SliceJobFileKeys.SVG])
		except Exception as exc:
			quitWithError(f"{exc}")

		log.echo(f"svg config:")
		log.echo(f"{main_svg_config}")
	else:
		log.echo("no svg config specified")


	# --------------------------------------------------------------------------
	# create height map
	log.echo()
	log.echo("creating height map")
	gtimer.startTimer("load height map")

	main_height_map = HeightMap(name = "MHM")

	# have map file?
	if len(main_config["height_map_filename"]):
		log.echo(f"Loading height map from file: {main_config['height_map_filename']}")
		if os.path.isfile(main_config["height_map_filename"]):
			raw_data = ""
			with open(main_config["height_map_filename"], "rt") as height_map_file_obj:
				raw_data = height_map_file_obj.read()
				height_map_data_obj = jsons.loads(raw_data)
				main_height_map.fromDataObj(height_map_data_obj)
		else:
			log.echo("file not found")
	else:
		log.echo("No height map file specified.")

	log.echo()
	log.echo(str(main_height_map))

	gtimer.markTimer("load height map")

	# --------------------------------------------------------------------------
	# generate slices
	log.echo("generate slices")
	gtimer.startTimer("generate all slices")

	main_slices = generateTopoSlices(main_slice_job)
	gtimer.markTimer("generate all slices")

	# --------------------------------------------------------------------------
	# get elevations
	log.echo("getting elevations")
	gtimer.startTimer("get elevations")

	if main_config["async_http"]:
		asyncio.run(getElevationsAsync(main_slices, main_height_map))
	else:
		getElevations(main_slices, main_height_map)

	gtimer.markTimer("get elevations")

	# --------------------------------------------------------------------------
	# generate svg's
	if main_svg_config:
		log.echo("generating svg files")
		gtimer.startTimer("generate svg file(s)")

		slicesToSVG(main_slices, main_svg_config)

		gtimer.markTimer("generate svg file(s)")
	else:
		log.echo("no svg config in job file, skipping svg generation")

	# --------------------------------------------------------------------------
	# write height map if changed
	if main_height_map.changed():
		gtimer.startTimer("save height map")

		log.echo(f"height map changed, saving")
		height_map_data_obj = main_height_map.toDataObj()

		with open(main_config["height_map_filename"], "wt") as height_map_file_obj:
			height_map_file_obj.write(jsons.dumps(height_map_data_obj, {"indent":3}))
			log.echo(f'height map saved to: {main_config["height_map_filename"]}')

		gtimer.markTimer("save height map")

	gtimer.markTimer("main")

	# --------------------------------------------------------------------------
	# height map final stats
	log.echo()
	log.echo(main_height_map.Stats())

	if report_timings:
		log.echo()
		log.echo(gtimer.report())


#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
# MAIN (ENTRY)
#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
if __name__ == '__main__':
	main_func()
