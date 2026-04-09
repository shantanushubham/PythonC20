"""
Primitive Data Types [They use pass by value]
1. byte - 1 byte
2. short - 2 byte
3. char - 2 byte
4. int - 4 byte - this
5. float - 4 byte - this
6. double - 16 byte - this
7. long - 16 byte - this
8. boolean - 1 bit - this

1 byte = 8 bits

Non-primitive Data Types [They use pass by reference]
1. All User Defined Classes
2. String
3. Array
4 .....
"""

# a = [1]

# def increment(num: list):
#   # num = num + "1"
#   # print(num)
#   num.append(2)
#   print(num)

# increment(a)
# print(a)

"""
  list in Python
  List of Java
  List of JS/TS
  vector of CPP
"""
from abstraction import PetrolEngine

# # Method 1
# my_list = list()

# # Method 2
# my_list1 = [10, 20, 30, "Shantanu", [55], PetrolEngine()]

# my_list.extend(my_list1)
# my_list.append(2)
# my_list.append(3)
# my_list.remove(10)
# my_list.pop(2)
# print(my_list.__contains__(20))
# print(my_list)

# Tuple is just like a list but you cannot change it after it was created (immutable)

# my_tuple = tuple(1, 2, 3)
# my_tuple1 = (4, 5, 6)

# Set - just like a list but contains only unique values
# my_set = set()
# my_set1 = {1, 2, 4, 4, 2, 1, 5, 7, 1}
# print(my_set)

# Dictionary
"""
  Map<Object, Object> in Java/C#/C++
  Object in JS/TS
"""

# my_dict: dict = {
#     1: "Shantanu",
#     2: "Shubham",
#     3: "Akshat",
#     4: "Drishti",
#     5: "Sakshi",
#     "Test": True,
# }
# my_dict1 = dict()

# my_dict.update({6: "Akshit"})
# print(my_dict)

my_list = [1, 2, 3]
print(my_list[ - 1])