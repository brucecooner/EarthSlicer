# Singleton for tracking average timing of an operation
import time

# TODO:
#	* report optionally reports timers still running
#	* startTimer(), addTiming() return ID's that can be re-used, to prevent bugs due to magic strings

#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
class GTimer:	# The G stands for Groceries
	_instance = None

	def __new__(cls):
		if cls._instance is None:			
			cls._instance = super(GTimer, cls).__new__(cls)
			# Put any initialization here.
			cls._instance.init()
		return cls._instance

	# ----------------------------------------------------
	def init(self):
		# accumulated data about timers that have ran
		self.timings = {}
		# individual timERs, note that these can be directed 
		# arbitrarily to a timING
		self.timers = {}

	# ----------------------------------------------------
	def addTiming(self, name, time):
		if not name in self.timings:
			# could just keep an array of all the timings, but takes less memory to accumulate them
			new_timing = { "count" : 0, "total_time" : 0.0 }
			self.timings[name] = new_timing

		cur_timing = self.timings[name]
		cur_timing["count"] += 1
		cur_timing["total_time"] += time

	# ----------------------------------------------------
	def startTimer(self, name):
		if name in self.timers:
			raise Exception(f"already a timer named {name}")
		
		self.timers[name] = time.perf_counter()

	# ----------------------------------------------------
	def markTimer(self, timer_name, timing_name):
		mark_time = time.perf_counter()

		if not timer_name in self.timers:
			raise Exception(f"timer not found: {timer_name}")
		
		timer_begin_time = self.timers[timer_name]
		total_time = mark_time - timer_begin_time

		self.addTiming(timing_name, total_time)

		# free timer name for future use, maybe
		self.timers.pop(timer_name, None)

	# ----------------------------------------------------
	def report(self, ind = "\t"):
		str_rep = "Timings:\n"
		for cur_name, cur_timing in self.timings.items():
			cur_avg = cur_timing['total_time'] / cur_timing['count']
			str_rep += f"{ind}{cur_name} - total:{cur_timing['total_time']}"
			str_rep += f" count:{cur_timing['count']} avg:{cur_avg}\n"

		return str_rep
#------------------------------------------------------------------------------
gtimer = GTimer()
