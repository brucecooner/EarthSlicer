import math

def radiansPerDegree():
	return (2 * math.pi) / 360.0

def feetPerMile():
	return 5280

def circumferenceOfEarthAtEquator():
	return 24901.461	# at equator

def milesPerDegreeAtEquator():
	return circumferenceOfEarthAtEquator() / 360.0	# 69.170725

def feetPerDegreeAtEquator():
	return milesPerDegreeAtEquator() * feetPerMile()	#	25,262,630.96

def longitudeDegreesToMiles(degrees:float, longitude:float):
	assert(-90.0 <= degrees and degrees <= 90.0)
	# attenuate for decreasing distance between lines of latitude
	adjust = math.cos(longitude * radiansPerDegree()) # technically north latitude is not as wide, but we'll ignore that
	return degrees * (milesPerDegreeAtEquator() * adjust)

def latitudeDegreesToMiles(degrees:float):
	assert(-180.0 <= degrees and degrees <= 180.0)
	return degrees * milesPerDegreeAtEquator()
