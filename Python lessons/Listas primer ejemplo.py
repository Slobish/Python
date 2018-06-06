#   def cortar (v)
#       b=v.copy()
#       b.pop()
#       b.pop(0)
#       print(b)
#       a=[1,2,3,4,5,6,7]
#cortar(a)

def Orden(a):
    c=[]
    c=a.sort(a)
    print(a)
    print(c)
    if(c!=a):
        print("FALSE")
    else:
        print("TRUE")

def Ingresar():
    a =[]
    b =[]
    while(a!="1"):
    
        a=input("Ingrese otro termino mas que desee agregar a la lista y 1 si desea salir ")
        b.append(a)
          
    return b



p=Orden(Ingresar())
print(p)




##a =[]
##b =[]
##while(a!="1"):
##    
##    a=input("Ingrese otro termino mas que desee agregar a la lista y 1 si desea salir ")
##    b.append(a)
##          
##print(b)




    
