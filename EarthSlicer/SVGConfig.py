# configuration of slice job svg output
from jsonschema import Draft7Validator

# ------------------------------------------------------------------------------------------------------
class SVGConfig():
	def __init__(self, svg_config: dict = None):
		# just throw an exception, if somebody needs it they can catch it
		SVGConfig.validateConfig(svg_config, True)

		self.bottom_notch_config = None

		for cur_key in SVGConfig.getSchema()["properties"]:
			if cur_key in svg_config:
				self[cur_key] =  svg_config[cur_key]

		# these are hardwired for now I guess
		self.layers_grid_x_spacing = 0.5
		self.layers_grid_y_spacing = 0.25

		self.repr_keys = [cur_val_key for cur_val_key in svg_config.keys()]

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
	def getSchema():
		return {
			"type":"object",
			"properties":
			{
				"slice_width_inches" : { "type" : "number" },
				"vertical_scale" : { "type" : "number" },
				"svg_base_filename" : { "type" : "string"},
				"smoothed" : { "type" : "boolean" },
				"layers_grid_min_x" : { "type" : "number" },
				"layers_grid_max_x" : { "type" : "number" },
				"layers_grid_min_y" : { "type" : "number" },
				"layers_grid_max_y" : { "type" : "number" },
				"base_inches" : { "type" : "number"},
				"bottom_notch_config" :
					{
					"type" : "object",
					"properties" : {
						"count" : { "type" : "integer" },
						"width" : { "type" : "number" },
						"depth" : { "type" : "number" },
						"distance_from_ends" : { "type" : "number" }
					}
					}
			},
			"required" : [
				"slice_width_inches",
				"vertical_scale",
				"svg_base_filename",
				"smoothed",
				"layers_grid_min_x",
				"layers_grid_max_x",
				"layers_grid_min_y",
				"layers_grid_max_y",
				"base_inches"
			]
		}

	# -------------------------------------------------------------------------------------
	@staticmethod
	def validateConfig(svg_config: dict, throw_on_fail:bool = True) -> bool:
		validation_result = True

		try:
				# check that schema itself is valid...
				schema = SVGConfig.getSchema()
				Draft7Validator.check_schema(schema)

				validator = Draft7Validator(schema)
				validator.validate(svg_config)
		except Exception as e:
			validation_result = False
			if throw_on_fail:
				raise e

		return validation_result
