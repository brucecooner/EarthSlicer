# system
from enum import Enum
import jsons
import os
import asyncio
from aiohttp import ClientSession
import argparse
import math

# support
from support.LogChannels import log
from support.GTimer import gtimer
from support.ClassFromDict import ClassFromDict
from unitsSupport import *

from HeightMap import HeightMap
from USGS_EPQS import USGS_EPQS

# slicing
from SliceJobConfig import SliceJobConfig
from SliceJob import SliceJob
from SVGConfig import SVGConfig
from Slice import SliceDirection
from SliceRender import slicesToSVG

#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
# TODO:
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
#	* allow parameter overriding any config option?
#	* add coords to output slices?
#	* allow material width inches to override configured number of slices?
#	* emsmallen the text (parameterized?)
#	* validator: better way to denote keys that belong to dict, and keys that belong to validator
#	* registration marks?
#	* wide svg's via overlap
#	* add extended tags to svg's <earthslicer /> ? (desc. / coordinates / ?)
#	* render numbers/letters at origin, translate to final position
#	* DOCUMENTATION! - default job file for reference, or ability to create one from configs
#	* better help if no slice job specified (include example config file)
#	* hollowing out svgs
#	* output info about svg files created (layers/?)
#	* formalize some svg generation tests (rows x columns and stuff)
#	* config: silence option
#	* config: specify height map filename?
#	* optionally view height map stats?
#	* far future: flatten areas
#	* progress feedback when getting lots of elevations

# DONE:
#	* render every nth slice (slice step)
#	* change material "width" to "thickness" (less confustion with svg width)
#	* echo (optional) "description" key from slice job file
#	* notches in bottom option?
#	* put slice numbers in output svg names
# 	* config:input: validate inputs / range checks - sorta doing this with validator
#	* BUG: reports incorrect number of svg files written!
#	* slice job config post validator
#	* ----- VERSION 1.0 ----------------------------------
#	* linear feet of material required
#	* mark between filename and suffix (numbers get multiplied by 10!)
#	* output slice metrics 
#	* svg: vertical scale
#	* leading zeros on slice numbers in svg
#	* svg: use svgconfig.base_inches instead of hardwired value
#	* allow working with files in non-script folders (output should be in same dir as job file)
#	* config: svg layers/file (handled as usable area of svg)
#	* svg: id numbers / directions / coordinates on layers
#	* svg: move layers around to they don't overlap?
#	* svg: smooth nodes - https://www.w3.org/TR/SVG/paths.html#PathDataQuadraticBezierCommands
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
MajorVersion = 1
MinorVersion = 0

#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
# DEFAULTS
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
default_app_config = {
	# "async_http" : True,
	"height_map_filename" : "height_map.json",
	"report_timings" : True,
	"no_output" : False,
	"material_thickness_inches" : None,
	"slice_step" : 1	# how far slice index steps after each slice, allows "skipping" slices (i.e. 1=> every slice, 2=>every other slice, 3=>every third slice)
}

#  -----------------------------------------------------------------
# TYPES
#  -----------------------------------------------------------------

#  -----------------------------------------------------------------
# CONSTANTS
#  -----------------------------------------------------------------
SliceJobFileKeys = ClassFromDict({"SliceJob":"slices", "SVG":"svg"})

#  -----------------------------------------------------------------
#	VARIABLES
#  -----------------------------------------------------------------

#  -----------------------------------------------------------------
#	FUNCTIONS
#  -----------------------------------------------------------------
#  ----------------------------------------------------------------------------
# don't see this ever running quickly enough to use but, will leave it for now
# def getElevations(slices:list[Slice], height_map:HeightMap):
# 	#  ----------------------------------------
# 	# uses height map param, delegates misses to epqs (serial)
# 	def getHeightFromMap(lat_long_array):
# 			return height_map.get(lat_long_array[0], lat_long_array[1], USGS_EPQS.getHeight)

# 	for cur_slice in slices:
# 		log.slicer(f'slice: {cur_slice.slice_index}')
# 		cur_slice.getElevations(getHeightFromMap)

#  ----------------------------------------------------------------------------
# async def getElevationsAsync(slices:list[Slice], height_map:HeightMap):
async def getElevationsAsync(slice_job:SliceJob, height_map:HeightMap):
	total_elevations_queried = 0
	#  ----------------------------------------
	# uses height map passed in to parent func, delegates misses to epqs (async)
	async with ClientSession() as session:
		async def getHeightFromMapAsync(lat_long_array):
			return await height_map.getAsync(lat_long_array[0], lat_long_array[1], lambda lat_long_arr : USGS_EPQS.getHeightAsync(lat_long_arr, session))

		for cur_slice in slice_job.slices:
			log.echo(f'getting elevations for slice: {cur_slice.slice_index}')
			total_elevations_queried += await cur_slice.getElevationsAsync(getHeightFromMapAsync)

	return total_elevations_queried

