import time
# track runtime of specific actions (in English maybe?)


class TimingTrace:
	def __init__(self, timer_name):
		self.trace_name = timer_name
		self.timings = []

	def start(self):
		self.last_mark = time.perf_counter()

	def mark(self, timing_name):
		mark_time = time.perf_counter()
		new_timing = {"name":timing_name, "time":mark_time - self.last_mark }
		self.timings.append(new_timing)
		self.last_mark = mark_time

	def total_time(self):
		return sum((cur_timing["time"] for cur_timing in self.timings), 0)

	def __repr__(self) -> str:
		string_rep = f"Timer: {self.trace_name}  (total_time:{self.total_time()})\n"
		for cur_timing in self.timings:
			string_rep += f"\t{cur_timing['name']} : {cur_timing['time']}\n"
		return string_rep
