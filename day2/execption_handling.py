class NumberInvalidException(Exception):
  pass

def test_function():
  arr = [1, 2, 3]
  try:
    print(arr[4]) # We know that this line can throw IndexError + 3 other unknown exceptions
  except Exception as e:
    print("Please mention correct index")
    print(e)

test_function()

def validate_num(num: int):
  if (num >= 10 and num <=30):
    print("Num is: " + num + " and is valid.")
  else:
    raise NumberInvalidException("The number is invalid.")

def test_validate(num):
  try:
    validate_num(num)
  except Exception as e:
    print(e)
  finally:
    # The logic that we want whether an exception occurred or not
    print("Inside Finally")

test_validate(40)
test_validate(20)