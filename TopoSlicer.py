import jsons

from LogChannels import log

from Slice import Slice, SliceDirection

log.addChannel("slicer", "slicer")
log.setChannel("slicer", False)

# TODO:
#	* track overall min/max?
#	* version that takes data obj? seems unnecessary with height map in play

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class TopoSlicer:
	def __init__(self):
		self.config = None
		self.slices = None

	# ------------------------------
	def __repr__(self) -> str:
		string_rep = f"TopoSlicer\n"
		string_rep += f"id: {id(self)}\n"
		string_rep += f"config: \n"
		string_rep += "None" if not self.config else jsons.dumps(self.config, {"indent":3}) + "\n"
		string_rep += f"slices: " + "None" if not self.slices else str(self.slices) + "\n"

		return string_rep

	# ------------------------------------------
	# returns step
	@staticmethod
	def calcStep(start, end, number_of_points):
		difference = end - start

		step = difference / (number_of_points - 1)

		return step

	# ------------------------------------------
	# returns properties expected in a TopoSlicer config
	@staticmethod
	def configProperties():
		return (	
			"slice_direction",
			"number_of_slices",
			"number_of_elevations",
			"north_edge",
			"west_edge",
			"south_edge",
			"east_edge")
	
	# ------------------------------------------
	@staticmethod
	def validateConfig(test_config, throw_on_fail = True):
		valid_config = True
		result_message = ""
		missing_keys = []
		for cur_prop in TopoSlicer.configProperties():
			if not cur_prop in test_config:
				valid = False
				missing_keys.append(cur_prop)

		if len(missing_keys):
			result_message = f'Invalid TopoSlices config, missing keys: ' + str(missing_keys)
			if throw_on_fail:
				raise Exception(result_message)

		return {"result":valid_config, "message":result_message}

	# ------------------------------------------
	# generates slices from given config
	def generateSlices(self, config):
		log.slicer("generating slices...")

		TopoSlicer.validateConfig(config)
		# get slice relevant parts of config
		self.config = { cp : config[cp] for cp in self.configProperties()}

		self.slices  = []
		slice_num = 0

		# some messy looping shit, hey i drunk now, back off
		if config["slice_direction"] == SliceDirection.NorthSouth:
			# travel west -> east, taking those delicious north/south slices
			# so start lat and end lat are constant over the everything
			current_long = config["west_edge"]
			long_step = self.calcStep(config["west_edge"], config["east_edge"], config["number_of_slices"])

			for current_step in range(config["number_of_slices"]):
				# do some shit
				current_slice = Slice(	config["north_edge"], current_long,
												config["south_edge"], current_long,
												config["number_of_elevations"],
												config["slice_direction"],
												f"slice_{slice_num}")

				self.slices.append(current_slice)
				slice_num += 1
				current_long += long_step
		else:
			# slicing west/east
			# so traveling north -> south, taking w/e slices
			current_lat = config["north_edge"]
			lat_step = self.calcStep(config["north_edge"], config["south_edge"], config["number_of_slices"])

			for current_step in range(config["number_of_slices"]):
				current_slice = Slice(	current_lat, config["west_edge"],
												current_lat, config["east_edge"],
												config["number_of_elevations"],
												config["slice_direction"],
												f"slice_{slice_num}")
				
				self.slices.append(current_slice)
				slice_num += 1
				current_lat += lat_step

		log.slicer(f"generated {len(self.slices)} slices")

	# ------------------------------------------
	# serially generates elevations
	async def getElevationsAsync(self, elevation_func):
		if None == self.slices:
			raise Exception('Attempt to get elevations without slices defined')
		
		log.slicer(f"getElevationsAsync()")

		for cur_slice in self.slices:
			log.slicer(f'slice: {cur_slice.name}')
			await cur_slice.getElevationsAsync(elevation_func)

	# ------------------------------------------
	# serially generates elevations
	def getElevations(self, elevation_func):
		if None == self.slices:
			raise Exception('Attempt to get elevations without slices defined')
		
		log.slicer(f"getElevations()")

		for cur_slice in self.slices:
			log.slicer(f'slice: {cur_slice.name}')
			cur_slice.getElevations(elevation_func)

	# ------------------------------------------
	def toDataObj(self):
		# slices to data obj array
		slices_data = [ cur_slice.toDataObj() for cur_slice in self.slices]

		return { "config": self.config, "slices": slices_data }

	# ------------------------------------------
	def fromDataObj(self, data_obj):
		# TODO: move validation to function

		if not "config" in data_obj:
			raise Exception("TopoSlices.fromDataObj(): Invalid data_obj, missing property 'config'")

		self.config = data_obj["config"]
		TopoSlicer.validateConfig(self.config)

		# convert slice direction to Class enum
		slice_dir_enum = SliceDirection.toSliceDirection(self.config["slice_direction"])
		self.config["slice_direction"] = slice_dir_enum

		if not "slices" in data_obj:
			raise Exception("TopoSlices.fromDataObj(): Invalid data_obj, missing property 'slices'")

		# validate data_obj has expected number of slices?
		expected_slices_num = self.config["number_of_slices"]
		if len(data_obj["slices"]) != expected_slices_num:
			raise Exception(f"TopoSlices.fromDataObj(): Invalid data_obj, expected {expected_slices_num} slices, data contains {len(data_obj['slices'])}")

		self.slices = []
		# turn slice data into Slices object instances
		for cur_slice_data in data_obj["slices"]:
			self.slices.append(Slice().fromDataObj(cur_slice_data))

# end TopoSlices class---------------------------------------------------