from enum import Enum
from concurrent.futures import ProcessPoolExecutor

# TODO:
# 	* use vertical scale (somewhere, probably in svg translation?)
# 	* translate to svg(s), single svg w/layers? (does svgwrite support layers? if so how many? limit in Inkscape?)
# TO-DONE:
#	* dispatch multiple elevation requests to cut down on time

#  -----------------------------------------------------------------
class SliceDirection(Enum):
    NorthSouth = 1
    WestEast = 2		# west /east cause svg coords or something

#  -----------------------------------------------------------------
class Slice:
	def __init__(self, start_lat, start_long, end_lat, end_long, num_steps, direction):
		self.start_lat = start_lat
		self.start_long = start_long
		self.end_lat = end_lat
		self.end_long = end_long
		self.num_steps = num_steps
		self.slice_direction = direction
		self.points = None
		self.elevations = None
		self.minimum_elevation = None

		self.use_concurrency = False

	# ------------------------------
	def set_use_concurrency(self, use_conc = True):
		self.use_concurrency = use_conc

	# ------------------------------
	def __repr__(self) -> str:
		string_rep = f"Slice(start:{self.start_lat},{self.start_long} \
			end:{self.end_lat},{self.end_long} \
			num_steps:{self.num_steps}, \
			slice_dir:{self.slice_direction})"

		string_rep += f"\npoints: {str(self.points) if None != self.points else '???'}"
		string_rep += f"\nelevations: {self.elevations if None != self.elevations else '???'}"
		string_rep += f"\nminimum_elevation: {self.minimum_elevation if None != self.minimum_elevation else '???'}"

		return string_rep

	# ------------------------------
	def generatePoints(self):
		self.points = []
		lat_diff = self.end_lat - self.start_lat
		long_diff = self.end_long - self.start_long

		long_step = long_diff / (self.num_steps)
		lat_step = lat_diff / (self.num_steps)

		cur_lat = self.start_lat
		cur_long = self.start_long

		# think of the "steps" as existing between the numbers, instead of the numbers themselves
		for cur_step in range(self.num_steps + 1):
			self.points.append( [cur_lat, cur_long] )
			cur_lat += lat_step
			cur_long += long_step

	# ------------------------------
	def generateElevationsSerial(self, elevation_func):
		self.elevations = []
		for cur_point in self.points:
			cur_elevation = elevation_func(cur_point)
			
			self.minimum_elevation = cur_elevation if self.minimum_elevation == None else min(self.minimum_elevation, cur_elevation)
			self.minimum_elevation = min(self.minimum_elevation, cur_elevation)
			self.elevations.append(cur_elevation)

	# ------------------------------
	def generateElevationsConcurrent(self, elevation_func):
		self.elevations = []
		with ProcessPoolExecutor(4) as executor:
			chunk_size = 2
			# python returns map results in the order they are dispatched, so 
			# these /should/ always be in correct order
			elevations = list(executor.map(elevation_func, self.points, chunksize=chunk_size))

		print("elevations:")
		print(elevations)
		self.elevations = elevations
		# TODO: get minimum elevation
		self.minimum_elevation = min(self.elevations)

	# ------------------------------
	# elevation_func should (for now), just take lat,long coordinates
	def generateElevations(self, elevation_func):
		if None == self.points:
			raise Exception('Attempt to generate elevations without coordinates defined')
		
		if False == self.use_concurrency:
			self.generateElevationsSerial(elevation_func)
		else:
			self.generateElevationsConcurrent(elevation_func)


# end Slice class---------------------------------------------------
