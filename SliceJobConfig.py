# configuration of a slice job
from support.ClassFromDict import ClassFromDict
from support.ValidateDict import validateDict, checkValidator
from support.LogChannels import log

from Slice import SliceDirection


#	TODO:
#	* additional validation (coordinates in correct order i.e. north > south)

log.addChannel("sjc", "sjc")
log.setChannel("sjc", False)

# ------------------------------------------------------------------------------------------------------
class SliceJobConfig(ClassFromDict):
	def __init__(self, slice_config: dict = None):
		use_config = slice_config if slice_config else SliceJobConfig.getDefaultConfig()
		# just throw an exception, if somebody needs it they can catch it
		SliceJobConfig.validateConfig(use_config, True)
		self.fromDict(use_config)

	# -------------------------------------------------------------------------------------
	def fromDict(self, slice_config:dict):
		SliceJobConfig.validateConfig(slice_config, throw_on_fail=True)

		self.addProperties(slice_config, SliceJobConfig.getConfigValidator().keys())
		#TODO: specially handle slice_direction here...
		self.slice_direction = SliceDirection.toSliceDirection(self.slice_direction)

	# ------------------------------------------------------------------------------------------------------
	def __repr__(self):
		srep = ""

		# print all keys in validator
		validator = SliceJobConfig.getConfigValidator()
		for cur_rule_key  in validator.keys():
			srep += f"   {cur_rule_key}: {getattr(self, cur_rule_key)}\n"

		return srep

	# ------------------------------------------------------------------------------------------------------
	# this is considered the source of truth for which keys a slice job config should have
	@staticmethod
	def getConfigValidator():
		def validateSliceDir(val):
			return True if SliceDirection.isValidSliceDir(val) else (False, f"{val} is not a valid SliceDirection")
		return {
			# actually, an enum, but will come in as a string and we'll convert manually anyway
			"slice_direction": { "required":True, "type": str, "validation_fn": validateSliceDir },
			"number_of_elevations" : { "required":True, "type": int },
			"number_of_slices" : { "required":True, "type": int },
			"north_edge" : { "required":True, "type": float },
			"south_edge" : { "required":True, "type": float },
			"east_edge" : { "required":True, "type": float },
			"west_edge" : { "required":True, "type": float }
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
			"east_edge" : 0.0,
			"west_edge" : 1.0
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
	print("a passing case")
	good_config = SliceJobConfig.getDefaultConfig()
	good_config["slice_direction"] = "WestEast"
	good_config["number_of_elevations"] = 78
	good_config["west_edge"] = 10.1
	good_config_instance = SliceJobConfig(good_config)

	print("result:")
	print(good_config_instance)
	# verify that slice direction was converted to enum type
	print(f"verify type of slice direction: {type(good_config_instance.slice_direction)}")
