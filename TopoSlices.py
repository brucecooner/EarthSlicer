import jsons

from Slice import Slice, SliceDirection

# TODO:
#	* track overall min/max?

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class TopoSlices:
	# TODO: version that takes data obj
	def __init__(self):
		self.config = None
		self.slices = None

	# ------------------------------
	def __repr__(self) -> str:
		string_rep = f"TopoSlices\n"
		string_rep += f"config: \n"
		string_rep += "None" if not self.config else jsons.dumps(self.config, {"indent":3}) + "\n"
		string_rep += f"slices: " + "None" if not self.slices else str(self.slices) + "\n"

		return string_rep

	# ------------------------------------------
	# returns step
	@staticmethod
	def calcStep(start, end, num_steps):
		diff = end - start

		step = diff / (num_steps)

		return step

	# ------------------------------------------
	# returns properties expected in a TopoSlicer config
	@staticmethod
	def configProperties():
		return (	
			"slice_direction",
			"num_NS_steps",
			"num_WE_steps",
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
		for cur_prop in TopoSlices.configProperties():
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
		TopoSlices.validateConfig(config)
		# get slice relevant parts of config
		self.config = { cp : config[cp] for cp in self.configProperties()}

		self.slices  = []

		# some messy looping shit, hey i drunk now, back off
		if config["slice_direction"] == SliceDirection.NorthSouth:
			# travel west -> east, taking those delicious north/south slices
			# so start lat and end lat are constant over the everything
			current_long = config["west_edge"]
			long_step = self.calcStep(config["west_edge"], config["east_edge"], config["num_WE_steps"])

			# +1 because, think of the "steps" as the gaps between the numbers, instead of the numbers themselves
			for current_step in range(config["num_WE_steps"] + 1):
				# do some shit
				current_slice = Slice(	config["north_edge"], current_long,
												config["south_edge"], current_long,
												config["num_NS_steps"],
												config["slice_direction"]);
				current_slice.generatePoints() 

				self.slices.append(current_slice)
				current_long += long_step
		else:
			# slicing west/east
			# so traveling north -> south, taking w/e slices
			current_lat = config["north_edge"]
			lat_step = self.calcStep(config["north_edge"], config["south_edge"], config["num_NS_steps"])

			# +1 because, think of the "steps" as the gaps between the numbers, instead of the numbers themselves
			for current_step in range(config["num_NS_steps"] + 1):
				current_slice = Slice(	current_lat, config["west_edge"],
												current_lat, config["east_edge"],
												config["num_WE_steps"],
												config["slice_direction"])
				current_slice.generatePoints()
				
				self.slices.append(current_slice)
				current_lat += lat_step

	# ------------------------------------------
	# generates slices from given config
	def generateElevations(self, elevation_func, use_concurrency):
		if None == self.slices:
			raise Exception('Attempt to generate elevations without slices defined')

		for cur_slice in self.slices:
			cur_slice.generateElevations(elevation_func, use_concurrency)

	# ------------------------------------------
	def toDataObj(self):
		# slices to data obj array
		slices_data = [ cur_slice.toDataObj() for cur_slice in self.slices]

		return { "config": self.config, "slices": slices_data }

	# ------------------------------------------
	def fromDataObj(self, data_obj):
		# TODO: validate more of data_obj?

		if not "config" in data_obj:
			raise Exception("TopoSlices.fromDataObj(): Invalid data_obj, missing property 'config'")

		self.config = data_obj["config"]
		TopoSlices.validateConfig(self.config)

		# convert slice direction to Class enum
		slice_dir_enum = SliceDirection.toSliceDirection(self.config["slice_direction"])
		self.config["slice_direction"] = slice_dir_enum

		if not "slices" in data_obj:
			raise Exception("TopoSlices.fromDataObj(): Invalid data_obj, missing property 'slices'")

		# validate data_obj has expected number of slices?
		expected_slices_num = 1 + self.config["num_WE_steps"] if self.config["slice_direction"] == SliceDirection.NorthSouth else self.config["num_NS_steps"]
		if len(data_obj["slices"]) != expected_slices_num:
			raise Exception(f"TopoSlices.fromDataObj(): Invalid data_obj, expected {expected_slices_num} slices, data contains {len(data_obj['slices'])}")

		self.slices = []
		# turn slice data into Slices object instances
		for cur_slice_data in data_obj["slices"]:
			self.slices.append(Slice().fromDataObj(cur_slice_data))

# end TopoSlices class---------------------------------------------------
