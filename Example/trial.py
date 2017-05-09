import Test1
from East import Test

class TrialDriver(Test):
  def __init__(self):
    super().__init__()
    self.test_object = Test1.Test1()
    self.add(self.test1)
    self.add(self.test2)
    self.add(self.test3)
    self.add(self.test4)
    self.add(self.test5)
    self.add(self.test6)
    self.add(self.test7)
    self.add(self.test8)
    self.add(self.test9)
    self.add(self.test10)
    self.add(self.test11)
    self.add(self.test12)
    self.add(self.test13)
    self.add(self.test14)
    self.add(self.test15)
    self.add(self.test16)
    self.run()

  def test1(self):
    self.note("AND/OR Test:")
    self.note("Last condition is shortcircuit")
    self.check(False, self.test_object.and_test(True, True, False))
    self.check(True, self.test_object.or_test(False, False, True))

  def test2(self):
    self.note("AND/OR Test:")
    self.note("Middle condition is shortcircuit")
    self.check(False, self.test_object.and_test(True, False, True))
    self.check(True, self.test_object.or_test(False, True, False))

  def test3(self):
    self.note("AND/OR Test:")
    self.note("First condition is shortcircuit")
    self.check(False, self.test_object.and_test(False, True, True))
    self.check(True, self.test_object.or_test(True, False, False))

  def test4(self):
    self.note("AND/OR Test:")
    self.note("No shortcircuit in gate")
    self.check(True, self.test_object.and_test(True, True, True))
    self.check(False, self.test_object.or_test(False, False, False))

  def test5(self):
    self.note("XOR Test:")
    self.check(True, self.test_object.xor_test(False, True))
    self.check(True, self.test_object.xor_test(True, False))
    self.check(False, self.test_object.xor_test(False, False))
    self.check(False, self.test_object.xor_test(True, True))

  def test6(self):
    self.note("IF#1")
    self.check(1, self.test_object.if_test1(True, True))
    self.check(2, self.test_object.if_test1(True, False))
    self.check(3, self.test_object.if_test1(False, True))
    self.check(-1, self.test_object.if_test1(False, False))

  def test7(self):
    self.note("IF#2")
    self.check(1, self.test_object.if_test2(True))
    self.check(-1, self.test_object.if_test2(False))

  def test8(self):
    self.note("IF#3")
    self.check(1, self.test_object.if_test3(True))
    self.check(-1, self.test_object.if_test3(False))

  def test9(self):
    self.note("FOR#1")
    self.note("Invalid list")
    self.check(0, self.test_object.for_test1(None))

  def test10(self):
    self.note("FOR#1")
    self.note("Valid list...of strings")
    self.check(0, self.test_object.for_test1(["AA", "BB", "CC"]))

  def test11(self):
    self.note("FOR#1")
    self.note("Valid list...of ints!")
    self.check(7, self.test_object.for_test1([1, 2, 4]))

  def test12(self):
    self.note("FOR#2")
    self.note("Mismatch input")
    self.check(1, self.test_object.for_test2("BB"))
    self.note("Complete loop/Execute 'Else'")
    self.check(100, self.test_object.for_test2("AA"))

  def test13(self):
    self.note("WHILE#1")
    self.note("Iterate 0 times")
    self.check(0, self.test_object.while_test1(0))
    self.note("Iterate 1 time")
    self.check(1, self.test_object.while_test1(1))
    self.note("Iterate N times")
    self.check(10, self.test_object.while_test1(10))

  def test14(self):
    self.note("WHILE#2")
    self.note("Iterate 0 times, Limit of 5")
    self.check(100, self.test_object.while_test2(0, 5))
    self.note("Iterate 1 time, Limit of 5")
    self.check(101, self.test_object.while_test2(1, 5))
    self.note("Iterate 4 times, Limit of 5")
    self.check(104, self.test_object.while_test2(4, 5))
    self.note("Iterate 5 times, Limit of 5")
    self.check(0, self.test_object.while_test2(5, 5))
    self.note("Iterate N times, Limit of 5")
    self.check(0, self.test_object.while_test2(6, 5))

  def test15(self):
    self.note("Value in List")
    self.note("Checking for None, True")
    self.check(False, self.test_object.value_in_list(None, True))
    self.note("Checking for AA, False")
    self.check(False, self.test_object.value_in_list("AA", False))
    self.note("Checking for AA, True")
    self.check(True, self.test_object.value_in_list("AA", True))

  def test16(self):
    self.note("Chain")
    self.note("Input is too small")
    self.check(False, self.test_object.chain(-1))
    self.note("Input is too large")
    self.check(False, self.test_object.chain(11))
    self.note("Input is just right")
    self.check(True, self.test_object.chain(5))

if __name__ == "__main__":
  TrialDriver()