# --------------------------------------------------------------------------
# returns ( True/False, error message on failure|job file bits)
# how does this know the key names of parts of the job?
def loadJobFile(job_filename):
	if os.path.isfile(job_filename):
		log.echo(f"loading job file: {job_filename}")
		with open(job_filename, "rt") as slice_job_file_obj:
			raw_data = slice_job_file_obj.read()
			# main_obj = jsons.loads(raw_data)
			return_dict = jsons.loads(raw_data)

			# validation
			# pick pieces out of main obj
			# return_dict = {}
			# slice job is required
			if not SliceJobFileKeys.SliceJob in return_dict: # main_obj:
				return (False, f"job file did not contain slice config key '{SliceJobFileKeys.SliceJob}'")
		
			# return_dict[SliceJobFileKeys.SliceJob] = main_obj[SliceJobFileKeys.SliceJob]
			# svg is actually optional
			# if SliceJobFileKeys.SVG in main_obj:
			# 	return_dict[SliceJobFileKeys.SVG] = main_obj[SliceJobFileKeys.SVG]

			return (True, return_dict)

	# file was not found
	return (False, f"job file not found: {job_filename}")

#  ----------------------------------------------------------------------------
def quitWithError(error_msg):
	log.echo()
	log.echo("ERROR: " + error_msg)
	log.echo("quitting")
	quit(1)

# -----------------------------------------------------------------------------
# so you can standardize reporting on major work section entry
def logSectionHeader(section_name:str):
	dashes = "----------"
	log.echo()
	log.echo(f"{dashes} {section_name} {dashes}")

