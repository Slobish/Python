number = int( input("Ingrese un numero: ") )

while( number < 0 ):
    number = int( input("Numeros invalido. Nuevo numero: ") )

divList = []
counter = 1
while( counter <= number ):
    if( not( number % counter ) ):
        divList.append( counter )
    counter += 1

print("Los divisores de " + str(number) + " son: ", end="")
for num in divList:
    print(str(num), end=" ")
