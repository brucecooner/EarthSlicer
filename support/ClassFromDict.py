# class that takes a dict and adds specified keys as class memebers
class ClassFromDict:
	def __init__(self, from_dict = None):
		if from_dict:
			self.addProperties(from_dict)

	def addProperties(self, src_dict:dict, only_keys:list = None):
		if only_keys:
			for cur_key in only_keys:
				self[cur_key] = src_dict[cur_key]
		else:
			for cur_key,cur_value in src_dict.items():
				self[cur_key] = cur_value

	# ------------------------------------------
	def __getitem__(self, item):
			return getattr(self, item)

	# ------------------------------------------
	def __setitem__(self, key, value):
			return setattr(self, key, value)

# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------
if __name__ == "__main__":
	print("--------------------------")
	print("messing with ClassFromDict")

	source_d = {"key1":"val1", "key2":2, "key3": "third value", "key4": 4.444}

	print("--------------------------")
	print("all keys")
	test_c1 = ClassFromDict(source_d)
	print(test_c1)
	print(f"key1 : {test_c1.key1}")
	print(f"key2 : {test_c1.key2}")
	print(f"key3 : {test_c1.key3}")
	print(f"key4 : {test_c1.key4}")

	print("--------------------------")
	print("filtered keys")
	keys_l = ["key1", "key3"]
	test_c2 = ClassFromDict(source_d, keys_l)
	print(test_c2)
	print(f"key1 : {test_c2.key1}")
	print(f"key3 : {test_c2.key3}")
	try:
		print(f"key4: {test_c2.key4}")
	except Exception as exc:
		print(f"Threw exception: {exc}")
	else:
		print(f"NO exception?")
	

	print("--------------------------")
	print("derived class...")
	class DerivedClass(ClassFromDict):
		def __init__(self, src_dict:dict):
			ClassFromDict.__init__(self, src_dict)
			self.derived = True

	test_dc = DerivedClass(source_d)
	print(test_dc)
	print(f"key1 : {test_dc.key1}")
	print(f"key2 : {test_dc.key2}")
	print(f"key3 : {test_dc.key3}")
	print(f"key4 : {test_dc.key4}")
