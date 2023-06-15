# kinda sucks that you might NOT see the exception you expect, need a better
# way to detect test pass/fail based on specific exceptions
# ------------------------------------------------------------
def testForException(test_name:str, test_func):
	print(f"TEST: {test_name}")
	try:
		test_func()
	except Exception as exc:
		print(f"\tThrew Exception: {exc}")
	else:
		print(f"\tFAILED: Did NOT throw exception")

# ------------------------------------------------------------
def testForNoException(test_name:str, test_func):
	print(f"TEST: {test_name}")
	try:
		test_func()
	except Exception as exc:
		print(f"\tFAILED with  Exception: {exc}")
	else:
		print(f"\tPASSED")

