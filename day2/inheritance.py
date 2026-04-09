

class Parent1:

  def __init__(self, name: str) -> None:
    self.name = name

  def test_function(self):
    print("Inside Parent 1")

class Child(Parent1):

  def __init__(self, name: str, val: int) -> None:
    self.name = name

  def test_function(self):
    print("Inside Child")

  def child_function(self):
    p = Parent1("Shatanu")
    p1 = super("Shantanu")
    print("Inside Child")

  # def demo_function(self):
  #   super().test_function()
  #   super().my_function()


c = Child("Shantanu", 21)
c.test_function()


