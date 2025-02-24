import pytest

from SVGConfig import SVGConfig

# --------------------------------------------------------------------------
default_config_dict = {
	"slice_width_inches" : 14.0,
	"vertical_scale" : 1.75,
	"svg_base_filename" : "test_base_filename",
	"smoothed" : False,
	"layers_grid_min_x" : 0.0,
	"layers_grid_max_x" : 30.0,
	"layers_grid_min_y" : 0.0,
	"layers_grid_max_y" : 20.0,
	"base_inches" : 0.5,
	"bottom_notch_config" : {
		"count" : 4,
		"width" : 0.09,
		"depth" : 0.125,
		"distance_from_ends" : 1.0 }
}

class TestSVGConfig:
	# --------------------------------------------------------------------------
	def test_getSchema(self):
		config_schema = SVGConfig.getSchema()

		assert type(config_schema) == dict

	# --------------------------------------------------------------------------
	def test_configBecomesClassAttributes(self):
		test_config = SVGConfig(default_config_dict)

		for cur_schema_key in default_config_dict:
			assert hasattr(test_config, cur_schema_key)

		# spot check some values
		assert test_config.svg_base_filename == default_config_dict["svg_base_filename"]
		assert test_config.vertical_scale == default_config_dict["vertical_scale"]
		assert test_config.bottom_notch_config["count"] == default_config_dict["bottom_notch_config"]["count"]

	# --------------------------------------------------------------------------
	def test_badConfigThrowsError(self):
		# can't test all combos, and it's not the job of this test file to know the schema anyway, but we'll test that a
		# bad config throws an error
		# note: missing something...
		config_dict = {
			"slice_width_inches" : 14.0,
			"vertical_scale" : 1.75,
			"svg_base_filename" : "test_base_filename",
			"smoothed" : False,
			# "layers_grid_min_x" : 0.0,
			"layers_grid_max_x" : 30.0,
			"layers_grid_min_y" : 0.0,
			"layers_grid_max_y" : 20.0,
			"base_inches" : 0.5,
			"bottom_notch_config" : {
				"count" : 4,
				"width" : 0.09,
				"depth" : 0.125,
				"distance_from_ends" : 1.0 }
		}

		with pytest.raises(Exception):
			test_config = SVGConfig(config_dict)

	# --------------------------------------------------------------------------
	def test_noBottomNotchConfigBecomesNone(self):
		# note: missing bottom notch should be allowed
		config_dict = {
			"slice_width_inches" : 14.0,
			"vertical_scale" : 1.75,
			"svg_base_filename" : "test_base_filename",
			"smoothed" : False,
			"layers_grid_min_x" : 0.0,
			"layers_grid_max_x" : 30.0,
			"layers_grid_min_y" : 0.0,
			"layers_grid_max_y" : 20.0,
			"base_inches" : 0.5
		}

		test_config = SVGConfig(config_dict)

		assert test_config.bottom_notch_config == None
