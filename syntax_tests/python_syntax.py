"""A Python syntax highlighting test.

Below are a lot of different kinds of python code to view what the syntax
highlighting for it will look like.
"""
import os


def my_function(x):
  for i in range(x):
    print(i, 'is a great number!')


class MyClass:
  def __init__(self):
    self.prop_1 = 1
    self.prop_2 = 'two'
    self.prop_3 = False

  def my_method(self, param_1, param_2):
    self.prop_1 = param_1
    self.prop_2 = param_2
    self.my_static_method(num_1=param_1, num_2=param_2)

  @staticmethod
  def my_static_method(num_1, num_2):
    nums_sum = sum(num_1, num_2)
    print(nums_sum)


def main():
  my_number = 42
  my_complex_number = 2 + 3j

  my_bool = True

  my_string = 'A string\n'
  my_b_string = b'newline:\n also newline:\x0a'
  my_u_string = u"Cyrillic Я is \u042f. Oops: \u042g"
  my_f_string = f'My previous string, {my_string}, was great.'
  my_tri_string = """This is a triple quoted string"""
  an_unused_variable = 'This is not returned, so it is never used.'

  # TODO: This is what a todo item looks like.
  my_char = my_string[0].lower()

  my_tuple = ("Test", 2 + 3, {'a': 'b'}, f'My str {my_number!s:{"^10"}}')

  # A single line comment.
  my_list_of_strings = ['a', 'b', 'c', 'c']
  my_list_of_number = [1, 2, 3, 4]
  my_dict = {
    'a': 1,
    'b': 2,
    '3': 3,
  }

  my_function(10_000)

  str_len = len('abc')
  with open(os.path.abspath(__file__)) as f:
    print(f.read())

  return (my_number, my_complex_number, my_bool, my_string, my_b_string,
          my_u_string, my_f_string, my_tri_string, my_char, my_tuple,
          my_list_of_strings, my_list_of_number, my_dict, str_len)


if __name__ == '__main__':
  main()
