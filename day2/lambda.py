# Lambda is a function which is written in 1 line only in Python
class Demo:

  def __init__(self, age, name) -> None:
    self.name = name
    self.age = age

def add_numbers(*args): #varargs [1, 2]
  sum = 0
  for i in range(0, len(args)):
    sum = sum + args[i]
  
  return sum

# lambda argumnets without brackets : expression (1 line only)
add_numbers_lambda = lambda a, b: a + b

lambda *args: sum(args)

print(add_numbers(1, 2))
# print(add_numbers_lambda(1, 2))


students = [
  ("Shantanu", 90, 27),
  ("Aman", 90, 26),
  ("Riya", 85, 25)
]

test_list = [Demo(25, "Shantanu"), Demo(30, "Ajay")]


# We want to sort the student list
sorted_students = sorted(students, key=lambda a: a[-1])
print(sorted_students)
