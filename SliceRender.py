from InkscapeSVG import *
from support.LogChannels import log

from SVGConfig import SVGConfig
from Slice import SliceDirection, Slice

# TODO:
#	* weird little bug where last (rightmost segment) isn't smoothed?
#	* use vertical scale
#	* all slices need to be aware of global minimum, adjust to accordingly
#	* is there a max layer count in inkscape?
#	* svg gen uses config: slice length inches
#	* PROPERLY render chars?  Ugh, fonts
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
def renderCross(x, y, width, height, path):
	path.move(x - (width* 0.5), y)
	path.draw(x + (width*0.5), y)
	path.move(x, y - (height*0.5))
	path.draw(x, y + (height*0.5))
	return path

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

	print("renderNumString()")
	print(f"int_str: {int_str}")

	for cur_char in int_str:
		cur_render_func = num_render_funcs[ord(cur_char) - ord("0")]
		paths.append(cur_render_func(cur_x, start_y, width, height))
		cur_x += width + spacing

	return paths

# ------------------------------------------------------------------
def renderInt(int_number, start_x, start_y, width, height, spacing):
	return renderNumString(f"{int_number}")

#  -----------------------------------------------------------------
# todo: so many params, can we make this cleaner?
def elevationToY(elevation, start_y, basement_inches, minimum_elevation, slice_inches_to_svg_inches, vertical_exaggeration):
	calc_y = start_y - basement_inches
	current_elevation_in_svg_scale = ((elevation - minimum_elevation)* 12) * slice_inches_to_svg_inches * vertical_exaggeration
	calc_y -= current_elevation_in_svg_scale
	return calc_y
	
