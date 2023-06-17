# configuration of a slice job svg
from support.ClassFromDict import ClassFromDict
from support.ValidateDict import validateDict, checkValidator


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
		return {
			"slice_svg_length_inches" : { "required":True, "type": float },
			"vertical_scale" : { "required":True, "type": float },
			"svg_base_filename" : { "required":True, "type": str }
		}

	# ------------------------------------------------------------------------------------------------------
	@staticmethod
	def getDefaultConfig():
		default_config = {
			"slice_svg_length_inches" : 10.0,
			"vertical_scale" : 1.0,
			"svg_base_filename" : "earthslicer_default"
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
	print("a passing case")
	good_config = SVGConfig.getDefaultConfig()
	good_config["svg_base_filename"] = "test_filename"
	good_config["slice_svg_length_inches"] = 5.0
	good_config["vertical_scale"] = 2.5
	print(f"should match: {good_config}")

	good_config_instance = SVGConfig(good_config)

	print("result:")
	print(good_config_instance)
	