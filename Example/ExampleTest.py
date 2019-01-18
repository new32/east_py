import ExampleLib
import East

class TrialDriver(East.Test):
  def __init__(self):
    super().__init__()
    self.test_object = ExampleLib.Test1()
    self.run(self.logicalAndTests)
    self.run(self.logicalOrTests)
    self.run(self.test5)
    self.run(self.test6)
    self.run(self.test7)
    self.run(self.test8)
    self.run(self.test9)
    self.run(self.test10)
    self.run(self.test11)
    self.run(self.test12)
    self.run(self.test13)
    self.run(self.test14)
    self.run(self.test15)
    self.run(self.test16)
    self.run(self.test17)
    self.run(self.test18)
    self.run(self.test19)

  def logicalAndTests(self):
    self.function("Test1.and_test")
    self.doc("Given no input")
    self.doc("When all parameters are True")
    self.doc("Then the result is True")
    self.check(True, self.test_object.and_test(True, True, True))
    self.doc("When the last parameter is False and all others are True")
    self.doc("Then the result is False")
    self.check(False, self.test_object.and_test(True, True, False))
    self.doc("When the middle parameter is False and all others are True")
    self.doc("Then the result is False")
    self.check(False, self.test_object.and_test(True, False, True))
    self.doc("When the first parameter is False and all others are True")
    self.doc("Then the result is False")
    self.check(False, self.test_object.and_test(False, True, True))

  def logicalOrTests(self):
    self.function("Test1.or_test")
    self.doc("Given no input")
    self.doc("When all parameters are False")
    self.doc("Then the result is False")
    self.check(False, self.test_object.or_test(False, False, False))
    self.doc("When the last parameter is True and all others are False")
    self.doc("Then the result is True")
    self.check(True, self.test_object.or_test(False, False, True))
    self.doc("When the middle parameter is True and all others are False")
    self.doc("Then the result is True")
    self.check(True, self.test_object.or_test(False, True, False))
    self.doc("When the first parameter is True and all others are False")
    self.doc("Then the result is True")
    self.check(True, self.test_object.or_test(True, False, False))

  def test5(self):
    self.doc("XOR Test:")
    self.check(True, self.test_object.xor_test(False, True))
    self.check(True, self.test_object.xor_test(True, False))
    self.check(False, self.test_object.xor_test(False, False))
    self.check(False, self.test_object.xor_test(True, True))

  def test6(self):
    self.doc("IF#1")
    self.check(1, self.test_object.if_test1(True, True))
    self.check(2, self.test_object.if_test1(True, False))
    self.check(3, self.test_object.if_test1(False, True))
    self.check(-1, self.test_object.if_test1(False, False))

  def test7(self):
    self.doc("IF#2")
    self.check(1, self.test_object.if_test2(True))
    self.check(-1, self.test_object.if_test2(False))

  def test8(self):
    self.doc("IF#3")
    self.check(1, self.test_object.if_test3(True))
    self.check(-1, self.test_object.if_test3(False))

  def test9(self):
    self.doc("FOR#1")
    self.doc("Invalid list")
    self.check(0, self.test_object.for_test1(None))

  def test10(self):
    self.doc("FOR#1")
    self.doc("Valid list...of strings")
    self.check(0, self.test_object.for_test1(["AA", "BB", "CC"]))

  def test11(self):
    self.doc("FOR#1")
    self.doc("Valid list...of ints!")
    self.check(7, self.test_object.for_test1([1, 2, 4]))

  def test12(self):
    self.doc("FOR#2")
    self.doc("Mismatch input")
    self.check(1, self.test_object.for_test2("BB"))
    self.doc("Complete loop/Execute 'Else'")
    self.check(100, self.test_object.for_test2("AA"))

  def test13(self):
    self.doc("WHILE#1")
    self.doc("Iterate 0 times")
    self.check(0, self.test_object.while_test1(0))
    self.doc("Iterate 1 time")
    self.check(1, self.test_object.while_test1(1))
    self.doc("Iterate N times")
    self.check(10, self.test_object.while_test1(10))

  def test14(self):
    self.function("Test1.while_test2")
    self.doc("Iterate 0 times, Limit of 5")
    self.check(100, self.test_object.while_test2(0, 5))
    self.doc("Iterate 1 time, Limit of 5")
    self.check(101, self.test_object.while_test2(1, 5))
    self.doc("Iterate 4 times, Limit of 5")
    self.check(104, self.test_object.while_test2(4, 5))
    self.doc("Iterate 5 times, Limit of 5")
    self.check(0, self.test_object.while_test2(5, 5))
    self.doc("Iterate N times, Limit of 5")
    self.check(0, self.test_object.while_test2(6, 5))

  def test15(self):
    self.function("Test1.value_in_list")
    self.doc("Checking for None, True")
    self.check(False, self.test_object.value_in_list(None, True))
    self.doc("Checking for AA, False")
    self.check(False, self.test_object.value_in_list("AA", False))
    self.doc("Checking for AA, True")
    self.check(True, self.test_object.value_in_list("AA", True))

  def test16(self):
    self.doc("Chain")
    self.doc("Input is too small")
    self.check(False, self.test_object.chain(-1))
    self.doc("Input is too large")
    self.check(False, self.test_object.chain(11))
    self.doc("Input is just right")
    self.check(True, self.test_object.chain(5))

  def test17(self):
    self.function("Test1.chain")
    desc = """
Do some really amazing and awesome testing of the function
under test while being the bestest at testing
    """
    self.description(desc)
    self.suspend("Forgot what I was doing...")

  def test18(self):
    self.function("Test1.chain")
    self.description("Iterate through all values from 0 until death")
    val = 0
    while True:
      self.doc("%d within range" % val)
      self.check(self.test_object.chain(val),False,die=True)
      val += 1

  def test19(self):
    self.doc("FOR#3")
    self.test_object.for_test3()

if __name__ == "__main__":
  TrialDriver()
