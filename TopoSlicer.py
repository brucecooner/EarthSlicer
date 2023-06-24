import jsons

from support.LogChannels import log
from support.GTimer import gtimer

from SliceJobConfig import SliceJobConfig
from Slice import Slice, SliceDirection

log.addChannel("slicer", "slicer: ")
log.setChannel("slicer", False)

# TODO:
#	* track overall min/max?

# ------------------------------------------
def calcStep(start, end, number_of_points):
	difference = end - start

	step = difference / max(number_of_points - 1, 1)

	return step

# ------------------------------------------
# def topoSlicerValidateConfig(test_config:dict, throw_on_fail:bool = True):
# 	topoSlicerConfigProperties = {
# 		"slice_direction",
# 		"number_of_slices",
# 		"number_of_elevations",
# 		"north_edge",
# 		"west_edge",
# 		"south_edge",
# 		"east_edge" }
	
# 	valid_config = True
# 	result_message = ""
# 	missing_keys = []
# 	for cur_prop in topoSlicerConfigProperties:
# 		if not cur_prop in test_config:
# 			valid = False
# 			missing_keys.append(cur_prop)

# 	if len(missing_keys):
# 		result_message = f'Invalid TopoSlices config, missing keys: ' + str(missing_keys)
# 		if throw_on_fail:
# 			raise Exception(result_message)

# 	return {"result":valid_config, "message":result_message}

# ------------------------------------------
# takes in a SliceJobConfig, returns array of slices that result from it
def generateTopoSlices(config:SliceJobConfig):
	log.slicer("generating slices...")

	slices = []
	slice_num = 0

	# some messy looping shit, hey i drunk now, back off
	if config.slice_direction == SliceDirection.NorthSouth:
		# travel west -> east, taking those delicious north/south slices
		# so start lat and end lat are constant over the everything
		log.slicer("north south")
		current_long = config.west_edge
		if config["number_of_slices"] > 1:
			long_step = calcStep(config.west_edge, config.east_edge, config.number_of_slices)
		else:
			long_step = 0

		for current_step in range(config.number_of_slices):
			# do some shit
			current_slice = Slice(	config.north_edge, current_long,
											config.south_edge, current_long,
											config.number_of_elevations,
											config.slice_direction,
											slice_num)

			slices.append(current_slice)
			slice_num += 1
			current_long += long_step
	else:
		log.slicer("west east")
		# slicing west/east
		# so traveling north -> south, taking w/e slices
		current_lat = config.north_edge
		lat_step = calcStep(config.north_edge, config.south_edge, config.number_of_slices)

		for current_step in range(config.number_of_slices):
			gtimer.startTimer('generate single slice')
			current_slice = Slice(	current_lat, config.west_edge,
											current_lat, config.east_edge,
											config.number_of_elevations,
											config.slice_direction,
											slice_num)

			gtimer.markTimer('generate single slice')

			slices.append(current_slice)
			slice_num += 1
			current_lat += lat_step

	log.slicer(f"generated {len(slices)} slices")

	return slices

