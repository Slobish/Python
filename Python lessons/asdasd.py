##a=input("Ingrese string :")
##b=0
##b=int(input("Ingrese valor :"))
##for n in a:
##    print(a[0:b],end="")
##    b=b-1
##    if(b==0):
##        break

d=input("Ingrese palabra capicua : ")
e=d[::-1]
if(d==e):
    print("Capicua")
else:
    print("No es capicua")
