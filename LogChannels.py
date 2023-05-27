# Singleton for creating arbitrary channels to receive logging
#
# Usage:
# from LogChannels import log
#
# # create my channels
# log.addChannel("echo")
# log.addChannel("debug")
# log.addChannel("todo")
# log.addChannel("foo")
#
# log.echo("normal operational message!")
# log.todo("reticulate splines")
# log.debug(f"power level = {power_level}")
# log.foo("whimsical missive")
#
# # add a prefix to a channel:
# log.addChannel("info", "info") # these don't need to match, but really should
# log.info("important info")
# # outputs: info: important info
#
# # silence a single channel:
# log.setChannel("debug", False) 
# log.debug("hushed") # this produces no output (but is still added to internal log)
# log.setChannel("debug", True) # debug channel output resumes
#
# # silence ALL channels
# log.silence()
# # <no more output from any channel>

# TODO:
#	* I don't like the setChannel() method, rename it
#	* also awkward going through log to silence a channel, can we engineer a way to 
#	 		silence a channel THROUGH that channel? like... log.echo.silence(True)
#			Oof, that's going to be making the channels into callable classes...give me a few minutes on that one.
#	* dump a channel (already storing all messages)


#  ----------------------------------------------------------------------------
#  ----------------------------------------------------------------------------
class LogChannels:
	_instance = None

	def __new__(cls):
		if cls._instance is None:			
			cls._instance = super(LogChannels, cls).__new__(cls)
			# Put any initialization here.
			cls._instance.init()
		return cls._instance

	def init(self):
		self.silenced = False	# all channels override
		self.channels = {}

	# --------------------------------------------------------
	def silence(self, setting = True):
		self.silenced = setting

	# ALL CHANNELS GO THROUGH HERE (for global override check)
	def print(self, message):
		if not self.silenced:
			print(message)

	# --------------------------------------------------------
	def addChannel(self, channel_name, channel_prefix = None):
		# only create channel once
		if channel_name not in self.channels:
			self.channels[channel_name] = {
				"on": True,
				"prefix": channel_prefix,	# shows before every msg to channel
				"logs": []
			}
			def channelFunc(self, message = ""):
				channel_info = self.channels[channel_name]
				channel_info["logs"].append(message)
				if channel_info["on"]:
					prefix = channel_info["prefix"] + ":" if channel_info["prefix"] else ""
					self.print(f"{prefix}{message}")

			setattr(LogChannels, channel_name, channelFunc)

	# --------------------------------------------------------
	def setChannel(self, channel_name, on):
		channel_info = self.channels[channel_name]
		channel_info["on"] = on

#------------------------------------------------------------------------------
log = LogChannels()
