from InkscapeSVG import *
from support.LogChannels import log

from Slice import SliceDirection, Slice

# TODO:
#	* vertical scale
#	* all slices need to be aware of global minimum, adjust to accordingly
#	* is there a max layer count in inkscape?
#	* svg gen uses config: slice length inches
#	* PROPERLY render chars
#	* logic to render N/W lettering
#	* id numbers, whenever that is sorted
#	* number rendering to its own module or something

# DONE:
#	* sort out vertical coordinate chaos

log.addChannel("svg", "svg")
log.setChannel("svg", False)


#  -----------------------------------------------------------------
# puts start x,y at lower left corner
def renderSegPoints(start_x, start_y, width, height):
	seg_points = []
	seg_points.insert( 0, (start_x, start_y) )	# lower left
	seg_points.insert( 1, (start_x + width, start_y) )	# lower right
	seg_points.insert( 2, (start_x, start_y - height + (height*0.5)) )	# mid left
	seg_points.insert( 3, (start_x + width, start_y - height + (height*0.5)) )	# mid right
	seg_points.insert( 4, (start_x, start_y - height) )	# top left
	seg_points.insert( 5, (start_x + width, start_y - height ) )	# top right
	return seg_points

#  -----------------------------------------------------------------
def drawToIndex(path, sp, index):
	path.draw(sp[index][0], sp[index][1])

#  -----------------------------------------------------------------
def moveToIndex(path, sp, index):
	path.move(sp[index][0], sp[index][1])

#  -----------------------------------------------------------------
# start_x,start_y specifies end of arrow shaft, tip is "screen left" (decreasing x) of end
def renderLeftArrow(start_x, start_y, total_length, tip_fraction, tip_height_fraction):
	tip_width = total_length * tip_fraction
	tip_x = start_x - total_length
	tip_back_x = start_x - total_length + tip_width
	tip_top_y = start_y - ((total_length * tip_height_fraction)/2)
	tip_bottom_y = start_y + ((total_length * tip_height_fraction)/2)

	arrow_path = InkscapePath(start_x, start_y)
	arrow_path.draw(tip_back_x, start_y)
	arrow_path.draw(tip_back_x, tip_top_y)
	arrow_path.draw(tip_x, start_y)
	arrow_path.draw(tip_back_x, tip_bottom_y)
	arrow_path.draw(tip_back_x, start_y)

	return arrow_path

#  -----------------------------------------------------------------
# start_x,start_y = coordinate of lower left corner
def renderN(start_x, start_y, width, height):
	sp = renderSegPoints(start_x,start_y,width,height)
	char_path = InkscapePath(sp[0][0], sp[0][1])
	drawToIndex(char_path, sp, 4)
	drawToIndex(char_path, sp, 1)
	drawToIndex(char_path, sp, 5)
	return char_path

#  -----------------------------------------------------------------
# start_x,start_y = coordinate of lower left corner
def renderW(start_x, start_y, width, height):
	quarter_width = width * 0.25
	char_path = InkscapePath(start_x, start_y - height)
	char_path.draw(start_x + (quarter_width * 1), start_y)
	char_path.draw(start_x + (quarter_width * 2), start_y - (height/2))
	char_path.draw(start_x + (quarter_width * 3), start_y)
	char_path.draw(start_x + (quarter_width * 4), start_y - height)
	return char_path

def render0(start_x, start_y, width, height):
	sp = renderSegPoints(start_x,start_y,width,height)
	path = InkscapePath(sp[0][0], sp[0][1])
	drawToIndex(path, sp, 4)
	drawToIndex(path, sp, 5)
	drawToIndex(path, sp, 1)
	path.close()
	return path

def render1(start_x, start_y, width, height):
	sp = renderSegPoints(start_x,start_y,width,height)
	path = InkscapePath(sp[1][0], sp[1][1])
	drawToIndex(path, sp, 5)
	return path

def render2(start_x, start_y, width, height):
	sp = renderSegPoints(start_x,start_y,width,height)
	path = InkscapePath(sp[1][0], sp[1][1])
	drawToIndex(path, sp, 0)
	drawToIndex(path, sp, 2)
	drawToIndex(path, sp, 3)
	drawToIndex(path, sp, 5)
	drawToIndex(path, sp, 4)
	return path

def render3(start_x, start_y, width, height):
	sp = renderSegPoints(start_x,start_y,width,height)
	path = InkscapePath(sp[0][0], sp[0][1])
	drawToIndex(path, sp, 1)
	drawToIndex(path, sp, 5)
	drawToIndex(path, sp, 4)
	moveToIndex(path, sp, 3)
	drawToIndex(path, sp, 2)
	return path

