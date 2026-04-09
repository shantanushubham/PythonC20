# Procedural Oriented Programming (POP) - Fortran, Basic, C

# Object Oriented Programming (OOP) - Java, C#, C++, Python, Javascript, TypeScript, Swift, Ruby, etc.
# Class and Object

# Class
# You are an architect working at Prestige Group (Builder) and your job is to design buildings
# You have created a blueprint of a building on a sheet of paper
# You have identified that to make the building that you have designed, we need the following things:
# 1. no of floors
# 2. color

# class = blueprint
# object = what you make from this blueprint

class Building:

  NO_OF_BUILDINGS_NEEDED: int = 10

  @classmethod
  def change_no_of_buildings_needed(cls, num):
    Building.NO_OF_BUILDINGS_NEEDED = num
 
  # A contstructor
  def __init__(self, no_of_floors: int, color: str):
    self.no_of_floors = no_of_floors
    self.color = color

  # Class Member
  def change_to_new_color(self):
    print(self.no_of_floors, self.color)
    self.color = "NewColor"

  def change_no_buildings(self, num: int):
    self.NO_OF_BUILDINGS_NEEDED = num

  @classmethod
  def test_function(cls, data):
    # cls means the class itself.
    # cls = Building
    no_floors, color = data.split(",")
    return cls(no_floors, color)
    # Building(no_floors, color)


# object of Builing
my_building1 = Building(10, "Yellow")
my_building2 = Building(5, "Red")
my_building3 = Building(6, "White")
my_building4 = Building(12, "Lime Green")

# print(my_building1.color)
# my_building2.change_to_new_color()
print(Building.NO_OF_BUILDINGS_NEEDED)
my_building1.change_no_buildings(15)
print(my_building1.NO_OF_BUILDINGS_NEEDED)

my_building5 = Building.test_function("11,Pink")
print(my_building5.color)
# Self keyword is always used inside a class. It is related to class and its object
# In Python, every function inside a class needs to have "self" as the 1st argument of the function, if arguments are needed.
# Only that makes it a member of the class.
# 1. Inside a Constructor
  # self = the object of the class that is going to be created
# 2. Outside a Constructor
  # self = the object of the class which was used to call the member of the class