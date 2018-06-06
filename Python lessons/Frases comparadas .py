def frases(a,b):
    c=len(a)
    d=len(b)
    e="Son Iguales"
    if(a>b):
        print(a)
    else:
        if(b>a):
            print(b)
        else:
            print("Iguales")
frase1=input("Ingrese frase: ")
frase2=input("Ingrese frase: ")
frases(frase1,frase2)
