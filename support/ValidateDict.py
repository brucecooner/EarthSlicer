# ------------------------------------------------------------------------------------
# validator form:
# {
#	key: { required:bool, types:builtin-type, validation_fn: callable },
# ...
#	validateDict_post_validate_fn : callable (optional)
# }
# Notes:
#		validation_fn must return: True or (result, result_message)

# TODO:
#	* bug for type:dict rules?
#	* validate sub-dicts recursively? want to do this with a lambda that calls validator again?
#	* might be nice to have parameters for validation_fn, maybe, not sure

validateDict_PostValidateFnKey = "validateDictPostFn"

# -------------------------------------------------------------------------------------
def validateIsPositive(val, key):
	return True if val > 0 else (False, f"{key} must be > 0")


# -------------------------------------------------------------------------------------
def checkRule(rule_key, rule):
	# special keys
	if rule_key == validateDict_PostValidateFnKey:
		if not callable(rule):
			raise Exception(f"rule '{rule_key}' must be a callable")
	else:
		# rule must be a dict	
		if type(rule) != dict:
			raise Exception(f"rule '{rule_key}' is not a dict")
		# rule must contain required property
		if "required" not in rule.keys():
			raise Exception(f"rule {rule_key} does not contain property: 'required'(bool)")
		# 'required' property must be type bool
		if type(rule["required"]) != bool:
			raise Exception(f"rule {rule_key} 'required' property value is not a bool")
		# must contain type property
		if "type" not in rule.keys():
			raise Exception(f"rule {rule_key} does not contain property: 'type'")
		# 'type' property must be of type type 
		if type(rule["type"]) != type:
			raise Exception(f"rule {rule_key} 'type' is not a system type")
		# 'validation' property is optional

		if "validation_fn" in rule:
			# if 'validation_fn' property is present, must be a callable
			if not callable(rule["validation_fn"]):
				raise Exception(f"rule {rule_key} 'validation' property 'func' is not a callable")

# -------------------------------------------------------------------------------------
def checkValidator(validator):
	if type(validator) != dict:
		raise Exception("validator is not a dict")
	
	for cur_rule_key, cur_rule in validator.items():
		checkRule(cur_rule_key, cur_rule)


# -------------------------------------------------------------------------------------
def validateDict(validate_dict:dict, rules:dict, throw_on_fail:bool = True, trace_enabled:bool=False):
	validation_result = True
	failures = []
	error_msg_separator = ","

	def trace(msg):
		if trace_enabled:
			print(msg)

	trace(f"validateDict()")
	trace(f"throw_on_fail: {throw_on_fail}")
	trace(f"validating:")
	trace(validate_dict)

	for cur_rule_key, cur_rule_val in rules.items():
		checkRule(cur_rule_key, cur_rule_val)

	has_post_validateFn = False
	for cur_rule_key, cur_rule in rules.items():
		if cur_rule_key == validateDict_PostValidateFnKey:
			has_post_validateFn = True
		else:
			trace(f"validating rule : {cur_rule_key}")
			if cur_rule["required"]:
				trace(f"\trequired")
				if not cur_rule_key in validate_dict:
					trace(f"\tnot present, failure")
					validation_result = False
					failures.append(f"missing property: {cur_rule_key}")
			
			if cur_rule_key in validate_dict:
				trace(f"\t{cur_rule_key} in dict")
				cur_validation_value = validate_dict[cur_rule_key]
				# validate type
				if type(cur_validation_value) != cur_rule["type"]:
					trace(f"\tincorrect type, failure")
					validation_result = False
					failures.append(f"property {cur_rule_key} is not of type {cur_rule['type']}")

				# validation function?
				if "validation_fn" in cur_rule:
					validationFn = cur_rule["validation_fn"]
					fn_result = validationFn(cur_validation_value, cur_rule_key)
					if fn_result != True:
						trace(f"\tvalidation_fn failed: result={fn_result}")
						validation_result = False
						failures.append(f"property {cur_rule_key}: {fn_result[1]}")

	# if there were other errors don't call post validate, it can throw key errors or other stuff
	if has_post_validateFn and validation_result:
		post_validation_result = rules[validateDict_PostValidateFnKey](validate_dict)
		if post_validation_result != True:
			trace(f"\tpost validation failed: result={post_validation_result}")
			validation_result = False
			failures.append(f"post validation : {post_validation_result[1]}")

	if not validation_result and throw_on_fail:
		trace(f"failed and throw_on_fail")
		error_msg = error_msg_separator.join(failures)
		raise Exception(f"{error_msg}")
	


	return validation_result if validation_result else ( validation_result, failures)


# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------
if __name__ == "__main__":
	from TestSupport import testForException, testForNoException

	# -------------------------------------------------------------------------------------------------------
	def test_checkValidator():

		print("---------------------------------------------------")
		print("testing validateRule()")
		print("")

		testForException("rule must be a dict", lambda : checkRule("test_rule", 1))
		testForException("rule must contain 'required' property", lambda : checkRule("test_rule", { "foo":1} ))
		testForException("'required' property must be type bool", lambda : checkRule("test_rule", {"required":1}))
		testForException("must contain 'type' property", lambda : checkRule("test_rule", {"required":True}))
		testForException("'type' property must be of type type", lambda : checkRule("test_rule", {"required":True, "type":1}))

		testForException("if present, 'validation_fn' property must be a callable", lambda: checkRule("test_rule", {"required":True, "type":int, "validation_fn":1}))

		# validateDict_PostValidateFnKey must be a callable
		testForException(f"if present, '{validateDict_PostValidateFnKey}' property must be a callable",
		    lambda: checkRule(validateDict_PostValidateFnKey, 1))

		# fully formed rule, should work
		print()
		print("Test passing case")
		passing_rule = {"required":True, "type":int, "validation":{"func":lambda : True}}
		try:
			checkRule("test_rule", passing_rule)
		except Exception as exc:
			print(f"FAILED with exception: {exc}")
		else:
			print("PASSED")

		# now test overall validator
		print("---------------------------------------------------")
		print("testing validateValidator()")
		print("")
		test_validator = 1
		testForException("validator must be a dict", lambda: checkValidator(test_validator))
		# rule not a dict
		good_rule = {"required":True, "type":int, "validation":{"func":lambda : True}}
		test_validator = { "foo": good_rule,
		    					"bar": 1 }
		testForException("validator rules must all be dicts", lambda: checkValidator(test_validator))
		test_validator = { "foo": good_rule,
		    					"bar": good_rule }
		testForNoException("passing case", lambda: checkValidator(test_validator))

	# ---------------------------------------------------------------------------------------
	def test_validateDict():
		print()
		print("---------------------------------------------------")
		print("testing checkDict()")

		# --------------------------------------------------------
		# "foo" required, must be type int
		validator = { "foo": { "required":True, "type":int } }
		test_dict = {"bar":1}	# missing required property

		print("Expecting missing property 'foo', exception")
		try:
			validateDict(test_dict, validator, True)
		except Exception as exc:
			print(f"caught exception: {exc}")
		else:
			print("NO EXCEPTION?")

		print("Expecting missing property 'foo', NO exception")
		try:
			result = validateDict(test_dict, validator, False)
		except Exception as exc:
			print(f"EXCEPTION: {exc}")
		else:
			print(f"No exception, result = {result}")

		# --------------------------------------------------------
		# "foo" required, type int
		# "bar" required, type int
		print()
		validator = { "foo": { "required":True, "type":int },
						"bar": { "required":True, "type":int },}
		test_dict = {"foo":1}	# missing required property
		testForException("missing properties foo,bar", lambda: validateDict({}, validator))
		testForException("missing property 'bar'", lambda: validateDict(test_dict, validator, True))
		test_dict = { "foo": "baz"}
		testForException("'foo' is incorrect property type, missing 'bar'", lambda: validateDict(test_dict, validator))

		validator = { "foo": { "required":True, "type":int, "validation_fn":lambda val: True if val > 0 and val < 10 else (False, "out of range (0,10)")}}
		test_dict = { "foo": 0 }
		testForException("'foo' is out of range (lower)", lambda: validateDict(test_dict, validator))
		test_dict = { "foo": 10 }
		testForException("'foo' is out of range (upper)", lambda: validateDict(test_dict, validator))

		# some that should pass
		test_dict = { "foo": 1 }
		testForNoException("passes, value in range", lambda: validateDict(test_dict, validator))
		test_dict = { "foo": 9 }
		testForNoException("passes, value in range", lambda: validateDict(test_dict, validator))
		# float type (0,9)
		test_dict = { "float_type":1.1 }
		validator = { "float_type": { "required":True, "type":float, "validation_fn": lambda val: True if val > 0.5 and val < 9.5 else (False, "out of range")}}
		testForNoException("no exception, float  in range", lambda: validateDict(test_dict, validator))
		# should fail
		test_dict = { "float_type": 0.3 }
		testForException("fails with exception, float out of range", lambda: validateDict(test_dict, validator))

		# should fail during post validation
		validator = {	"int1": { "required":True, "type":int, "validation_fn": lambda val: True},
	       				"int2": { "required":True, "type":int, "validation_fn": lambda val: True},
							validateDict_PostValidateFnKey : lambda v_dict : True if v_dict["int1"] < v_dict["int2"] else (False, "int1 is >= int2") }
		failing_dict = { "int1" : 100, "int2":1 }
		testForException("fails with exc. int1 >= int2", lambda : validateDict(failing_dict, validator))


	# ----------------------------------------
	# test_checkValidator()
	test_validateDict()
