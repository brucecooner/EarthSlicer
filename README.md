# EarthSlicer
vertically oriented topography extractor (Python)

---
PLEASE NOTE: I haven't focused on this readme yet, so this is a not-entirely-useful mess.
I plan on improving it when I have more time to devote to this project.
---

EarthSlicer produces a series of vertical "slices" of a specified square of the Earth's surface.
How many slices to take over this square, their orientation (north-south or east-west), and how many elevation samples to take
across each slice can also be specified.

These slices become a series of .svg files for laser cutting (or whatever fun).
Since I use Inkscape, that flavored the file format I create, and thus I can only guarantee the files will work with Inkscape (download at inkscape.org).

Height data comes from USGS elevation query point service.
The queried heights are saved in a local text file (non-optimal but ok for now).
This local elevation store will speed up future runs of a job that uses the same elevation coordinates.

The script is driven by a json configuration file that specifies the parameters of a "slice job" and how to configure the svg output.

An example slice job config is included in the project, see the example-slicejob\ folder.
After cloning, enter root and run...

python EarthSlicer.py example-slicejob\EstrellasExample-slicejob.json

For more concrete info regarding the parts of the job file, check out SliceJobConfig.py and SVGConfig.py which contain embedded schemas.
