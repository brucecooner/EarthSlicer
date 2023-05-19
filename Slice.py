from enum import Enum
from concurrent.futures import ProcessPoolExecutor

# TODO:
# fingerprint for validation errors (coordinates)

# TO-DONE:
#	* remember max elevation
#	* dispatch multiple elevation requests to cut down on time
#	* no need to keep points around, generate them on demand when elevations are needed then dump them

#  -----------------------------------------------------------------
class SliceDirection(Enum):
	NorthSouth = 1
	WestEast = 2		# west /east cause svg coords or something

	def isValidSliceDir(test_value):
		slice_values = [value.name for value in SliceDirection]
		return test_value in slice_values

	def toSliceDirection(value):
		if not SliceDirection.isValidSliceDir( value ):
			raise Exception(f'TopoSlices.fromDataObj(): Invalid SliceDirection: {value}')
		
		return SliceDirection[value]

#  -----------------------------------------------------------------
class Slice:
	def __init__(self, start_lat = None, start_long = None, end_lat = None, end_long = None, number_of_elevations = None, direction = None):
		self.start_lat = start_lat
		self.start_long = start_long
		self.end_lat = end_lat
		self.end_long = end_long
		self.number_of_elevations = number_of_elevations
		self.slice_direction = direction

		# generated data
		self.elevations = None
		self.minimum_elevation = None
		self.maximum_elevation = None

		# config
		self.use_concurrency = False

	@staticmethod
	def dataObjFields():
		# fields written to/from data obj
		return [
			"start_lat",
			"start_long",
			"end_lat",
			"end_long",
			"number_of_elevations",
			"slice_direction",
			"minimum_elevation",
			"maximum_elevation",
			"elevations"
		]

	# ------------------------------
	def set_use_concurrency(self, use_conc = True):
		self.use_concurrency = use_conc

	# ------------------------------
	def __repr__(self) -> str:
		string_rep = f"{{Slice:\n"
		string_rep += f"\tstart:{self.start_lat},{self.start_long}\n"
		string_rep += f"\tend:{self.end_lat},{self.end_long},\n "
		string_rep += f"\tnumber_of_elevations:{self.number_of_elevations},\n"
		string_rep += f"\tslice_direction:{self.slice_direction}\n"

		string_rep += f"\tminimum_elevation: {self.minimum_elevation if None != self.minimum_elevation else '???'}\n"
		string_rep += f"\tmaximum_elevation: {self.maximum_elevation if None != self.maximum_elevation else '???'}\n"
		string_rep += f"\televations: {self.elevations if None != self.elevations else '???'}\n}}"

		return string_rep

	# ------------------------------
	def generatePoints(self):
		points = []
		lat_diff = self.end_lat - self.start_lat
		long_diff = self.end_long - self.start_long

		long_step = long_diff / (self.number_of_elevations - 1)
		lat_step = lat_diff / (self.number_of_elevations - 1)

		cur_lat = self.start_lat
		cur_long = self.start_long

		for cur_step in range(self.number_of_elevations):
			points.append( [cur_lat, cur_long] )
			cur_lat += lat_step
			cur_long += long_step

		return points

	# ------------------------------
	def generateElevationsSerial(self, elevation_func, points):
		self.elevations = []
		for cur_point in points:
			cur_elevation = elevation_func(cur_point)
			self.elevations.append(cur_elevation)

	# ------------------------------
	def generateElevationsConcurrent(self, elevation_func, points):
		self.elevations = []
		with ProcessPoolExecutor(4) as executor:
			chunk_size = 2
			# python returns map results in the order they are dispatched, so 
			# these /should/ always be in correct order
			elevations = list(executor.map(elevation_func, points, chunksize=chunk_size))

		self.elevations = elevations

	# ------------------------------
	# elevation_func should (for now), just take lat,long coordinates
	def generateElevations(self, elevation_func, use_concurrency ):
		points = self.generatePoints()

		if False == use_concurrency:
			self.generateElevationsSerial(elevation_func, points)
		else:
			self.generateElevationsConcurrent(elevation_func, points)

		self.minimum_elevation = min(self.elevations)
		self.maximum_elevation = max(self.elevations)

	# ------------------------------------------
	# calculate length of slices in miles (feet?)
	def sliceLengthDegrees(self):
		slice_length_degrees = 0
		if self.slice_direction == SliceDirection.NorthSouth:
			slice_length_degrees = abs(self.end_lat - self.start_lat)
		else:
			slice_length_degrees = abs(self.end_long - self.start_long)

		return slice_length_degrees

	# ------------------------------------------
	def __getitem__(self, item):
			return getattr(self, item)

	# ------------------------------------------
	def __setitem__(self, key, value):
			# print('Slice.setitem called')
			return setattr(self, key, value)

	# ------------------------------
	def toDataObj(self):
		data_obj = { cur_field:self[cur_field] for cur_field in self.dataObjFields() }
		# data_obj["elevations"] = self.elevations

		return data_obj

	# ------------------------------------------
	@staticmethod
	def validateDataObj(validate_data_obj, throw_on_fail = True):
		valid_data = True
		result_message = ""
		missing_keys = []
		# note: adding elevations here
		expected_fields = Slice.dataObjFields()
		for cur_prop in expected_fields:
			if not cur_prop in validate_data_obj:
				valid_data = False
				missing_keys.append(cur_prop)

		if len(missing_keys):
			valid_data = False
			result_message = f'Invalid Slices data_obj, missing keys: ' + str(missing_keys)
			if throw_on_fail:
				raise Exception(result_message)

		# only validate number_of_elevations if valid
		if valid_data:
			# validate number of elevations
			expected_elevations_num = validate_data_obj["number_of_elevations"]

			if len(validate_data_obj["elevations"]) != expected_elevations_num:
				valid_data = False
				result_message = f"Slice.fromDataObj(): Invalid data_obj, expected {expected_elevations_num} elevations, data contains {len(validate_data_obj['elevations'])}"
				if throw_on_fail: 
					raise Exception(result_message)

		return {"result":valid_data, "message":result_message}

	# ------------------------------------------
	def fromDataObj(self, data_obj):
		Slice.validateDataObj(validate_data_obj = data_obj)

		for cur_field in self.dataObjFields():
			self[cur_field] = data_obj[cur_field]

		# convert slice direction to Class enum
		slice_dir_enum = SliceDirection.toSliceDirection(self.slice_direction)
		self.slice_direction = slice_dir_enum

		self.elevations = data_obj["elevations"]

		return self

# end Slice class---------------------------------------------------
