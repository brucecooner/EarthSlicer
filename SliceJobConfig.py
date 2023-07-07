# configuration of a slice job
from support.ClassFromDict import ClassFromDict
from support.ValidateDict import validateDict, checkValidator, validateDict_PostValidateFnKey, validateIsPositive
from support.LogChannels import log
from unitsSupport import *
from Slice import SliceDirection


#	TODO:
#	* additional validation (coordinates in correct order i.e. north > south)

log.addChannel("sjc", "sjc")
log.setChannel("sjc", False)

# ------------------------------------------------------------------------------------------------------
class SliceJobConfig(ClassFromDict):
	def __init__(self, slice_config: dict = None):
		self.repr_keys = []
		use_config = slice_config if slice_config else SliceJobConfig.getDefaultConfig()
		# just throw an exception, if somebody needs it they can catch it
		SliceJobConfig.validateConfig(use_config, True)
		self.fromDict(use_config)

	# -------------------------------------------------------------------------------------
	def fromDict(self, slice_config:dict):
		SliceJobConfig.validateConfig(slice_config, throw_on_fail=True)

		self.addProperties(slice_config, slice_config.keys()) # SliceJobConfig.getConfigValidator().keys())
		#TODO: specially handle slice_direction here...
		self.slice_direction = SliceDirection.toSliceDirection(self.slice_direction)

		self.repr_keys = [cur_val_key for cur_val_key in slice_config.keys()] # SliceJobConfig.getConfigValidator()]
		self.calcMetrics()

	# ------------------------------------------------------------------------------------------------------
	def __repr__(self):
		srep = ""

		for cur_key in self.repr_keys:
			srep += f"   {cur_key}: {getattr(self, cur_key)}\n"
		# # print all keys in validator
		# output_keys = (cur_val_key for cur_val_key in SliceJobConfig.getConfigValidator())
		# # add metrics keys
		# output_keys.concat(getMetricsKeys())

		# validator = SliceJobConfig.getConfigValidator()
		# for cur_rule_key  in validator.keys():
		# 	srep += f"   {cur_rule_key}: {getattr(self, cur_rule_key)}\n"

		# print metrics
		# for cur_metric_key in metrics_keys:
		# 	srep += f"   {cur_metric_key}: {getattr(self, cur_metric_key)}\n"

		return srep

	# ------------------------------------------------------------------------------------------------------
	# this is considered the source of truth for which keys a slice job config should have
	@staticmethod
	def getConfigValidator():
		def sliceConfigPostValidator(cfg):
			# north lat must be > south lat
			if cfg["north_edge"] <= cfg["south_edge"]:
				return (False, "north_edge must be > south_edge")
			# west longitude must be < east longitude (decreasing to the west)
			if cfg["west_edge"] > cfg["east_edge"]:
				return (False, "east_edge must be > west_edge")
			return True

		def validateSliceDir(val, key):
			return True if SliceDirection.isValidSliceDir(val) else (False, f"{val} is not a valid SliceDirection")

		return {
			# actually, an enum, but will come in as a string and we'll convert manually anyway
			"slice_direction": { "required":True, "type": str, "validation_fn": validateSliceDir },
			"number_of_elevations" : { "required":True, "type": int, "validation_fn" : validateIsPositive },
			"number_of_slices" : { "required":True, "type": int, "validation_fn" : validateIsPositive },
			"north_edge" : { "required":True, "type": float },
			"south_edge" : { "required":True, "type": float },
			"east_edge" : { "required":True, "type": float },
			"west_edge" : { "required":True, "type": float },
			validateDict_PostValidateFnKey : sliceConfigPostValidator
		}

	# ------------------------------------------------------------------------------------------------------
	@staticmethod
	def getDefaultConfig():
		default_config = {
			# actually, slice_direction is an enum, but will come in as a string and we'll convert manually after (probably)
			"slice_direction": "NorthSouth",
			"number_of_elevations" : 10,
			"number_of_slices" : 10,
			"north_edge" : 1.0,
			"south_edge" : 0.0,
			"east_edge" : 1.0,
			"west_edge" : 0.0
		}
		log.sjc(f"getDefaultConfig(): {default_config}")
		# just validate this every time with exception
		SliceJobConfig.validateConfig(default_config, True)
		return default_config

	# -------------------------------------------------------------------------------------
	@staticmethod
	def validateConfig(slice_config: dict, throw_on_fail:bool = True) -> bool:

		log.sjc(f"validateConfig(): {slice_config}")

		validation_result = validateDict(slice_config, SliceJobConfig.getConfigValidator(), throw_on_fail = throw_on_fail, trace_enabled=False)

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

		self.addProperties(metrics)

		for cur_met_key in metrics.keys():
			self.repr_keys.append(cur_met_key)



