import os
from math import ceil
import argparse
import jsons

from support.ClassFromDict import ClassFromDict
from support.ValidateDict import validateDict, checkValidator, validateDict_PostValidateFnKey, validateIsPositive
from InkscapeSVG import *
from support.LogChannels import log

log.addChannel("echo")


# TODO: switch this to use a json schema
# WILL BE HORRIBLY BROKEN UNTIL THEN!!!

# Notes:
# - all measurements assumed to be in INCHES

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
#  ██████  ██████  ███    ██ ███████ ██  ██████  
# ██      ██    ██ ████   ██ ██      ██ ██       
# ██      ██    ██ ██ ██  ██ █████   ██ ██   ███ 
# ██      ██    ██ ██  ██ ██ ██      ██ ██    ██ 
#  ██████  ██████  ██   ████ ██      ██  ██████  
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
class NotchedBarConfig(ClassFromDict):
	def __init__(self, nb_config: dict = None):
		use_config = nb_config if nb_config else NotchedBarConfig.getDefaultConfig()
		# just throw an exception, if somebody needs it they can catch it
		NotchedBarConfig.validateConfig(use_config, True)
		self.fromDict(use_config)

		if not hasattr(self, "notch_separation"):
			self.addProperties({"notch_separation": self.notch_width})

		self.addProperties({"bar_height": self.notch_depth + self.notch_depth_below})

	# -------------------------------------------------------------------------------------
	def fromDict(self, nb_config:dict):
		NotchedBarConfig.validateConfig(nb_config, throw_on_fail=True)

		self.addProperties(nb_config)

	# ------------------------------------------------------------------------------------------------------
	def __repr__(self):
		srep = ""

		members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
		for cur_member in members:
			srep += f"   {cur_member}: {getattr(self, cur_member)}\n"

		return srep

	# ------------------------------------------------------------------------------------------------------
	# this is considered the source of truth for which keys a notched bar config should have
	@staticmethod
	def getConfigValidator():
		return {
			# "extry" length at end of bar
			"end_cap_width_1" : { "required":True, "type": float, "validation_fn" : validateIsPositive  },
			"end_cap_width_2" : { "required":True, "type": float, "validation_fn" : validateIsPositive  },
			"notch_width" : { "required":True, "type": float, "validation_fn" : validateIsPositive  },
			"notch_depth" : { "required":True, "type": float, "validation_fn" : validateIsPositive  },
			# notch_depth_below is the solid be below the notch, the bar's height would then be the
			# depth, plus notch_depth_below
			"notch_depth_below" : { "required":True, "type": float, "validation_fn" : validateIsPositive  },
			"notch_count" : { "required":True, "type": int, "validation_fn" : validateIsPositive  },
			# TODO: if notch_separation is not specified, distance between notches is equal to notch_width
			"notch_separation" : { "required":False, "type": float, "validation_fn" : validateIsPositive  },
			# if present, a mark is placed under first and every nth notch
			"mark_nth_notches" : { "required":False, "type":int, "validation_fn" : validateIsPositive }
			# validateDict_PostValidateFnKey : postValidateSVGConfig
		}

	# ------------------------------------------------------------------------------------------------------
	@staticmethod
	def getDefaultConfig():
		# these defaults are based off of my specific needs
		default_config = {
			"end_cap_width" : 1.0,
			"notch_width" : 0.125,
			"notch_depth" : 0.125,
			"notch_depth_below" : 0.125,
			"notch_count" : 10,
			"notch_separation" : 0.125
		}
		# just validate this every time with exception
		NotchedBarConfig.validateConfig(default_config, True)
		return default_config

	# -------------------------------------------------------------------------------------
	@staticmethod
	def validateConfig(svg_config: dict, throw_on_fail:bool = True) -> bool:
		validation_result = validateDict(svg_config, NotchedBarConfig.getConfigValidator(), throw_on_fail = throw_on_fail, trace_enabled=False)

		return validation_result

# -------------------------------------------------------------
# end class NotchedBarConfig

# run this test every import
checkValidator(NotchedBarConfig.getConfigValidator())


#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
# ██████  ███████ ███    ██ ██████  ███████ ██████  
# ██   ██ ██      ████   ██ ██   ██ ██      ██   ██ 
# ██████  █████   ██ ██  ██ ██   ██ █████   ██████  
# ██   ██ ██      ██  ██ ██ ██   ██ ██      ██   ██ 
# ██   ██ ███████ ██   ████ ██████  ███████ ██   ██ 
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
# assumes svg coordinate system...
#
#  y  x ------>
#  |
#  |
#  v

