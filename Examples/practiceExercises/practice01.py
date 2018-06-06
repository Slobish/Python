number = input("Please enter a number between 1 and 100: ")
number = int(number)

while( number < 1 or number > 100 ):
    number = int(input("Out of range. Enter again: "))

print("The number you entered is ", end="")
if( not(number % 2) ):
    print("even")
else:
    print("odd")
