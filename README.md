# EarthSlicer
vertical topography slicer (Python)

EarthSlicer produces a series of vertical "slices" of a specified square of the Earth's surface.
These slices can be specified to run north-south or east-west.

Output is in a series of .svg files.  
Since I use Inkscape, that flavorted the file format I create, and thus I can only guarantee the files will work with Inkscape (download at inkscape.org).

Height data comes from USGS elevation query point service.
The queried heights are saved in a local file (text based).
This local elevation store will speed up future runs of a job that uses the same elevation coordinates.

The script is driven by a configuration file that specifies the parameters of a "slice job" and how to configure the svg output.
The file example-slicejob.json is a good starting example (more documentation to come)

