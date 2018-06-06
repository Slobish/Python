import math

a = 0
f = 0
g = 0
b = 0
h = 0
base = 0
perimetro = 0
tr = 0
print("Ingrese 1 si quiere que sea isoceles, 2 si quiere que sea equilatero y 3 si quiere que sea escaleno")
tr = input()
tr = int(tr)

if(tr==3):
    print("Escaleno Ingrese lado A")
    
    a = input()

    print("Ingrese lado F")
    f = input()
    print("Ingrese lado G")
    g = input()
else:
    if(tr==2):
        print("Equilatero Ingrese valor de lado")
    
        a=f=g= input()
else:
    print("Isoceles Ingrese primero los dos lados iguales y luego el distinto")
    a = f = input()
    g = input()
    
a=int(a)
f=int(f)
g=int(g)
b=int(b)
h=int(math.sqtr((a**2)-((b/2)**2))
perimetro=int(perimetro)
base=int(g)

perimetro = a+f+g
print("El perimetro es ")
print(perimetro)
print("El area es")
print((b*h)/2)

