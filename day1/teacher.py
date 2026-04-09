class Teacher:

  def __init__(self, first_name, last_name, dob) -> None:
    self.first_name = first_name
    self.last_name = last_name
    self.dob = dob

  @classmethod
  def get_no_teachers(cls):
    return 10

my_teacher = Teacher("Arun", "Kumar", "1990-10-21")
print(my_teacher.get_no_teachers())
print(Teacher.get_no_teachers())