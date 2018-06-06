def invertir(frase):
    a=len(frase)
    while(a!=0):
        print(frase[a-1],end="")
        a=a-1
f=input("Ingrese frase a invertir: ")
invertir(f)
