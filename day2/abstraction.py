from abc import ABC, abstractmethod
from typing import override

"""
  1. An abstract class is a class.
  2. An abstract class CANNOT have an object.
  3. An abstract can have "abstract" or "non-abstract" functions.
  4. An "abstract" function is a function that has
    a. A name
    b. Arugments
    c. Return Type (in languages in C++/Java)
  But it doesn't have a function body
  5. Every child of an abstract class must implement/override the abstract functions present in the Abstract Class.
"""

class Engine(ABC):

    @abstractmethod
    def start(self):
      pass

    @abstractmethod
    def stop(self):
      pass

    def non_abs(self):
      print("Non abstract")

class PetrolEngine(Engine):

    @override
    def start(self):
        print("Petrol Engine Starting")

    @override 
    def stop(self):
        print("Petrol Engine Stopping")


class ElectricEngine(Engine):

    @override
    def start(self):
        print("Electric Engine Starting")

    @override
    def stop(self):
        print("Electric Engine Stopping")

  
engine = ElectricEngine()
engine.start()

p_engine = PetrolEngine()
p_engine.start()