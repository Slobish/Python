length = int(input("Largo de la lista: "))
numberList = []

while( length ):
    newNumber = int(input("Elemento nuevo: "))
    numberList.append( newNumber )
    length -= 1

print("Numeros menores a 5:")
for number in numberList:
    if( number < 5 ):
        print(str(number), end=" ")