def render4(start_x, start_y, width, height):
	sp = renderSegPoints(start_x,start_y,width,height)
	path = InkscapePath(sp[1][0], sp[1][1])
	drawToIndex(path, sp, 5)
	moveToIndex(path, sp, 4)
	drawToIndex(path, sp, 2)
	drawToIndex(path, sp, 3)
	return path

def render5(start_x, start_y, width, height):
	sp = renderSegPoints(start_x,start_y,width,height)
	path = InkscapePath(sp[0][0], sp[0][1])
	drawToIndex(path, sp, 1)
	drawToIndex(path, sp, 3)
	drawToIndex(path, sp, 2)
	drawToIndex(path, sp, 4)
	drawToIndex(path, sp, 5)
	return path

def render6(start_x, start_y, width, height):
	sp = renderSegPoints(start_x,start_y,width,height)
	path = InkscapePath(sp[5][0], sp[5][1])
	drawToIndex(path, sp, 4)
	drawToIndex(path, sp, 0)
	drawToIndex(path, sp, 1)
	drawToIndex(path, sp, 3)
	drawToIndex(path, sp, 2)
	return path

def render7(start_x, start_y, width, height):
	sp = renderSegPoints(start_x,start_y,width,height)
	path = InkscapePath(sp[4][0], sp[4][1])
	drawToIndex(path, sp, 5)
	drawToIndex(path, sp, 1)
	return path

def render8(start_x, start_y, width, height):
	sp = renderSegPoints(start_x,start_y,width,height)
	path = InkscapePath(sp[0][0], sp[0][1])
	drawToIndex(path, sp, 4)
	drawToIndex(path, sp, 5)
	drawToIndex(path, sp, 1)
	drawToIndex(path, sp, 0)
	moveToIndex(path, sp, 2)
	drawToIndex(path, sp, 3)
	return path

def render9(start_x, start_y, width, height):
	sp = renderSegPoints(start_x,start_y,width,height)
	path = InkscapePath(sp[0][0], sp[0][1])
	drawToIndex(path, sp, 1)
	drawToIndex(path, sp, 5)
	drawToIndex(path, sp, 4)
	drawToIndex(path, sp, 2)
	drawToIndex(path, sp, 3)
	return path

# ------------------------------------------------------------------
def renderNumString(int_str, start_x, start_y, width, height, spacing):
	paths = []

	num_render_funcs = [
		render0, render1, render2, render3, render4, render5, render6, render7, render8, render9
	]

	cur_x = start_x

	for cur_char in int_str:
		cur_render_func = num_render_funcs[ord(cur_char) - ord("0")]
		paths.append(cur_render_func(cur_x, start_y, width, height))
		cur_x += width + spacing

	return paths

# ------------------------------------------------------------------
def renderInt(int_number, start_x, start_y, width, height, spacing):
	return renderNumString(f"{int_number}")


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
		slice_path.draw(cur_x, cur_y)

		cur_x += x_step_inches

	# at end, move back DOWN to min_y
	cur_x -= x_step_inches	# remove last x step
	slice_path.draw(cur_x, start_y)

	slice_layer.add_node(slice_path)

	# add arrow pointing left
	arrow_path = renderLeftArrow(1, start_y - 0.5, 0.5, 0.25, 0.25)
	slice_layer.add_node(arrow_path)

	tstart_x = 1.25
	tstart_y = start_y - 0.5
	twidth = 0.25
	theight = 0.35
	spacing = 0.1

	# add direction hint next to arrow

	# testing
	# test_func = render1
	# t_pathns = test_func(tstart_x, tstart_y, twidth, theight)
	# slice_layer.add_node(t_pathns)

	cur_start_x = tstart_x

	print(slice.name)

	# paths = renderInt(render_num, tstart_x, tstart_y, twidth, theight, spacing)
	paths = renderNumString(slice.name, tstart_x, tstart_y, twidth, theight, spacing)
	for cur_path in paths:
		slice_layer.add_node(cur_path)

	# for cur_num in range(10):
	# 	cur_render_func = num_render_funcs[cur_num]
	# 	cur_num_path = cur_render_func(cur_start_x, tstart_y, twidth, theight)
	# 	slice_layer.add_node(cur_num_path)
	# 	cur_start_x += twidth + spacing

	return slice_layer

#  -----------------------------------------------------------------
def slicesToSVG(slices:list[Slice], config:dict):
	svg = InkscapeSVG()

	cur_slice_number = 0
	slice_base_name = "slice_"

	log.todo("svg configuration (layers/file), other stuff")
	for cur_slice in slices:
		cur_slice_layer = sliceToLayer(cur_slice, slice_base_name + str(cur_slice_number), config)
		svg.addNode(cur_slice_layer)
		cur_slice_number += 1

	svg.write(config["svg_filename"])