def generateNotchedBarLayer(left_x:float, bottom_y:float, config:NotchedBarConfig):
	# text_color_string = "00aa00"
	# arrow_color_string = "00aa00"

	# -------------
	# begin drawing at lower left...
	# remember that y coordinates go UP from start, so I guess that works since we're dealing with elevations?
	bar_path = InkscapePath(left_x, bottom_y)

	marks_path = InkscapePath(left_x, bottom_y)
	marks_path.setColor("00aa00")

	# --------------
	# up "left" side
	# draw line up to upper left corner
	bar_path.draw(left_x, bottom_y - config.bar_height)

	# ----------------------------------------------
	# draw "top" of bar
	# add end cap
	cur_x = left_x + config.end_cap_width_1
	top_y = bottom_y - config.bar_height

	# draw end cap
	bar_path.draw(cur_x, top_y)
	# now sitting at left edge of first notch...

	for cur_notch in range(config.notch_count):
		# down...
		cur_y = top_y + config.notch_depth
		bar_path.draw(cur_x, cur_y)

		# right...
		cur_x += config.notch_width
		bar_path.draw(cur_x, cur_y)

		# up...
		cur_y = top_y
		bar_path.draw(cur_x, top_y)

		# make mark?
		if hasattr(config, "mark_nth_notches"):
			if cur_notch == 0 or (cur_notch + 1) % config.mark_nth_notches == 0:
				mark_y = top_y + config.notch_depth + (config.notch_depth_below / 2)
				marks_path.move(cur_x - config.notch_width, mark_y)
				marks_path.draw(cur_x, mark_y)

		# over to edge of next notch (unless last one)
		if cur_notch < config.notch_count - 1:
			cur_x += config.notch_separation
			bar_path.draw(cur_x, cur_y)

	# add other end cap
	cur_x += config.end_cap_width_2
	bar_path.draw(cur_x,cur_y)

	# ---------------
	# right side
	# at end, move back DOWN to bottom_y
	bar_path.draw(cur_x, bottom_y)

	# now at bottom "right" (max x) corner 

	# -----------
	# draw bottom 
	bar_path.draw(left_x, bottom_y)
	# note that path doesn't get closed, so the laser cutter will start
	# its cut there instead of a random point along the slope (probably)

	# the path goes into a layer group
	bar_layer_group = InkscapeGroup(f"notched_bar", True)
	bar_layer_group.addNode(bar_path)
	bar_layer_group.addNode(marks_path)

	return bar_layer_group

# -----------------------------------------------------------------------------------------
def generateNotchedBarSVG(left_x:float, bottom_y:float, config:NotchedBarConfig):

	log.echo("notched bar config:")
	log.echo(config)

	svg = InkscapeSVG()

	bar_layer = generateNotchedBarLayer(left_x, bottom_y, config)

	svg.addNode(bar_layer)

	filename_addendum = f"_cnt{config.notch_count}_wid{config.notch_width}_dep{config.notch_depth}_sep{config.notch_separation}"
	filename_addendum += f"_el{config.end_cap_width_1}-er{config.end_cap_width_2}"

	final_filename = config.svg_filename + filename_addendum + ".svg"

	log.echo(f"writing svg file: {final_filename}")

	svg.write(final_filename)

#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
# ███    ███ ██ ███████  ██████ 
# ████  ████ ██ ██      ██      
# ██ ████ ██ ██ ███████ ██      
# ██  ██  ██ ██      ██ ██      
# ██      ██ ██ ███████  ██████ 
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
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

# --------------------------------------------------------------------------
# returns ( True/False, error message on failure|job file bits)
# how does this know the key names of parts of the job?
def loadConfigFile(config_filename):
	if os.path.isfile(config_filename):
		with open(config_filename, "rt") as config_file_obj:
			raw_data = config_file_obj.read()
			config_dict = jsons.loads(raw_data)

			return (True, config_dict)

	# file was not found
	return (False, f"config file not found: {config_filename}")


#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
# ███    ███  █████  ██ ███    ██ 
# ████  ████ ██   ██ ██ ████   ██ 
# ██ ████ ██ ███████ ██ ██ ██  ██ 
# ██  ██  ██ ██   ██ ██ ██  ██ ██ 
# ██      ██ ██   ██ ██ ██   ████ 
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
def main_func():

	# --------------------------------------------------------------------------
	# config defaults (some may get overridden later)
	main_config_dict = {}

	# ---------------------------------------------
	# command line parsing
	parser = argparse.ArgumentParser()
	parser.add_argument("config_file", help="json file specifying notched bar config") #refine this later
	# parser.add_argument("--material_width_inches", help="enter width of material used for slices, will report\
	# 	     number of slices needed based on size of modeled area")
	parser.add_argument("--outfile", help="output svg file name")
	# parser.add_argument("--no_output", help="load slice job and report its config, then exit", action="store_true")

	args = parser.parse_args()

	if args.config_file:
		main_config_dict["config_filename"] = args.config_file

	if args.outfile:
		main_config_dict["svg_filename"] = args.outfile
	else:
		# strip extension from config file to get svg filename
		main_config_dict["svg_filename"] = os.path.splitext(main_config_dict["config_filename"])[0]

	# --------------------------------------------------------------------------
	# print banner
	log.echo()
	log.echo(f"==================== Notched Bar Generator ====================")
	log.echo()

	# --------------------------------------------------------------------------
	# load config file
	logSectionHeader(f"loading config file")
	log.echo(f"config file: {main_config_dict['config_filename']}")
	load_config_file_result = loadConfigFile(main_config_dict["config_filename"])
	if not load_config_file_result[0]:
		log.echo()
		quitWithError(load_config_file_result[1])

	main_nb_config = NotchedBarConfig(load_config_file_result[1])
	main_nb_config.addProperties({"svg_filename": main_config_dict["svg_filename"]})

	log.echo("config loaded")

	# --------------------------------------------------------------------------
	# generate svg
	logSectionHeader(f"generating notched bar")
	generateNotchedBarSVG(0, main_nb_config.bar_height * 2.0, main_nb_config)

	log.echo()
	log.echo("done")

#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
#  -----------------------------------------------------------------
main_func()