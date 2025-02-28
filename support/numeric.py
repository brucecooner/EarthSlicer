
# -----------------------------------------------------------
def floatToPrecision(flt: float, num_decimals: int)-> float:
	assert num_decimals > 0

	decimal_shifter = pow(10, num_decimals)

	as_int = int(flt * decimal_shifter)		# shift left, make to int
	to_precision = as_int / decimal_shifter	# shift right
	return to_precision
