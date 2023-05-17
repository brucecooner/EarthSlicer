from InkscapeSVG import *
from Slice import SliceDirection, Slice

# TODO:
#	* sort out vertical coordinate chaos
#	* vertical scale

#  -----------------------------------------------------------------
def sliceToLayer(slice, layer_name, config):
	slice_layer = InkscapeLayer(layer_name)
	
	# TODO sort out scaling
	inches_per_slice = 5

	start_y = 12

	cur_x = 0
	x_step_inches = 1

	# remember that y coordinates go UP from start, so I guess that works since we're dealing with elevations?
	slice_path = InkscapePath(cur_x, start_y)

	# very placeholder...
	# but yeah, need to scale DOWN the elevations to some local scale
	elevation_feet_to_inches = .0033
	basement_inches = 1

	# oh yeah, y coordinates are reversed cuz screen space
	for cur_elevation in slice.elevations:
		cur_y = start_y - basement_inches
		# subtract some thing fromthe current elevation
		current_calc_elev = cur_elevation - 4000
		current_calc_elev *= elevation_feet_to_inches
		cur_y -= current_calc_elev
		cur_x += x_step_inches
		slice_path.move(cur_x, cur_y)

	# at end, move back DOWN to min_y
	slice_path.move(cur_x, start_y)
	
	slice_layer.add_node(slice_path)

	return slice_layer

#  -----------------------------------------------------------------
def slicesToSVG(slices, config):
	svg = InkscapeSVG()

	cur_slice_number = 1
	slice_base_name = "slice_"

	for cur_slice in slices:
		cur_slice_layer = sliceToLayer(cur_slice, slice_base_name + str(cur_slice_number), config)
		svg.addNode(cur_slice_layer)
		cur_slice_number += 1

	svg.write(config["svg_filename"])
