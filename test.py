def fuzzy_math (num1, operator, num2):
    if type(num1) != int or type(num2) != int:
        raise Exception("We need to do fuzzy_math with int.")

    if operator == "+":
        result = num1 + num2
    elif operator == "*":
        result = num1 * num2
    else:
        raise Exception(f"I do not do math with '{operator}'.")

    if result < 0:
        return 'A negative number.'
    elif result < 10:
        return 'A small number.'
    elif result < 20:
        return 'A medium number.'
    else:
        return 'A very big number.'
    
class TestFuzzyMath:
    
    def test_non_int_input_num1(self):
        pass
    
    # Exception - how to use
    # If condition returns True, then nothing happens.
    # If condition returns False , AssertionError is raised.
        # EXAMPLE
        # x = "hello"
        # if condition returns False, AssertionError is raised:
        # assert x == "goodbye", "x should be 'hello'"
    def test_non_int_input_num2(self):
        error = None
        try:
            fuzzy_math(2, '+', "hi")
        except Exception as e:
            error = e
        assert error is not None
    
    def test_addition_with_negative_result(self):
        pass
    
    # lines 33 and 36 are the same types of conditions, but put differently.
    def test_addition_with_small_result(self):
        assert fuzzy_math(2, '+', 2) == 'A small number.'
    
    # lines 33 and 36 are the same types of conditions, but put differently.       
    def test_addition_with_medium_result(self):
        assert "A medium number." in fuzzy_math(12, '+', 2)
    
    def test_addition_with_big_result(self):
        pass
    
    def test_multiplication_with_negative_result(self):
        pass

    def test_multiplication_with_small_result(self):
        assert "A small number." in fuzzy_math(3, '*', 2)

    def test_multiplication_with_medium_result(self):
        assert fuzzy_math(3, '*', 5) == 'A medium number.'

    def test_multiplication_with_big_result(self):
        pass

    def test_invalid_operator(self):
        error = None
        try:
            fuzzy_math(2, '-', 5)
        except Exception as e:
            error = e
        assert error is not None