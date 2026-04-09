class Test:

  def __init__(self, my_num) -> None:
    # member of the class
    self.my_num = my_num

  @classmethod
  def test_function(cls):
    print("Hello World")
    print(cls.test_function_2())

  @classmethod
  def test_function_2(cls):
    print("Hello World 2")

# t = Test()
# t.test_function()
Test.test_function()