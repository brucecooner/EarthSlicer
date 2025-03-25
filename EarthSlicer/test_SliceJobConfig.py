import pytest

from EarthSlicer.Slice import SliceDirection
from EarthSlicer.SliceJobConfig import SliceJobConfig

default_config_dict = {
	"slice_direction" : "NorthSouth",
	"number_of_elevations" : 10,
	"number_of_slices" : 100,
	"north_edge" : 1.0,
	"south_edge" : 0.1,
	"east_edge" : 0.0,
	"west_edge" : 1.0
}

class TestSliceJobConfig:

	# --------------------------------------------------------------------------
	def test_getConfigSchema(self):
		config_schema = SliceJobConfig.getConfigSchema()

		assert type(config_schema) == dict

	# --------------------------------------------------------------------------
	def test_getMetricsSchema(self):
		metrics_schema = SliceJobConfig.getMetricsSchema()

		assert type(metrics_schema) == dict

	# --------------------------------------------------------------------------
	def test_configBecomesClassAttributes(self):
		test_config = SliceJobConfig(default_config_dict)

		# slice_direction is a typed value
		assert type(test_config.slice_direction) == SliceDirection
		assert test_config.slice_direction == SliceDirection.toSliceDirection(default_config_dict["slice_direction"])

		for cur_schema_key in SliceJobConfig.getConfigSchema()["required"]:
			if cur_schema_key != 'slice_direction':	# ugh, carve out typed value
				assert getattr(test_config, cur_schema_key) == default_config_dict[cur_schema_key]

	# --------------------------------------------------------------------------
	def test_metricsAreCalculated(self):
		test_config = SliceJobConfig(default_config_dict)

		# assert all schema-specified keys are present
		test_config_dir = dir(test_config)
		for cur_schema_key in SliceJobConfig.getMetricsSchema()["required"]:
			assert cur_schema_key in test_config_dir

		# test some easily calculated metrics
		assert test_config.east_west_degrees == default_config_dict["west_edge"] - default_config_dict["east_edge"]
		assert test_config.north_south_degrees == default_config_dict["north_edge"] - default_config_dict["south_edge"]

	# --------------------------------------------------------------------------
	def test_invalidSliceDir(self):
		bad_config = default_config_dict
		bad_config["slice_direction"] = "invalid_direction"

		with pytest.raises(Exception):
			test_config = SliceJobConfig(bad_config)

	# --------------------------------------------------------------------------
	def test_minimumSlicesConstraint(self):
		bad_config = default_config_dict
		bad_config["number_of_slices"] = 0

		with pytest.raises(Exception):
			test_config = SliceJobConfig(bad_config)

	# --------------------------------------------------------------------------
	def test_minimumElevationsConstraint(self):
		bad_config = default_config_dict
		bad_config["number_of_elevations"] = 0

		with pytest.raises(Exception):
			test_config = SliceJobConfig(bad_config)

	# print()
	# north_lt_south_config = SliceJobConfig.getDefaultConfig()
	# north_lt_south_config["north_edge"] = -1.0
	# north_lt_south_config["south_edge"] = 0.0
	# testForException("exception for north edge < south edge", lambda: SliceJobConfig(north_lt_south_config))

	# print()
	# east_lt_west_config = SliceJobConfig.getDefaultConfig()
	# east_lt_west_config["east_edge"] = -33.0
	# east_lt_west_config["west_edge"] = -31.0
	# testForException("exception for east edge < west edge", lambda: SliceJobConfig(east_lt_west_config))

	# print()
	# print("a passing case")
	# good_config = SliceJobConfig.getDefaultConfig()
	# good_config["slice_direction"] = "WestEast"
	# good_config["number_of_elevations"] = 78
	# good_config["east_edge"] = -9.1
	# good_config["west_edge"] = -10.1
	# good_config_instance = SliceJobConfig(good_config)

	# print("result:")
	# print(good_config_instance)
	# # verify that slice direction was converted to enum type
	# print(f"verify type of slice direction: {type(good_config_instance.slice_direction)}")