#  -----------------------------------------------------------------
def sliceToLayer(slice, layer_name, config:SVGConfig, minimum_elevation):
	slice_layer = InkscapeLayer(layer_name)

	slice_length_degrees = slice.sliceLengthDegrees()

	log.svg(f"minimum_elevation: {minimum_elevation}")
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
	slice_inches_to_svg_inches = config.slice_svg_length_inches / slice_inches # should be something < 1

	log.svg(f"slice_inches_to_svg_inches: {slice_inches_to_svg_inches}")

	log.todo("make start_y configurable")
	start_y = 12

	cur_x = 0
	x_step_inches = config.slice_svg_length_inches / (len(slice.elevations)-1)
	x_step_half = x_step_inches * 0.5

	# remember that y coordinates go UP from start, so I guess that works since we're dealing with elevations?
	slice_path = InkscapePath(cur_x, start_y)

	# very placeholder...
	# but yeah, need to scale DOWN the elevations to some local scale
	basement_inches = 1
	vertical_exaggeration = 1.0

	smoothed = True
	# cross_path = InkscapePath(0,0)
	cross_width = 0 # 0.25

	if cross_width > 0:
		c1_path = InkscapePath(0,0)
		c1_path.setColor("ff0000")
		c2_path = InkscapePath(0,0)
		c2_path.setColor("00ff00")
		points_path = InkscapePath(0,0)
		points_path.setColor("0000ff")

	# compute slopes (convert to svg inches)
	# note that there are one fewer slopes than there are elevations(points)
	# (cuz slopes are measured between points)
	slopes = []
	for cur_index in range(0,len(slice.elevations) - 1):
		slopes.append((slice.elevations[cur_index + 1] - slice.elevations[cur_index]) * 12 * slice_inches_to_svg_inches)

	log.svg(f"slopes:{slopes}")

	# move up "left" side to first elevation
	cur_elevation = slice.elevations[0]

	cur_y = elevationToY(cur_elevation,start_y,basement_inches,minimum_elevation
		      ,slice_inches_to_svg_inches, vertical_exaggeration)

	# draw line up to first (0 index) point...
	slice_path.draw(cur_x, cur_y)

	log.svg(f"index:{0} curxy:{cur_x},{cur_y} elev:{cur_elevation}")

	# control points
	c1x = 0
	c1y = 0
	c2x = 0
	c2y = 0

	# note: looping from 1 because index 0 is leftmost point, and already drawn (above)
	for cur_index in range(1, len(slice.elevations)):
		last_y = cur_y
		last_x = cur_x

		cur_x += x_step_inches
		cur_elevation = slice.elevations[cur_index]
		cur_y = elevationToY(cur_elevation,start_y,basement_inches,minimum_elevation
					,slice_inches_to_svg_inches, vertical_exaggeration)

		if not smoothed:
			log.svg(f"index:{cur_index} curxy:{cur_x},{cur_y} elev:{cur_elevation}")
			slice_path.draw(cur_x,cur_y)
		else:
			# compute two control points of current line
			c1x = last_x + x_step_half
			if cur_index == 1:
				# for first point, control point 1 is just straight out from zero point
				# c1y = last_y	# todo: this looks bad, do something different
				c1y = cur_y + slopes[0] * 0.5
			else:
				# 1st control point is along previous slope, projected into current segment
				prev_slope = slopes[cur_index-1]
				c1y = last_y - prev_slope * 0.5

			c2x = last_x + x_step_half	# both control points always sit at same x (for now)
			# control point 2 y coordinate is on a line from next slope, projected back into current segment
			if cur_index < (len(slice.elevations) - 1) :
				next_slope = slopes[cur_index]
				c2y = cur_y + next_slope * 0.5
			else:
				# if on last point, don't have a next slope (remember how there are one fewer slopes than
				# points?), so just use last slope I guess
				c2y = cur_y + slopes[cur_index - 1] * 0.5

			slice_path.Cdraw(c1x, c1y, c2x, c2y, cur_x, cur_y)

			log.svg(f"index:{cur_index} curxy:{cur_x},{cur_y} elev:{cur_elevation}")
			log.svg(f"c1:{c1x},{c1y} c2:{c2x},{c2y}")

			if cross_width > 0:
				renderCross(c1x, c1y, cross_width,cross_width, c1_path)
				renderCross(c2x, c2y, cross_width,cross_width, c2_path)
				renderCross(cur_x,cur_y, cross_width,cross_width, points_path)


	# at end, move back DOWN to min_y
	# restart Line draw mode
	slice_path.Ldraw(cur_x, start_y)
	slice_path.draw(0, start_y)
	slice_path.close()

	slice_layer.add_node(slice_path)

	if cross_width > 0:
		c1_path.close()
		slice_layer.add_node(c1_path)
		c2_path.close()
		slice_layer.add_node(c2_path)
		points_path.close()
		slice_layer.add_node(points_path)

	# add arrow pointing left
	arrow_path = renderLeftArrow(1, start_y - 0.5, 0.5, 0.25, 0.25)
	slice_layer.add_node(arrow_path)

	tstart_x = 1.25
	tstart_y = start_y - 0.5
	twidth = 0.25
	theight = 0.35
	spacing = 0.1

	# todo: add direction hint next to arrow

	paths = renderNumString(slice.name, tstart_x, tstart_y, twidth, theight, spacing)
	for cur_path in paths:
		slice_layer.add_node(cur_path)

	return slice_layer

#  -----------------------------------------------------------------
def slicesToSVG(slices:list[Slice], config:SVGConfig):
	svg = InkscapeSVG()

	cur_slice_number = 0
	slice_base_name = "slice_"

	# have to know the minimum elevation in the job
	min_elevation = min([cur_slice.minimum_elevation for cur_slice in slices])

	log.todo("svg configuration (layers/file), other stuff")
	for cur_slice in slices:
		cur_slice_layer = sliceToLayer(cur_slice, slice_base_name + str(cur_slice_number), config, min_elevation)
		svg.addNode(cur_slice_layer)
		cur_slice_number += 1

	svg.write(config.svg_base_filename)
