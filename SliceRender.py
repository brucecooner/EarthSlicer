import os
from math import ceil

from InkscapeSVG import *
from support.LogChannels import log
from unitsSupport import *

from SVGConfig import SVGConfig
from Slice import SliceDirection, Slice

# TODO:
#	* weird little bug where last (rightmost segment) isn't smoothed?
#	* is there a max layer count in inkscape?
#	* number rendering to its own module or something

# DONE:
#	* svg gen uses config: slice length inches
#	* id numbers, whenever that is sorted
#	* all slices need to be aware of global minimum, adjust to accordingly
#	* sort out vertical coordinate chaos (sorta done I guess)

log.addChannel("svg", "svg")
log.setChannel("svg", False)
log.addChannel("svggrid", "svgg")
log.setChannel("svggrid", False)

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
# start_x,start_y specifies tip of arrow
def renderLeftArrow(start_x, start_y, total_length, tip_fraction, tip_height_fraction):
	tip_width = total_length * tip_fraction
	tip_back_x = start_x + tip_width
	tip_top_y = start_y - ((total_length * tip_height_fraction)/2)
	tip_bottom_y = start_y + ((total_length * tip_height_fraction)/2)

	arrow_path = InkscapePath(start_x, start_y)
	arrow_path.draw(tip_back_x, tip_top_y)
	arrow_path.draw(tip_back_x, tip_top_y)
	arrow_path.draw(tip_back_x, tip_bottom_y)
	arrow_path.draw(start_x, start_y)

	arrow_path.move(tip_back_x, start_y)
	arrow_path.draw(start_x + total_length, start_y)

	return arrow_path

#  -----------------------------------------------------------------
# start_x,start_y = coordinate of lower left corner
def renderN(start_x, start_y, width, height, color = "000000"):
	sp = renderSegPoints(start_x,start_y,width,height)
	char_path = InkscapePath(sp[0][0], sp[0][1])
	char_path.setColor(color)
	drawToIndex(char_path, sp, 4)
	drawToIndex(char_path, sp, 1)
	drawToIndex(char_path, sp, 5)
	return char_path

#  -----------------------------------------------------------------
# start_x,start_y = coordinate of lower left corner
def renderW(start_x, start_y, width, height, color = "000000"):
	quarter_width = width * 0.25
	char_path = InkscapePath(start_x, start_y - height)
	char_path.setColor(color)
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
def renderNumString(int_str, start_x, start_y, width, height, spacing, color="000000"):
	paths = []

	num_render_funcs = [
		render0, render1, render2, render3, render4, render5, render6, render7, render8, render9
	]

	cur_x = start_x

	for cur_char in int_str:
		cur_render_func = num_render_funcs[ord(cur_char) - ord("0")]
		path = cur_render_func(cur_x, start_y, width, height)
		path.setColor(color)
		paths.append(path)
		cur_x += width + spacing

	return paths

# ------------------------------------------------------------------
def renderInt(int_number, start_x, start_y, width, height, spacing):
	return renderNumString(f"{int_number}")

#  -----------------------------------------------------------------
# todo: so many params, can we make this cleaner?
def elevationToY(elevation, start_y, base_inches, minimum_elevation, slice_inches_to_svg_inches, vertical_scale):
	calc_y = start_y - base_inches
	current_elevation_in_svg_scale = ((elevation - minimum_elevation) * vertical_scale * 12) * slice_inches_to_svg_inches
	calc_y -= current_elevation_in_svg_scale
	return calc_y
	
