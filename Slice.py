from enum import Enum
import asyncio

from unitsSupport import *
from support.LogChannels import log
from support.GTimer import gtimer

# TODO:
#	* fingerprint for validation errors (coordinates)  (huh? was I drunk when I wrote this?)
#	* configurable slice chunk size
#	* friendlier output around elevation progress

# TO-DONE:
#	* probably need to throttle the number of async requests somehow
#	* remember max elevation
#	* dispatch multiple elevation requests to cut down on time
#	* no need to keep points around, generate them on demand when elevations are needed then dump them

log.addChannel("slice", "slice")
log.setChannel("slice", False)

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
	def __init__(	self,
	      			start_lat = None,
						start_long = None,
						end_lat = None,
						end_long = None,
						number_of_elevations = None,
						direction = None,
						slice_index = 0):
		self.start_lat = start_lat
		self.start_long = start_long
		self.end_lat = end_lat
		self.end_long = end_long
		self.number_of_elevations = number_of_elevations
		self.slice_direction = direction
		self.slice_index = slice_index

		# generated data
		self.elevations = None
		self.minimum_elevation = None
		self.maximum_elevation = None

		log.slice(f"constructed slice: {self.slice_index}")

	# ------------------------------
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
		gtimer.startTimer(f"{self.slice_index}_genpoints")
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

		gtimer.markTimer(f"{self.slice_index}_genpoints", "generate slice points")

		log.slice(f"generated {len(points)} points")
		log.slice(f"{points}")
		return points

	# ------------------------------
	# serial form
	# elevation_func will be sent (lat,long):list
	def getElevations(self, elevation_func):
		gtimer.startTimer(f"{self.slice_index}_gen_elevations_serial")

		points = self.generatePoints()
		self.elevations = []

		for cur_point in points:
			cur_elevation = elevation_func(cur_point)
			self.elevations.append(cur_elevation)

		self.minimum_elevation = min(self.elevations)
		self.maximum_elevation = max(self.elevations)

		gtimer.markTimer(f"{self.slice_index}_gen_elevations_serial", "sliceGetElevsSerial")

	# ------------------------------
	# async form
	async def getElevationsAsync(self, elevation_func):
		gtimer.startTimer(f"{self.slice_index}_getElevAsync")
		points = self.generatePoints()
		self.elevations = []

		# local func to get elevation and put it on a specific key in a map dict
		# because elevations may arrive back out of order
		async def getElevationToIndex(point, elevation_map, point_index):
			elevation = await elevation_func(point)
			elevation_map[f"{point_index}"] = elevation	# insert this elevation with index as key

		cur_chunk_index = 0
		chunk_size = 20
		log.slice(f"slice todo: configurable slice chunk size")

		# this allows proper ordering of elevations, because they can arrive out of order from the async get
		# keys are just the numeric index of the point
		point_index_to_elevation_map = {}

		while cur_chunk_index < len(points):
			tasks = []
			for cur_point_index in range(cur_chunk_index, min(len(points), cur_chunk_index + chunk_size)):
				tasks.append(getElevationToIndex(points[cur_point_index], point_index_to_elevation_map, cur_point_index))

			log.slice(f"queued {len(tasks)} elevation requests")
			await asyncio.gather(*tasks)
	
			cur_chunk_index += chunk_size

		# now turn elevation index map into ordered list
		# there should be a key in the map for every point index
		for cur_index in range(len(points)): 
			self.elevations.append(point_index_to_elevation_map[f"{cur_index}"]) # key error here means map wasn't fully built!

		self.minimum_elevation = min(self.elevations)
		self.maximum_elevation = max(self.elevations)

		gtimer.markTimer(f"{self.slice_index}_getElevAsync", "slice get elevations async")

	# ------------------------------------------
	def sliceLengthDegrees(self):
		slice_length_degrees = 0
		if self.slice_direction == SliceDirection.NorthSouth:
			slice_length_degrees = abs(self.end_lat - self.start_lat)
		else:
			slice_length_degrees = abs(self.end_long - self.start_long)

		return slice_length_degrees

	# ------------------------------------------
	def sliceLengthMiles(self):
		if self.slice_direction == SliceDirection.NorthSouth:
			miles = latitudeDegreesToMiles(self.sliceLengthDegrees())
		else:
			# since slices are taken north/south, the end_lat is the southern edge
			miles = longitudeDegreesToMiles(self.sliceLengthDegrees(), self.end_lat)

		return miles

	# ------------------------------------------
	def sliceLengthFeet(self):
		return self.sliceLengthMiles() * feetPerMile()

	# ------------------------------------------
	def __getitem__(self, item):
			return getattr(self, item)

	# ------------------------------------------
	def __setitem__(self, key, value):
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
