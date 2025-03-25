from support.GTimer import gtimer

from EarthSlicer.Slice import Slice, SliceDirection
from EarthSlicer.SliceJobConfig import SliceJobConfig

# --------------------------------------------------------------------------------------------
class SliceJob():
	def __init__(self, config:SliceJobConfig, slice_step:int):
		self.config = config
		self.slice_step = slice_step
		self.slices = None
		self.minimum_elevation = None
		self.maximum_elevation = None

	# -------------------------------------------------------------------
	def numSlices(self):
		return len(self.slices) if self.slices else 0

	# -------------------------------------------------------------------
	@staticmethod
	def calcStep(start, end, number_of_points):
		difference = end - start
		step = difference / max(number_of_points - 1, 1)
		return step

	# -------------------------------------------------------------------
	# this is the length in the sliced direction
	def sliceLengthFeet(self):
		return self.config.north_south_feet if self.config.slice_direction == SliceDirection.NorthSouth else self.config.east_west_feet

	# -------------------------------------------------------------------
	# this is the length perpendicular to the sliced direction
	def sliceWidthFeet(self):
		return self.config.north_south_feet if self.config.slice_direction == SliceDirection.WestEast else self.config.east_west_feet

	# -------------------------------------------------------------------
	def minimumElevation(self):
		if not self.minimum_elevation:
			if self.slices:
				self.minimum_elevation = min(cur_slice.minimumElevation() for cur_slice in self.slices)
			else:
				raise Exception("attempting to get SliceJob minimum elevation before slices have been created")

		return self.minimum_elevation

	# -------------------------------------------------------------------
	def maximumElevation(self):
		if not self.maximum_elevation:
			if self.slices:
				self.maximum_elevation = max(cur_slice.maximumElevation() for cur_slice in self.slices)
			else:
				raise Exception("attempting to get SliceJob maximum elevation before slices have been created")

		return self.maximum_elevation

	# -------------------------------------------------------------------
	def generateSlices(self):
		slices = []

		# some messy looping shit, hey i drunk now, back off
		if self.config.slice_direction == SliceDirection.NorthSouth:
			# travel west -> east, taking those delicious north/south slices
			# so start lat and end lat are constant over the everything
			current_long = self.config.west_edge
			if self.config["number_of_slices"] > 1:
				long_step = self.calcStep(self.config.west_edge, self.config.east_edge, self.config.number_of_slices)
			else:
				long_step = 0

			# doesn't current_step and slice_num just move in lockstep?
			for current_slice_num in range(0, self.config.number_of_slices, self.slice_step):
				current_slice = Slice(	self.config.north_edge, current_long,
												self.config.south_edge, current_long,
												self.config.number_of_elevations,
												self.config.slice_direction,
												current_slice_num) # slice_num)

				slices.append(current_slice)
				current_long += long_step * self.slice_step
		else:
			# slicing west/east
			# so traveling north -> south, taking w/e slices
			current_lat = self.config.north_edge
			lat_step = self.calcStep(self.config.north_edge, self.config.south_edge, self.config.number_of_slices)

			for current_slice_num in range(0, self.config.number_of_slices, self.slice_step):
				gtimer.startTimer('generate single slice')
				current_slice = Slice(	current_lat, self.config.west_edge,
												current_lat, self.config.east_edge,
												self.config.number_of_elevations,
												self.config.slice_direction,
												current_slice_num) # slice_num)

				gtimer.markTimer('generate single slice')

				slices.append(current_slice)
				current_lat += lat_step * self.slice_step

		self.slices = slices