#  -----------------------------------------------------------------
# renders slice elevations to an inkscape layer
# return (layer, minimum_y_coordinate_of_layer)
def sliceToLayer(slice, config:SVGConfig, minimum_elevation, start_x, start_y):
	text_color_string = "00aa00"
	arrow_color_string = "00aa00"

	# ------------
	# scale
	slice_feet = slice.sliceLengthFeet()
	slice_inches = slice_feet * 12.0 # probably a big number

	# okay, now go from the slice's size on earth to svg space
	slice_inches_to_svg_inches = config.slice_width_inches / slice_inches # should be something < 1

	# log.svg(f"slice_inches_to_svg_inches: {slice_inches_to_svg_inches}")

	min_y = None
	cur_x = start_x

	x_step_inches = config.slice_width_inches / (len(slice.elevations)-1)
	x_step_half = x_step_inches * 0.5

	# control points
	c1x = 0
	c1y = 0
	c2x = 0
	c2y = 0

	# ------------
	# notch config
	notch_count = None
	notch_centers = None
	notch_width = 0.0
	notch_depth = 0.0
	if config.bottom_notch_config:
		notch_count = config.bottom_notch_config["count"]
		notch_dist_from_ends = dict.get(config.bottom_notch_config, "distance_from_ends", 0)

		# since bottom of slice is drawn coming from higher x to lower x coords, notch centers must be
		# put into array the same way, hence these calcs start at higher x coords
		# also note that notch_centers are calculated starting at x = 0, so using them will 
		# require translation to start_x
		notch_width = config.bottom_notch_config["width"]
		notch_depth = config.bottom_notch_config["depth"]
		notch_half_width = notch_width / 2.0
		notch_centers = []

		if notch_count == 1:
			# if only one notch, always goes in center
			notch_centers.append(config.slice_width_inches / 2)
		else:
			if notch_dist_from_ends == 0:
				# if dist from edge == 0, spread evenly across entire slice
				notch_step = config.slice_width_inches / (notch_count + 1)
				cur_notch_center = config.slice_width_inches - notch_step
				for cur_notch in range(notch_count):
					notch_centers.append(cur_notch_center)
					cur_notch_center -= notch_step
			else:
				# if dist from edge > 0, distribute between slice minus the ends, with a notch at either end of this
				# distance
				# note: subtract dist from ends * 2, to get usable width, and use notch_count-1 to put a notch at the ends
				notch_step = (config.slice_width_inches - (notch_dist_from_ends * 2.0)) / (notch_count-1)
				cur_notch_center = config.slice_width_inches - notch_dist_from_ends
				for cur_notch in range(notch_count):
					notch_centers.append(cur_notch_center)
					cur_notch_center -= notch_step

	# ------------
	# cross config
	# set to >0 to turn on crosses on topo and control points
	cross_width = 0.0 # grrr, broken 0.25
	if cross_width > 0:
		c1_path = InkscapePath(0,0)
		c1_path.setColor("ff0000")
		c2_path = InkscapePath(0,0)
		c2_path.setColor("00ff00")
		points_path = InkscapePath(0,0)
		points_path.setColor("0000ff")

	# -------------------------------------------
	# compute slopes (also convert to svg inches)
	# note that there are one fewer slopes than there are elevations(points)
	# (cuz slopes are measured between points)
	slopes = []
	for cur_index in range(0,len(slice.elevations) - 1):
		slopes.append((slice.elevations[cur_index + 1] - slice.elevations[cur_index]) * 12 * slice_inches_to_svg_inches)

	# -------------
	# begin drawing
	# remember that y coordinates go UP from start, so I guess that works since we're dealing with elevations?
	slice_path = InkscapePath(cur_x, start_y)

	# --------------
	# "left" side
	cur_elevation = slice.elevations[0]

	cur_y = elevationToY(cur_elevation, start_y, config.base_inches, minimum_elevation
		      ,slice_inches_to_svg_inches, config.vertical_scale)

	# draw line up to first (0 index) point...
	slice_path.draw(cur_x, cur_y)

	# ----------------------------------------------
	# draw elevation points (terrain along "top" of path)
	# note: looping from 1 because index 0 is leftmost point, and already drawn (above)
	for cur_index in range(1, len(slice.elevations)):
		last_y = cur_y
		last_x = cur_x

		cur_x += x_step_inches
		cur_elevation = slice.elevations[cur_index]
		cur_y = elevationToY(cur_elevation,start_y, config.base_inches, minimum_elevation
					,slice_inches_to_svg_inches, config.vertical_scale)

		# track minimum y coordinate
		min_y = cur_y if not min_y else min(min_y, cur_y)

		if not config.smoothed:
			# log.svg(f"index:{cur_index} curxy:{cur_x},{cur_y} elev:{cur_elevation}")
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

			if cross_width > 0:
				renderCross(c1x, c1y, cross_width,cross_width, c1_path)
				renderCross(c2x, c2y, cross_width,cross_width, c2_path)
				renderCross(cur_x,cur_y, cross_width,cross_width, points_path)

	# ---------------
	# draw right side
	# at end, move back DOWN to min_y
	# (and set path back to Line draw mode)
	slice_path.Ldraw(cur_x, start_y)

	# now at bottom "right" (max x) corner 

	# -----------
	# draw bottom

	# draws not going to "left" (decreasing x)
	def notchAt(nx, ny, ndepth, nwidth, path):
		# up
		path.draw(nx, ny - ndepth)
		# left
		path.draw(nx - nwidth, ny - ndepth)
		# down
		path.draw(nx - nwidth, ny)

	if notch_count:
		for cur_notch_center in notch_centers:
			cur_x = start_x + cur_notch_center + notch_half_width
			slice_path.draw(cur_x, start_y)
			notchAt(cur_x, start_y, notch_depth, notch_width, slice_path)

	# finalize bottom line, to bottom "left" corner
	slice_path.draw(start_x, start_y)
	# note that slice_path doesn't get closed, so the laser cutter will start
	# its cut there instead of a random point along the slope (probably)

	if cross_width > 0:
		c1_path.close()
		c2_path.close()
		points_path.close()

	# add arrows / direction indicator
	# eh, arrow/direction not really adding much
	arrow_path = None
	dir_path = None
	# add arrow pointing left
	# arrow_height = (config.base_inches) * 0.25
	# arrow_length = arrow_height * 4
	# arrow_x = start_x + 0.5 # this assumes we've got 0.5 inches to work with
	# arrow_y = start_y - config.base_inches * 0.5
	# arrow_path = renderLeftArrow(arrow_x, arrow_y, arrow_length, 0.25, 0.25)
	# arrow_path.setColor(arrow_color_string)

	# text_height = config.base_inches * 0.5
	# text_width = text_height * 0.5
	# text_spacing = text_width * 0.5
	# text_start_x = arrow_x + arrow_length + text_spacing
	# text_start_y = start_y - (config.base_inches * 0.25)

	# renderLetterFunc = renderN
	# if slice.slice_direction == SliceDirection.WestEast:
	# 	renderLetterFunc = renderW

	# dir_path = renderLetterFunc(text_start_x, text_start_y, text_width, text_height, text_color_string)

	# text_start_x += (text_width + text_spacing) * 2

	# add slice number
	text_start_x = start_x + 0.5
	text_height = min(config.base_inches * 0.5, 0.1)
	text_width = text_height * 0.5
	# TODO: figure out better text placement/config
	# text_start_y = start_y - notch_depth - 0.1 if notch_depth else start_y - 0.1 # (config.base_inches * 0.25)
	text_start_y = start_y - 0.1 # (config.base_inches * 0.25)
	text_spacing = text_width * 0.5

	# note: text is green
	slice_index_text = ""
	# leading zeroes?
	if slice.slice_index < 10:
		slice_index_text += "00"
	elif slice.slice_index < 100:
		slice_index_text += "0"
	slice_index_text += f"{slice.slice_index}"
	num_paths = renderNumString(slice_index_text, text_start_x, text_start_y, text_width, text_height, text_spacing, text_color_string)

	# all paths in same (non layer) group
	slice_layer_path_group = InkscapeGroup(f"p_slice_{slice.slice_index}")
	slice_layer_path_group.addNode(slice_path)
	if arrow_path:
		slice_layer_path_group.addNode(arrow_path)
	if dir_path:
		slice_layer_path_group.addNode(dir_path)
	for cur_path in num_paths:
		slice_layer_path_group.addNode(cur_path)

	# then the path group goes into a layer group
	slice_layer_group = InkscapeGroup(f"g_slice_{slice.slice_index}", True)
	slice_layer_group.addNode(slice_layer_path_group)

	return (slice_layer_group, min_y)