# -------------------------------------------------------------
# end class SliceJobConfig

# run this test every import
checkValidator(SliceJobConfig.getConfigValidator())


# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------
if __name__ == "__main__":
	from support.TestSupport import testForException, testForNoException

	print("----- Slice Job Config Test -----")

	print("---- checking validator ----")
	checkValidator(SliceJobConfig.getConfigValidator())
	print("done checking validator")

	# validate the defaults
	print("---- validating defaults ----")
	validateDict(SliceJobConfig.getDefaultConfig(), SliceJobConfig.getConfigValidator())
	print("done validating defaults")

	print()
	print("testing constructor(None) returns default config:")
	test_default_config = SliceJobConfig(None)
	print(f"result:")
	print(test_default_config)

	print()
	print("testing some faulty configs to construtor")
	bad_config = SliceJobConfig.getDefaultConfig()
	bad_config["north_edge"] = 10	# subtle-ish type error (not a float)
	testForException("exception for incorrect north_edge type", lambda: SliceJobConfig(bad_config))

	print()
	bad_config = SliceJobConfig.getDefaultConfig()
	bad_config["slice_direction"] = "SouthNorth" # a more subtle error, this is not a valid slice dir
	testForException("exception for bad slice direction", lambda: SliceJobConfig(bad_config))

	print()
	num_slices_zero_config = SliceJobConfig.getDefaultConfig()
	num_slices_zero_config["number_of_slices"] = 0
	testForException("exception for number_of_slices = 0", lambda: SliceJobConfig(num_slices_zero_config))

	print()
	num_slices_negative_config = SliceJobConfig.getDefaultConfig()
	num_slices_negative_config["number_of_slices"] = -1
	testForException("exception for number_of_slices = -1", lambda: SliceJobConfig(num_slices_negative_config))

	print()
	num_elevations_zero_config = SliceJobConfig.getDefaultConfig()
	num_elevations_zero_config["number_of_elevations"] = 0
	testForException("exception for number_of_slices = 0", lambda: SliceJobConfig(num_elevations_zero_config))

	print()
	num_elevations_negative_config = SliceJobConfig.getDefaultConfig()
	num_elevations_negative_config["number_of_slices"] = -1
	testForException("exception for number_of_elevations = -1", lambda: SliceJobConfig(num_elevations_negative_config))

	print()
	num_slices_negative_config = SliceJobConfig.getDefaultConfig()
	num_slices_negative_config["number_of_slices"] = -1
	testForException("exception for number_of_slices = -1", lambda: SliceJobConfig(num_slices_negative_config))

	print()
	north_lt_south_config = SliceJobConfig.getDefaultConfig()
	north_lt_south_config["north_edge"] = -1.0
	north_lt_south_config["south_edge"] = 0.0
	testForException("exception for north edge < south edge", lambda: SliceJobConfig(north_lt_south_config))

	print()
	east_lt_west_config = SliceJobConfig.getDefaultConfig()
	east_lt_west_config["east_edge"] = -33.0
	east_lt_west_config["west_edge"] = -31.0
	testForException("exception for east edge < west edge", lambda: SliceJobConfig(east_lt_west_config))

	print()
	print("a passing case")
	good_config = SliceJobConfig.getDefaultConfig()
	good_config["slice_direction"] = "WestEast"
	good_config["number_of_elevations"] = 78
	good_config["east_edge"] = -9.1
	good_config["west_edge"] = -10.1
	good_config_instance = SliceJobConfig(good_config)

	print("result:")
	print(good_config_instance)
	# verify that slice direction was converted to enum type
	print(f"verify type of slice direction: {type(good_config_instance.slice_direction)}")
