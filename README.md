# EarthSlicer
vertical topography slicer (Python)

EarthSlicer produces a series of vertical "slices" of a specified square of the Earth's surface.
These slices can be specified to run north-south or east-west.

These slices become a series of .svg files for laser cutting (or whatever fun).
Since I use Inkscape, that flavorted the file format I create, and thus I can only guarantee the files will work with Inkscape (download at inkscape.org).

Height data comes from USGS elevation query point service.
The queried heights are saved in a local text file (non-optimal but ok for now).
This local elevation store will speed up future runs of a job that uses the same elevation coordinates.

The script is driven by a json configuration file that specifies the parameters of a "slice job" and how to configure the svg output.

After cloning, enter root and run...

python EarthSlicer.py example-slicejob\EstrellasExample-slicejob.json


An example slice job config is included in the project, see the example-slicejob\ folder.
For more concrete info regarding the parts of the job file, check out SliceJobConfig.py and SVGConfig.py which contain embedded schemas.
