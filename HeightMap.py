# HeightMap
# maps lat,long coordinates to a value (intended to be height in feet)
# Notes:
#		* lat/long coordinates are reduced to a specified amount of precision
#		  i.e. - it doesn't store every coordinate, but a sub set of them
#		* Retains discovered values in a dict (map).
#		* You specify the function that will fill the map for unknown coordinates.
#		* A precision setting of 0.0001 degrees (4 decimal places) should represent 
# 		  about 30 feet, probably more than good enough for my use
import jsons

# ------------------------------
# SETTINGS
height_map_default_precision = 4


# ------------------------------
class HeightMap():
	def __init__(self, precision = height_map_default_precision, name = "hmapdefault", log_fn = None):
		# precision at which coordinates are track
		self.precision = precision if precision else height_map_default_precision
		# multiplier that shifts decimals up/down when reducing precision
		self.decimal_shifter = pow(10,self.precision)

		self.log = log_fn if log_fn else self.nop_log

		self.name = name

		# holds discovered points
		self.map = {}

	def nop_log(self, message):
			pass

	# -----------------------------------------------------------
	def logConfig(self, log_fn):
		log_fn(f"HeightMap {self.name} config:")
		log_fn(f"\tprecision: {self.precision}")
		log_fn(f"\tdecimal_shifter: {self.decimal_shifter}")
		log_fn(f"\tmap size: {len(self.map.keys())}")

	# -----------------------------------------------------------
	def __repr__(self):
		string_rep = f"HeightMap {self.name}:\n"
		string_rep += f"\tprecision: {self.precision}\n"
		string_rep += f"\tdecimal_shifter: {self.decimal_shifter}\n"
		string_rep += f"\tmap size: {len(self.map.keys())}\n"

		return string_rep

	# -----------------------------------------------------------
	def numToPrecision(self, num):
		as_int = int(num * self.decimal_shifter)		# shift left, make to int
		to_precision = as_int / self.decimal_shifter	# shift right
		return to_precision

	# -----------------------------------------------------------
	def get(self, lat, long, fn_add_if_empty):
		self.log(f"get({lat},{long})")

		lat_adjust = self.numToPrecision(lat)
		long_adjust = self.numToPrecision(long)
		coordinate_string = f"{lat_adjust},{long_adjust}"

		if not coordinate_string in self.map:
			self.log("not found, adding...")
			self.map[coordinate_string] = fn_add_if_empty()

		return_val = self.map[coordinate_string]

		self.log(f"returning: {return_val}")

		return return_val

	# -----------------------------------------------------------
	def toDataObj(self):
		return { "name":self.name, "precision": self.precision, "map": self.map }

	# -----------------------------------------------------------
	def fromDataObj(self, data_obj):
		self.precision = data_obj["precision"]
		self.decimal_shifter = pow(10,self.precision)

		if "name" in data_obj.keys():
			self.name = data_obj["name"]

		self.map = data_obj["map"]


# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------
if __name__ == "__main__":
	from getHeightUSGS import getHeightUSGS
	from TimingTrace import TimingTrace

	llhm_timer = TimingTrace("HeightMap")
	llhm_timer.start()

	# gets a series of points and displays results
	# not supersampling from the data
	test_precision = 4
	test_map = HeightMap(test_precision)

	# reasonably steep slope on the west flank of Mt. Whitney
	test_lat = 36.569325
	test_long = -118.297750

	# move east in little steps at given precision
	long_increment = 1 / pow(10,test_precision)
	test_count = 16

	print(f"test_precision: {test_precision}")
	print(f"lat_increment: {long_increment}")

	feet_per_degree = 364488.0
	print(f"inc. should represent about {feet_per_degree * long_increment} feet")

	print(f"doing {test_count} tests...")

	for cur_test in range(test_count):		
		test_map.get(test_lat, test_long, lambda : getHeightUSGS([test_lat, test_long]) )
		print()
		test_long += long_increment

		llhm_timer.mark(f"test {test_long}")

	print(test_map)
	print()
	print(llhm_timer)