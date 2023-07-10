# WEB TA PURPOSES
from selenium import webdriver
# FINDING ELEMENTS PURPOSES
from selenium.webdriver.common.by import By
# FINDING ELEMENTS PURPOSES
# !!! RUN THIS FIRST (CMD)
# pip install htmldom==2.0
from htmldom import htmldom
# TEXT PURPOSES
from selenium.webdriver.common.keys import Keys
# WAIT PURPOSES
from selenium.webdriver.support.wait import WebDriverWait
# WAIT PURPOSES
# Shortened version of code (as).
from selenium.webdriver.support import expected_conditions as EC
# SLEEP PURPOSES
import time
# DROPDOWN PURPOSES
from selenium.webdriver.support.select import Select
# SLIDER PURPOSES - IN THIS SCRIPT
from selenium.webdriver.common.action_chains import ActionChains
# RANDOM PURPOSES
# https://www.w3schools.com/python/module_random.asp
# Import the random module, and display a random number between 1 and 9:
import random


# 0  CLASS

class MyClass:
  x = 5

p1 = MyClass()
print(p1.x)
# Result: 5.


# 1  Class __init__() Function

class Person:
  def __init__(self, name, age):
    self.myname = name
    self.myage = age

p1 = Person("John", 36)
print(p1.myname)
print(p1.myage)
# Result: John 36.


# 2  Class __str__() Function

class Person:
  def __init__(self, name, age):
    self.myname = name
    self.myage = age

  def __str__(self):
    return f"{self.myname}({self.myage})"    

p1 = Person("John", 36)
print(p1)
# Result: John(36).


# 3  Object METHODS
# Methods are functions in the objects.

class Person:
  def __init__(self, name, age):
    self.myname = name
    self.myage = age

  def myfunc(self):
    print("Hello my name is " + self.myname)

p1 = Person("John", 36)
p1.myfunc()
# Result: Hello my name is John.


# 4  Modify Object Properties

class Person:
  def __init__(self, name, age):
    self.myname = name
    self.myage = age

  def myfunc(self):
    print("Hello my name is " + self.myname)

p1 = Person("John", 36)
p1.myage = 35
print(p1.myage)
p1.myfunc()
# Result: 35 Hello my name is John.


# 5  del

# 5.1
# DELETE PROPERTY OF OBJECT
# del p1.myage

# 5.2
# DELETE WHOLE OBJECT
# del p1


# 6  PARENT AND CHILD CLASSES

# 6.1  PARENT CLASS
class Person:
  def __init__(self, fname, lname):
    self.firstname = fname
    self.lastname = lname

  def bothnames(self):
    print(self.firstname, self.lastname)

#Use the Person class to create an object, and then execute the bothnames method.
x = Person("John", "Doe")
x.bothnames()
# Result: John Doe.

# 6.2  CHILD CLASS
class Person:
  def __init__(self, fname, lname):
    self.firstname = fname
    self.lastname = lname

  def bothnames(self):
    print(self.firstname, self.lastname)

class Student(Person):
  pass

x = Student("Steve", "Olsen")
x.bothnames()
# Result: Steve Olsen.

# 6.3
# The __init__() function is called automatically every time the class is being used to create a new object.
# The child's __init__() function overrides the inheritance of the parent's __init__() function.
# To keep the inheritance of the parent's __init__() function, add a call to the parent's __init__() function.
class Person:
  def __init__(self, fname, lname):
    self.firstname = fname
    self.lastname = lname

  def bothnames(self):
    print(self.firstname, self.lastname)

class Student(Person):
  def __init__(self, fname, lname):
    Person.__init__(self, fname, lname)

x = Student("Steve", "Olsen")
x.bothnames()
# Result: Steve Olsen.

# 6.4  Class super() Function
class Person:
  def __init__(self, fname, lname):
    self.firstname = fname
    self.lastname = lname

  def bothnames(self):
    print(self.firstname, self.lastname)

class Student(Person):
  def __init__(self, fname, lname, year):
# Using super() to access __init__() method of Person (PARENT CLASS).
    super().__init__(fname, lname)
    self.graduationyear = year

  def welcome(self):
    print("Welcome", self.firstname, self.lastname, "to the class of", self.graduationyear)

x = Student("Steve", "Olsen", 2019)
x.welcome()
# Result: Welcome Steve Olsen to the class of 2019.