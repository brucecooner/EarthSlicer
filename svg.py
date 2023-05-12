import svgwrite

from Slice import SliceDirection, Slice

#	TODO:
#	* render an svg?
#	* added elevation below minimum
#	* units / inches - can use "XXin" when specifying to svgwrite, can inkscape extension set inks to show rulers in in? (low prio)
#	* investigate inkscape for layers (https://svgwrite.readthedocs.io/en/latest/extensions/inkscape.html)

#  -----------------------------------------------------------------
def sliceToSVG(slice, config):
	# just make an svg
	dwg = svgwrite.Drawing(filename=config["output_svg_basename"] + '.svg', size = ('20in', '12in'))

	# do we SET a unit type?

	# square = dwg.add(dwg.rect((0, 0), ('10in', '10in'), fill='blue'))

	# slice_layer = dwg.add(dwg.g(id='slice_1', fill='red'))

	slice_points = [	('0in', '0in'), 
		 					('10in', '0in'),
							('10in', '10in'),
							('5in', '15in'),
							('0in', '10in'),
						]
	slice_poly = dwg.polygon(slice_points, stroke=svgwrite.rgb(0, 0, 255, "RGB"))

	dwg.add(slice_poly)

	# slice_poly = dwg.add(svgwrite.shapes.poly)

	dwg.save()