log.addChannel("slicesToSVG", "slicesToSVG()")
log.setChannel("slicesToSVG", False)
log.addChannel("slicesToGridRow", "slicesToGridRow()")
log.setChannel("slicesToGridRow", False)

# ---------------------------------------------------------------------------
# renders slices in a row, starting at 0,0, puts them into an InkscapeGroup
# return (minimum_y_coordinate_reached_by_row, [InkscapeGroup])
def slicesToGridRow(slices, min_global_elevation, config:SVGConfig):
	# now make a group containing all slices in this row...
	row_slice_paths = []

	cur_x = 0
	# have to track/return minimum y in row so we know how far to move this row down
	min_y_in_row = None
	for cur_slice in slices:
		cur_slice_result = sliceToLayer(cur_slice, config, min_global_elevation, cur_x, 0)
		min_y_in_row = cur_slice_result[1] if not min_y_in_row else min(min_y_in_row, cur_slice_result[1])
		row_slice_paths.append(cur_slice_result[0])
		cur_x += config.slice_width_inches + config.layers_grid_x_spacing

	result = (min_y_in_row, row_slice_paths)

	log.slicesToGridRow(f"result:{result}")

	return result

# -----------------------------------------------------------------------------------------
def slicesToSVG(slices:list[Slice], config:SVGConfig):
	# have to know the minimum world elevation in the job as every slice has to be adjusted in screen space for it
	min_global_elevation = min([cur_slice.minimum_elevation for cur_slice in slices])

	# set up to do "overlay" mode, where all slices appear at 0,0
	# grid_width = None
	num_slices_per_row = 1
	row_results = []

	# calculate grid dims only if grid_config specified
	if config.grid_config:
		grid_width = config.grid_config["layers_grid_max_x"] - config.grid_config["layers_grid_min_x"]
		num_slices_per_row = ceil(grid_width / (config.slice_width_inches + config.layers_grid_x_spacing))

	log.slicesToSVG(f"slicesToSVG() num slices: {len(slices)}")
	log.slicesToSVG(f"min_global_elevation:{min_global_elevation}")
	log.slicesToSVG(f"num_slices_per_row:{num_slices_per_row}")

	cur_slice_index = 0

	# first just render ALL the rows...
	log.slicesToSVG("rendering all rows...")

	while cur_slice_index < len(slices):
		# log.slicesToSVG(f"cur_slice_index:{cur_slice_index}")
		# log.slicesToSVG(f"slicing to index: {cur_slice_index + num_slices_per_row}")
		# get slices for current row
		cur_row_slices = slices[cur_slice_index: cur_slice_index + num_slices_per_row]
		# log.slicesToSVG(f"cur_row_slices len: {len(cur_row_slices)}")
		cur_slice_index += num_slices_per_row
		log.slicesToSVG(f"cur_slice_index: {cur_slice_index}")
		row_results.append(slicesToGridRow(cur_row_slices, min_global_elevation, config))

	log.slicesToSVG(f"row_results len: {len(row_results)}")

	# start putting rows into grids up to max_y size, write that grid to an svg, repeat
	# unfortunately we don't know how many rows will fit into any given grid(file), since
	# their heights can vary
	# so add rows to the current grid until it exceeds max_y, this will go probably go over max_y but, eh, good enough

	# set up for building grids
	cur_svg = InkscapeSVG()
	cur_file_suffix = 0 # appended to file names
	cur_row_index = 0
	total_y_transform = 0
	svg_files_written = 0

	slices_in_current_svg = 0
	cur_file_start_slice_index = 0
	cur_file_end_slice_index = 0

	total_y_transform = 0.0

	# move rows into grids until they're all gone
	while cur_row_index < len(row_results):
		log.slicesToSVG(f"cur_row_index:{cur_row_index}")
		cur_row_result = row_results[cur_row_index]

		# if rendering grid, add this row's y transform
		# rows were all rendered at y=0, so we want to transform this row down onscreen, increasing y, by its maximum Y coordinate (stored in result[1])
		# BUT...the slice was rendered upward in screen space, which means it went towards negative
		# coordinates, but we want to move it DOWN in screen space, or in a positive y direction, so reverse the min y
		if config.grid_config:
			total_y_transform += (-cur_row_result[0] + (0 if cur_row_index == 0 else config.layers_grid_y_spacing))

		for cur_row_slice in cur_row_result[1]:
			log.slicesToSVG(f"adding row slice to svg...")
			log.slicesToSVG(f"total_y_transform:{total_y_transform}")
			cur_row_slice.setTransform(0, total_y_transform)
			# add current slice to svg
			cur_svg.addNode(cur_row_slice)

		# update numbers for added row
		slices_in_current_svg += len(cur_row_result[1])

		log.slicesToSVG(f"slices_in_current_svg: {slices_in_current_svg}")

		# time to write file?
		write_current_svg = False

		if config.grid_config:
			write_current_svg = (total_y_transform >= config.grid_config["layers_grid_max_y"]) or cur_row_index >= (len(row_results) - 1)
		else:
			# in non-grid mode, run to end then write
			write_current_svg = cur_row_index >= (len(row_results) - 1)

		# are we beyond max_y now? or at last row?
		if write_current_svg: # (total_y_transform >= config.layers_grid_max_y) or cur_row_index >= (len(row_results)-1):
			# write current svg
			cur_file_end_slice_index = cur_file_start_slice_index + slices_in_current_svg - 1

			# cur_filename = f"{config.svg_base_filename}-{cur_file_suffix}-"
			cur_filename = config.svg_base_filename
			if hasattr(config, "filename_info_string"):
				cur_filename += "-" + config.filename_info_string
			cur_filename += f"-{cur_file_start_slice_index}-{cur_file_end_slice_index}"
			cur_filename += ".svg"
			cur_path_and_filename = os.path.join(config.base_path, cur_filename)

			log.echo(f"writing svg file: {cur_path_and_filename}")
			log.echo(f"   {slices_in_current_svg} slices  {cur_file_start_slice_index}-{cur_file_end_slice_index}")

			cur_svg.write(cur_path_and_filename)
			svg_files_written += 1
			cur_svg = InkscapeSVG()
			cur_file_suffix += 1
			# reset for next file
			total_y_transform = 0
			cur_file_start_slice_index += slices_in_current_svg
			slices_in_current_svg = 0

		cur_row_index += 1

	log.echo()
	log.echo(f"generated {svg_files_written} svg files")
