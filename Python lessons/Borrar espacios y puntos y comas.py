def espacios(frase):
    for n in frase:
        if(n!=" " and n!="." and n!=","):
            print(n,end="")

a=input("Ingrese frase: ")
espacios(a)
