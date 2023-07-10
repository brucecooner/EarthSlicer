# configuration of a slice job svg
from support.ClassFromDict import ClassFromDict
from support.ValidateDict import validateDict, checkValidator, validateDict_PostValidateFnKey, validateIsPositive


# ------------------------------------------------------------------------------------------------------
class SVGConfig(ClassFromDict):
	def __init__(self, svg_config: dict = None):
		use_config = svg_config if svg_config else SVGConfig.getDefaultConfig()
		# just throw an exception, if somebody needs it they can catch it
		SVGConfig.validateConfig(use_config, True)
		self.fromDict(use_config)

	# -------------------------------------------------------------------------------------
	def fromDict(self, svg_config:dict):
		SVGConfig.validateConfig(svg_config, throw_on_fail=True)

		self.addProperties(svg_config)

	# ------------------------------------------------------------------------------------------------------
	def __repr__(self):
		srep = ""

		# print all keys in validator
		validator = SVGConfig.getConfigValidator()
		for cur_rule_key  in validator.keys():
			# some keys are optional
			if hasattr(self, cur_rule_key):
				srep += f"   {cur_rule_key}: {getattr(self, cur_rule_key)}\n"

		return srep

	# ------------------------------------------------------------------------------------------------------
	# this is considered the source of truth for which keys a svg job config should have
	@staticmethod
	def getConfigValidator():

		def postValidateSVGConfig(config):
			if config["layers_grid_min_x"] >= config["layers_grid_max_x"]:
				return (False, f"layers_grid_min_x({config['layers_grid_min_x']}) >= layers_grid_max_x({config['layers_grid_max_x']})")
			# because SVG Y coordinates decrease as you move "up" in screen space
			if config["layers_grid_min_y"] >= config["layers_grid_max_y"]:
				return (False, f"layers_grid_min_y({config['layers_grid_min_y']}) >= layers_grid_max_y({config['layers_grid_max_y']})")
			return True
		
		notch_config_validator = {
			"count" : { "required":True, "type":int, "validation_fn" : validateIsPositive },
			"width" : { "required":True, "type":float, "validation_fn" : validateIsPositive },
			"depth" : { "required":True, "type":float, "validation_fn" : validateIsPositive },
			# distance from end of slice to outermost notch(es)
			"distance_from_ends" : { "required":False, "type":float, "validation_fn" : validateIsPositive }
		}

		def validateNotchConfig(val, key):
			# TODO: not the greatest, this should be handled by the validator itself!
			return validateDict(val, notch_config_validator, True)

		return {
			"slice_width_inches" : { "required":True, "type": float, "validation_fn" : validateIsPositive  },
			"vertical_scale" : { "required":True, "type": float, "validation_fn" : validateIsPositive  },
			"smoothed" : { "required":True, "type": bool },
			"svg_base_filename" : { "required":True, "type": str },
			"layers_grid_min_x" : { "required":True, "type": float },
			"layers_grid_max_x" : { "required":True, "type": float },
			"layers_grid_min_y" : { "required":True, "type":float },
			"layers_grid_max_y" : { "required":True, "type": float },
			"base_inches" : { "required":True, "type":float, "validation_fn" : validateIsPositive },
			"bottom_notch_config": { "required":False, "type":dict, "validation_fn": validateNotchConfig },
			validateDict_PostValidateFnKey : postValidateSVGConfig
		}

	# ------------------------------------------------------------------------------------------------------
	@staticmethod
	def getDefaultConfig():
		# these defaults are based off of my specific needs
		default_config = {
			"slice_width_inches" : 10.0,
			"vertical_scale" : 1.0,
			"smoothed" : True,
			"svg_base_filename" : "earthslicer_default",
			"layers_grid_min_x" : 0.0,
			"layers_grid_max_x" : 20.0,
			"layers_grid_min_y" : 0.0,
			"layers_grid_max_y" : 12.0,
			"base_inches" : 1.0
		}
		# just validate this every time with exception
		SVGConfig.validateConfig(default_config, True)
		return default_config

	# -------------------------------------------------------------------------------------
	@staticmethod
	def validateConfig(svg_config: dict, throw_on_fail:bool = True) -> bool:
		validation_result = validateDict(svg_config, SVGConfig.getConfigValidator(), throw_on_fail = throw_on_fail, trace_enabled=False)

		return validation_result

# -------------------------------------------------------------
# end class SVGConfig

# run this test every import
checkValidator(SVGConfig.getConfigValidator())


# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------
if __name__ == "__main__":
	from support.TestSupport import testForException, testForNoException

	print("----- SVG Config Test -----")

	print("---- checking validator ----")
	checkValidator(SVGConfig.getConfigValidator())
	print("done checking validator")

	# validate the defaults
	print("---- validating defaults ----")
	validateDict(SVGConfig.getDefaultConfig(), SVGConfig.getConfigValidator())
	print("done validating defaults")

	print()
	print("testing constructor(None) returns default config:")
	test_default_config = SVGConfig(None)
	print(f"result:")
	print(test_default_config)

	print()
	print("testing some faulty configs to construtor")
	bad_config = SVGConfig.getDefaultConfig()
	bad_config["slice_svg_length_inches"] = 10	# subtle-ish type error (not a float)
	testForException("exception for incorrect slice_svg_length_inches type", lambda: SVGConfig(bad_config))

	print()
	bad_config = SVGConfig.getDefaultConfig()
	bad_config["svg_base_filename"] = {"foo":1} # a more subtle error, this is not a valid slice dir
	testForException("svg_base_filename wrong type", lambda: SVGConfig(bad_config))

	print()
	negative_slice_width_inches_config = SVGConfig.getDefaultConfig()
	negative_slice_width_inches_config["slice_width_inches"] = -1.0
	testForException("slice width inches < 0", lambda: SVGConfig(negative_slice_width_inches_config))

	print()
	# test post validate
	bad_config = SVGConfig.getDefaultConfig()
	bad_config["layers_grid_start_x"] = 1
	bad_config["layers_grid_max_x"] = 1
	testForException("svg post config start_x < max_x", lambda: SVGConfig(bad_config))

	bad_config = SVGConfig.getDefaultConfig()
	bad_config["layers_grid_start_y"] = 1
	bad_config["layers_grid_min_y"] = 1
	testForException("svg post config start_y > min_x", lambda: SVGConfig(bad_config))

	bad_config = SVGConfig.getDefaultConfig()
	bad_config["layers_grid_start_y"] = -10
	bad_config["layers_grid_min_y"] = 10
	testForException("2nd test svg post config start_y > min_x", lambda: SVGConfig(bad_config))

	print()
	print("a passing case")
	good_config = SVGConfig.getDefaultConfig()
	good_config["svg_base_filename"] = "test_filename"
	good_config["slice_svg_length_inches"] = 5.0
	good_config["vertical_scale"] = 2.5
	print(f"should match: {good_config}")

	good_config_instance = SVGConfig(good_config)

	print("result:")
	print(good_config_instance)
	