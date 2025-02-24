# configuration of a slice job
from jsonschema import Draft7Validator

from support.LogChannels import log
from unitsSupport import *
from Slice import SliceDirection


#	TODO:
#	* additional validation (coordinates in correct order i.e. north > south)

log.addChannel("sjc", "sjc")
log.setChannel("sjc", False)

# ------------------------------------------------------------------------------------------------------
class SliceJobConfig():
	def __init__(self, slice_config: dict):
		self.repr_keys = []

		# just throw an exception, if somebody needs it they can catch it
		SliceJobConfig.validateConfig(slice_config, True)

		for cur_key in SliceJobConfig.getConfigSchema()["properties"]:
			if cur_key in slice_config:
				self[cur_key] =  slice_config[cur_key]

		#TODO: specially handle slice_direction here...
		self.slice_direction = SliceDirection.toSliceDirection(self.slice_direction)

		self.repr_keys = [cur_val_key for cur_val_key in slice_config.keys()]
		self.calcMetrics()

	# these allow me to add class properties via brackets
	# ------------------------------------------
	def __getitem__(self, item):
			return getattr(self, item)

	def __setitem__(self, key, value):
			return setattr(self, key, value)

	# ------------------------------------------------------------------------------------------------------
	def __repr__(self):
		srep = ""

		for cur_key in self.repr_keys:
			srep += f"   {cur_key}: {getattr(self, cur_key)}\n"

		return srep

	# ------------------------------------------------------------------------------------------------------
	@staticmethod
	def getConfigSchema():
		return {
			"type":"object",
			"properties":
			{
				"slice_direction" : { "enum": ["NorthSouth", "WestEast"] },
				"number_of_elevations" : { "type" : "integer", "minimum": 1 },
				"number_of_slices" : { "type" : "integer", "minimum" : 1 },
				"north_edge" : { "type" : "number" },
				"south_edge" : { "type" : "number" },
				"east_edge" : { "type" : "number" },
				"west_edge" : { "type" : "number" }
			},
			"required" : [
				"slice_direction",
				"number_of_elevations",
				"number_of_slices",
				"north_edge",
				"south_edge",
				"east_edge",
				"west_edge"
			]
		}

	# ------------------------------------------------------------------------------------------------------
	@staticmethod
	def getMetricsSchema():
		""" returns schema for values that get calculated from a config """
		return {
			"type":"object",
			"properties":
			{
				"east_west_miles" : { "type": "number" },
				"east_west_degrees" : { "type": "number" },
				"east_west_feet" : { "type": "number" },
				"north_south_degrees" : { "type": "number" },
				"north_south_miles" : { "type": "number" },
				"north_south_feet" : { "type": "number" }
			},
			"required" : [
				"east_west_miles",
				"east_west_degrees",
				"east_west_feet",
				"north_south_degrees",
				"north_south_miles",
				"north_south_feet"
			]
		}

	# -------------------------------------------------------------------------------------
	@staticmethod
	def validateConfig(slice_config: dict, throw_on_fail:bool = True) -> bool:
		log.sjc(f"validateConfig(): {slice_config}")

		validation_result = True

		try:
				# check that schema itself is valid...
				config_schema = SliceJobConfig.getConfigSchema()
				Draft7Validator.check_schema(config_schema)

				validator = Draft7Validator(config_schema)
				validator.validate(slice_config)
		except Exception as e:
			validation_result = False
			if throw_on_fail:
				raise e

		return validation_result

	# --------------------------------------------------------------------------
	def calcMetrics(self):
		metrics = {}
		metrics["east_west_degrees"] = abs(self.west_edge) - abs(self.east_edge) # uhhhhh, might not be correct, but usually both the same sign so *shrug*

		# Just use south edge. Doing this stretches the slice e-w as you go north but, eh, hopefully good enough.
		metrics["east_west_miles"] = longitudeDegreesToMiles(metrics["east_west_degrees"], self.south_edge)
		metrics["east_west_feet"] = metrics["east_west_miles"] * feetPerMile()

		metrics["north_south_degrees"] = self.north_edge - self.south_edge
		metrics["north_south_miles"] = latitudeDegreesToMiles(metrics["north_south_degrees"])
		metrics["north_south_feet"] = metrics["north_south_miles"] * feetPerMile()

		for cur_met_key in metrics.keys():
			self[cur_met_key] = metrics[cur_met_key]
			self.repr_keys.append(cur_met_key)

# ----- end class SliceJobConfig -----

# -------------------------------------------------------------
# -------------------------------------------------------------
if __name__ == "__main__":
	print()
	print("===== SliceJobConfig =====")
	print()
	test_config_dict = {
		"slice_direction" : "NorthSouth",
		"number_of_elevations" : 10,
		"number_of_slices" : 100,
		"north_edge" : 1.0,
		"south_edge" : 0.1,
		"east_edge" : 0.0,
		"west_edge" : 1.0
	}

	test_config = SliceJobConfig(test_config_dict)

	print(f"input config: {test_config_dict}")

	print("------------------------")
	print("Resulting SliceJobConfig:")
	print(test_config)