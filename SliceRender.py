from InkscapeSVG import *
from LogChannels import log

from Slice import SliceDirection, Slice

# TODO:
#	* vertical scale
#	* all slices need to be aware of global minimum, adjust to accordingly
#	* is there a max layer count in inkscape?
#	* svg gen uses config: slice length inches

# DONE:
#	* sort out vertical coordinate chaos

log.addChannel("svg", "svg")
# log.setChannel("svg", False)

#  -----------------------------------------------------------------
def sliceToLayer(slice, layer_name, config):
	slice_layer = InkscapeLayer(layer_name)

	slice_length_degrees = slice.sliceLengthDegrees()

	log.svg(f"slice_length_degrees: {slice_length_degrees}")

	# elevations from USGS are in feet, so convert to feet somehow
	# one fourth of distance around the earth (approximate) divided by degrees in one fourth of a circle
	# kilometers_per_degree = 10,000 / 90
	# feet_per_kilometer = 3280.4
	# yields...
	feet_per_degree = 364488.0
	feet_per_mile = 5280
	# longitude gets squished as you approach the poles, but we'll consider the sliced squares to be truly square

	slice_feet = feet_per_degree * slice_length_degrees
	slice_inches = slice_feet * 12.0 # probably a big number

	log.svg(f"slice length inches: {slice_inches}")
	log.svg(f"slice length feet: {slice_feet}")
	log.svg(f"slice length miles: {slice_feet / feet_per_mile}")

	# okay, now go from the slice's size on earth to the render width
	slice_inches_to_svg_inches = config["slice_svg_length_inches"] / slice_inches # should be something < 1

	log.svg(f"slice_scale: {slice_inches_to_svg_inches}")

	start_y = 12

	cur_x = 0
	x_step_inches = config["slice_svg_length_inches"] / len(slice.elevations)

	# remember that y coordinates go UP from start, so I guess that works since we're dealing with elevations?
	slice_path = InkscapePath(cur_x, start_y)

	# very placeholder...
	# but yeah, need to scale DOWN the elevations to some local scale
	basement_inches = 1
	vertical_exaggeration = 1.0

	# oh yeah, y coordinates are reversed cuz screen space
	for cur_elevation in slice.elevations:
		log.svg(f"cur_elev: {cur_elevation}")
		cur_y = start_y - basement_inches
		current_elevation_in_svg_scale = (cur_elevation* 12) * slice_inches_to_svg_inches * vertical_exaggeration
		cur_y -= current_elevation_in_svg_scale
		slice_path.move(cur_x, cur_y)

		cur_x += x_step_inches

	# at end, move back DOWN to min_y
	cur_x -= x_step_inches	# remove last x step
	slice_path.move(cur_x, start_y)
	# TODO: NEED TO CLOSE THIS PATH WITH A Z CHARACTER!!! if it doesn't already do that?
	
	slice_layer.add_node(slice_path)

	return slice_layer

#  -----------------------------------------------------------------
def slicesToSVG(slices:list[Slice], config:dict):
	svg = InkscapeSVG()

	cur_slice_number = 1
	slice_base_name = "slice_"

	log.todo("svg configuration (layers/file), other stuff")
	for cur_slice in slices:
		cur_slice_layer = sliceToLayer(cur_slice, slice_base_name + str(cur_slice_number), config)
		svg.addNode(cur_slice_layer)
		cur_slice_number += 1

	svg.write(config["svg_filename"])
