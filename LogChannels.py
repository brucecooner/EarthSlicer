class LogChannels:
	def __init__(self):
		self.silenced = False	# all channels override
		self.channels = {}

	# --------------------------------------------------------
	def silence(self, setting):
		self.silenced = setting

	# ALL CHANNELS GO THROUGH HERE (for global override check)
	def print(self, message):
		if not self.silenced:
			print(message)

	# --------------------------------------------------------
	def addChannel(self, channel_name, channel_prefix = None):
		self.channels[channel_name] = {
			"on": True,
			"prefix": channel_prefix,	# shows before every msg to channel
			"logs": []
		}
		def channelFunc(self, message):
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

