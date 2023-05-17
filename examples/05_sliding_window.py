#
#  Homework - Dynamic Programming - Moving Window
#
#  Problem 1: Max Consecutive Sum
#
#  Prompt:    Given a list of integers find the sum of consecutive values in the
#             list that produces the maximum value.
#
#  Input:     Unsorted list of positive and negative integers
#  Output:    Integer (max consecutive sum)
#
#  Example:   input = [6, -1, 3, 5, -10]
#             output = 13 (6 + -1 + 3 + 5 = 13)
#
#  Resources:
#    1: https://projecteuler.net/problem=15
#    2: https://en.wikipedia.org/wiki/Lattice_path
#
#
#
#  Problem 2: Bit Flip
#
#  Prompt:    Given a list of binary values (0 and 1) and N number of flips (convert a
#             0 to a 1), determine the maximum number of consecutive 1's that can be
#             made.
#
#  Input:     A list of 1's and 0's, and an Integer N denoting the number of flips
#  Output:    Integer
#
#  Example:   bit_flip([0,1,1,1,0,1,0,1,0,0], 2)
#  Result:    7
#

# Time Complexity: O(N)
# Auxiliary Space Complexity: O(1)
def max_consecutive_sum(lst):
    if len(lst) == 0:
        return 0
    local_max = lst[0]
    ultimate_max = lst[0]
    for i in range(1, len(lst)):
        local_max = max(local_max + lst[i], lst[i])
        ultimate_max = max(local_max, ultimate_max)
    return ultimate_max


# Time Complexity: O(N)
# Auxiliary Space Complexity: O(N)
def bit_flip(lst, n):
    start, end, maxLength = 0, 0, 0
    count = n
    while (end < len(lst)):
      if lst[end] == 0:
        count -= 1

      while (count < 0):
        if lst[start] == 0:
          count += 1
        start += 1

      maxLength = max(maxLength, end - start + 1)
      end += 1

    return maxLength


############################################################
###############  DO NOT TOUCH TEST BELOW!!!  ###############
############################################################

# custom assert function to handle tests
# input: count {List} - keeps track out how many tests pass and how many total
#        in the form of a two item array i.e., [0, 0]
# input: name {String} - describes the test
# input: test {Function} - performs a set of operations and returns a boolean
#        indicating if test passed
# output: {None}
def expect(count, name, test):
    if (count is None or not isinstance(count, list) or len(count) != 2):
        count = [0, 0]
    else:
        count[1] += 1

    result = 'false'
    error_msg = None
    try:
        if test():
            result = ' true'
            count[0] += 1
    except Exception as err:
        error_msg = str(err)

    print('  ' + (str(count[1]) + ')   ') + result + ' : ' + name)
    if error_msg is not None:
        print('       ' + error_msg + '\n')


print('max_consecutive_sum Tests')
test_count = [0, 0]


def test():
    example = max_consecutive_sum([6, -1, 3, 5, -10])
    return example == 13


expect(test_count, 'should work on example input', test)


def test():
    example = max_consecutive_sum([5])
    return example == 5


expect(test_count, 'should work on single-element input', test)


def test():
    example = max_consecutive_sum([])
    return example == 0


expect(test_count, 'should return 0 for empty input', test)


def test():
    example = max_consecutive_sum([-1, 1, -3, 4, -1, 2, 1, -5, 4])
    return example == 6


expect(test_count, 'should work on longer input', test)

print('PASSED: ' + str(test_count[0]) + ' / ' + str(test_count[1]) + '\n\n')

print('Bit Flip Tests')
test_count = [0, 0]

def test():
  example = bit_flip([0,1,1,1,0,1,0,1,0,0], 2)
  return example == 7
expect(test_count, 'should handle example case', test)

def test():
  example = bit_flip([0], 0)
  return example == 0
expect(test_count, 'should handle smaller edge case where flip is not allowed', test)

print('PASSED: ' + str(test_count[0]) + ' / ' + str(test_count[1]) + '\n\n')