#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
# MAIN (FUNC)
#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
def main_func():
	gtimer.startTimer("main")

	log.addChannel("echo")
	log.addChannel("todo", "TODO: ")

	# --------------------------------------------------------------------------
	# get config defaults (some may get overridden later)
	main_config = { k: v for (k,v) in default_app_config.items()}

	# --------------------------------------------------------------------------
	# command line parsing
	parser = argparse.ArgumentParser()
	parser.add_argument("job_file", help="json file specifying an earth slice job") #refine this later
	parser.add_argument("--material_thickness_inches", help="thickness of material used for slices, will report\
		     number of slices needed based on size of modeled area")
	parser.add_argument("--slice_step", help="index step between slices (i.e. 1=>output every slice, 2=>output every other slice, 3=>output every third slice)")
	parser.add_argument("--no_output", help="load slice job and report its config, then exit", action="store_true")

	args = parser.parse_args()

	if args.job_file:
		main_config["slice_job_filename"] = args.job_file

	main_config["no_output"] = args.no_output
	main_config["material_thickness_inches"] = None if not args.material_thickness_inches else float(args.material_thickness_inches)
	if args.slice_step:
		main_config["slice_step"] = int(args.slice_step)

	log.todo("check for silent mode, turn off log channels")

	# --------------------------------------------------------------------------
	# print banner
	log.echo()
	log.echo(f"========================================================================================")
	log.echo(f"==================== TopoVSlicer-Py ({MajorVersion}.{MinorVersion}) ====================")
	log.echo(f"========================================================================================")
	log.echo()

	log.echo("main config:")
	# print config
	for (k,v) in main_config.items():
		log.echo(f"   {k} : {v}")

	# --------------------------------------------------------------------------
	# load job file
	logSectionHeader("loading job file")
	load_job_file_result = loadJobFile(main_config["slice_job_filename"])
	if not load_job_file_result[0]:
		log.echo()
		quitWithError(load_job_file_result[1])

	job_file_objects = load_job_file_result[1]

	main_config["job_file_path"] = os.path.dirname(main_config["slice_job_filename"])

	# --------------------------------------------------------------------------
	# echo slice job description key (if found)
	if "description" in job_file_objects:
		log.echo()
		log.echo(f"description: {job_file_objects['description']}")
		log.echo()

	# --------------------------------------------------------------------------
	# get slice job config
	try:
		main_slice_job_config = SliceJobConfig(job_file_objects[SliceJobFileKeys.SliceJob])
	except Exception as exc:
		quitWithError(f"{exc}")

	log.echo(f"slice job:")
	log.echo(f"{main_slice_job_config}")

	# --------------------------------------------------------------------------
	# get svg config (if present)
	main_svg_config = None
	if SliceJobFileKeys.SVG in job_file_objects:
		try:
			main_svg_config = SVGConfig(job_file_objects[SliceJobFileKeys.SVG])
			main_svg_config.addProperties({"layers_grid_x_spacing":0.5, "layers_grid_y_spacing":0.25})

		except Exception as exc:
			quitWithError(f"{exc}")
	else:
		log.echo("no svg config specified")

	# --------------------------------------------------------------------------
	# calculate/verify svg output location
	if main_svg_config:
		svg_output_path = os.path.dirname(main_svg_config.svg_base_filename)	# extract path from svg output name
		svg_output_full_path = os.path.join(main_config["job_file_path"], svg_output_path)

		if os.path.exists(svg_output_full_path):
			main_svg_config.addProperties( {"base_path": main_config["job_file_path"] } )

			log.echo(f"svg config:")
			log.echo(f"{main_svg_config}")
		else:
			quitWithError(f"specified svg output path does not exist: {svg_output_full_path}{os.sep}")

	# ---------------------------------------------------------------------------
	# create main slice job
	main_slice_job = SliceJob(main_slice_job_config, main_config["slice_step"])

	# ---------------------------------------------------------------------------
	# scale info
	scale_feet_per_inch = 0
	# the width of the svg's produced (which are in sliced direction) determines the map scale
	logSectionHeader("scale info")
	if main_svg_config:
		scale_feet_per_inch = main_slice_job.sliceLengthFeet() / main_svg_config.slice_width_inches
		log.echo(f"svg config specified a width of {main_svg_config.slice_width_inches} inches")
		log.echo(f"giving a scale of {scale_feet_per_inch} feet per inch")
		log.echo(f"or {scale_feet_per_inch / 5280} miles per inch")
	else:
		log.echo(f"no svg config given, unable to determine map scale")

	# ---------------------------------------------------------------------------
	# material width/thickness to number of slices calculator
	if main_config["material_thickness_inches"]:
		logSectionHeader("material thickness => number of slices")
		if not main_svg_config:
			quitWithError("material_thickness_inches option requires an svg config, but no svg config was found in job file")

		log.echo(f"specified material thickness (inches): {main_config['material_thickness_inches']}")
		log.echo(f"mapped width perpendicular to slices (feet): {main_slice_job.sliceWidthFeet()}")
		num_slices_of_material = int(main_slice_job.sliceWidthFeet() / (main_config["material_thickness_inches"] * scale_feet_per_inch))
		log.echo(f"results in {num_slices_of_material} layers of material to match mapped width")
		linear_feet_material = (main_svg_config.slice_width_inches * num_slices_of_material) / 12.0
		log.echo(f"which comes to {linear_feet_material} linear feet of material")
		log.echo(f"(exiting)")
		quit()

	# --------------------------------------------------------------------------
	# step out here if only wanted job file report
	if main_config["no_output"]:
		log.echo()
		log.echo("specified no_output option, exiting")
		quit()

	# --------------------------------------------------------------------------
	# create height map
	logSectionHeader("creating height map")
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
	logSectionHeader("generating slices")

	gtimer.startTimer("generate all slices")
	main_slice_job.generateSlices()
	gtimer.markTimer("generate all slices")

	log.echo(f"generated {main_slice_job.numSlices()} slices")

	# --------------------------------------------------------------------------
	# get elevations
	logSectionHeader("getting elevations")
	gtimer.startTimer("get elevations")

	total_elevations_queried = asyncio.run(getElevationsAsync(main_slice_job, main_height_map))

	gtimer.markTimer("get elevations")

	log.echo()
	log.echo(f"queried {total_elevations_queried} elevations")
	log.echo(f"minimum elevation: {main_slice_job.minimumElevation()} feet")
	log.echo(f"maximum elevation: {main_slice_job.maximumElevation()} feet")

	# --------------------------------------------------------------------------
	# generate svg's
	logSectionHeader("generating svg files")
	if main_svg_config:
		gtimer.startTimer("generate svg file(s)")

		direction_abbr = "NS" if main_slice_job.config.slice_direction == SliceDirection.NorthSouth else "WE"
		slice_svg_width = f"{main_svg_config.slice_width_inches}in"
		main_svg_config.addProperties({"filename_info_string" : direction_abbr + "-" + slice_svg_width})

		slicesToSVG(main_slice_job.slices, main_svg_config)

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
	logSectionHeader("height map usage stats")
	log.echo(main_height_map.Stats())

	# --------------------------------------------------------------------------
	# timings
	logSectionHeader("timings")
	if main_config["report_timings"]:
		log.echo(gtimer.report())


#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
# MAIN (ENTRY)
#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
if __name__ == '__main__':
	main_func()
