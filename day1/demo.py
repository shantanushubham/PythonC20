# Conditonal Programming
# 1. if-else
# 2. switch-case X

# a = 15

# if a < 10:
#   print("Less than 10")
# elif a >= 10 and a <= 20:
#   print("Between 10 and 20")
# else:
#   print("More than 20")

# Functions
# y = square(x)
# square(x) =  x * x
# y = dependent variable
# x = independent variable
# square = function
# y = square(2)
# In order to create a function in Python, we use "def"


# def square(x) -> float:
#     sq = x * x
#     print(sq)
#     return sq


# y: float = square(2)
# z: float = square(3)
# print(y)
# print(z)


def add_two_numbers(a: int, b: int) -> int:
    return a + b


result: int = add_two_numbers("Shantanu", "Shubham")
print(result)
