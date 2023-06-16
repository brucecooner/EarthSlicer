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
from threading import Lock
import random

import asyncio

from support.LogChannels import log


log.addChannel("hmap", "hmap")
log.setChannel("hmap", False)

# ------------------------------
# SETTINGS
height_map_default_precision = 4

# ------------------------------
class HeightMap():
	def __init__(self, precision = height_map_default_precision, name = "hmapdefault"):
		# precision at which coordinates are track
		self.precision = precision if precision else height_map_default_precision
		# multiplier that shifts decimals up/down when reducing precision
		self.decimal_shifter = pow(10,self.precision)
		self.name = name

		# holds discovered points
		self.map = {}

		# stats
		self.total_queries = 0
		self.total_queries_async = 0
		self.total_misses = 0

	# -----------------------------------------------------------
	def __repr__(self):
		string_rep = f"HeightMap {self.name} info:\n"
		string_rep += f"\tprecision: {self.precision}\n"
		string_rep += f"\tdecimal_shifter: {self.decimal_shifter}\n"
		string_rep += f"\tmap size: {len(self.map.keys())}\n"

		return string_rep

	# -----------------------------------------------------------
	def Stats(self):
		string_rep = f"HeightMap {self.name} stats:\n"
		string_rep += f"\tsize: {len(self.map)}\n"
		string_rep += f"\ttotal_queries: (serial/async) {self.total_queries}/{self.total_queries_async}\n"
		string_rep += f"\ttotal_misses: {self.total_misses}\n"
		return string_rep

	# -----------------------------------------------------------
	def numToPrecision(self, num):
		as_int = int(num * self.decimal_shifter)		# shift left, make to int
		to_precision = as_int / self.decimal_shifter	# shift right
		return to_precision

	# -----------------------------------------------------------
	def get(self, lat, long, fn_on_miss):
		self.total_queries += 1

		log.hmap(f"get({lat},{long}) ")

		lat_adjust = self.numToPrecision(lat)
		long_adjust = self.numToPrecision(long)
		coordinate_string = f"{lat_adjust},{long_adjust}"

		if not coordinate_string in self.map:
			log.hmap(f"not found...")
			self.total_misses += 1
			add_val = fn_on_miss((lat_adjust, long_adjust))
			self.map[coordinate_string] = add_val
			self.map_changed = True
			log.hmap(f"added {add_val}")

		log.hmap(f"returning: {self.map[coordinate_string]}")

		return self.map[coordinate_string]

	# -----------------------------------------------------------
	async def getAsync(self, lat, long, fn_on_miss):
		self.total_queries_async += 1
		log.hmap(f"getAsync({lat},{long}) ")

		lat_adjust = self.numToPrecision(lat)
		long_adjust = self.numToPrecision(long)
		coordinate_string = f"{lat_adjust},{long_adjust}"

		if not coordinate_string in self.map:
			# log.hmap(f"not found...")
			self.total_misses += 1
			add_value = await fn_on_miss((lat_adjust, long_adjust))
			self.map[coordinate_string] = add_value
			self.map_changed = True
			log.hmap(f"added {add_value} for {coordinate_string}")

		log.hmap(f"for {coordinate_string} returning: {self.map[coordinate_string]}")

		return self.map[coordinate_string]


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

		self.map_changed = False

	# -----------------------------------------------------------
	# returns true if state of map has changed since fromDataObj() was called
	def changed(self):
		return hasattr(self, "map_changed") and self.map_changed


# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------
if __name__ == "__main__":
	from USGS_EPQS import getHeightUSGS
	from support.TimingTrace import TimingTrace

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