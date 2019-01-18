#!/usr/bin/env python3

class Test1:
  VARIABLE_X = 1
  def __init__(self):
    # only done as a class for testing purposes
    pass

  def and_test(self, 
    in_a, 
    in_b, 
    in_c):
    return (in_a 
            and in_b 
            and in_c)

  def or_test(self, in_a, in_b, in_c):
    return in_a or in_b or in_c

  def xor_test(self, in_a, in_b):
    return (in_a or in_b) and not (in_a and in_b)

  def if_test1(self, in_a, in_b):
    ret_val = -1
    if (in_a 
        and in_b):
      ret_val = 1
    elif in_a:
      ret_val = 2
    elif in_b:
      ret_val = 3
    return ret_val

  def if_test2(self, in_a):
    ret_val = -1
    if in_a:
      ret_val = 1
    return ret_val

  def if_test3(self, in_a):
    return -1 if not in_a else 1

  def for_test1(self, for_vals):
    ret_val = 0
    for aval in for_vals:
      ret_val += int(aval)
    else:
      ret_val = -1
    return ret_val

  def for_test2(self, in_val):
    ret_val = 0
    for a_val in ["AA", "AB", "BA"]:
      if in_val != a_val:
        ret_val += 1
        break
    else:
      ret_val += 100
    return ret_val

  def for_test3(self):
    return list([x for x in range(1000000) if x%4])

  def while_test1(self, loop_count):
    count = 0
    while count < loop_count:
      count += 1
    return count

  def while_test2(self, loop_count, limit):
    count = 0
    while count < loop_count:
      count += 1
      if count == limit:
        count = 0
        break
    else:
      count += 100
    return count

  def value_in_list(self, val, flag):
    return ((val in ["AA", "BB", "CC"]) 
            and flag)

  def chain(self, in_a):
    return (0 <= in_a <= 10)
