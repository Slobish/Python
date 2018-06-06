import datetime

todays = datetime.datetime.now()

name = input("Please enter your name: ")
age = input("Please enter your age: ")

age = int(age)
yearsLeft = 100 - age
res = todays.year + yearsLeft

print("You will be 100 years old in " + str(res))
