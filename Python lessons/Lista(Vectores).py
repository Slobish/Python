Listas:

    La variable se guarda entre Corchetes "[]".
    En ellas se puede guardar cualquier tipo de variable.

    Ejemplo:
        Programa:
            lista = [1,2,3,4,5,6,"hola",8]
            #Si quiero pedir un elemento de la lista, lo llamo con la variable y el [bit]
            lista[0] = 1
            con - empiezo a contar desde atras, y con n el bit desde atràs que querìa.

    IMPORTANTE: #LAS LISTAS SON MUTABLESSSSSSS
                Ejemplo:
                    Programa:
                        lista = [1,2,3,4,5,6,"hola",8]
                        lista[0] = 45
                        lista = [45,2,3,4,5,6,"hola",8]
                        
    Comandos de màs para los "Vectores" de Python (Listas):
        lista.sort()#Te lo ordena alfabetico en caso de string y por valor en caso de num
        lista.reverse()#Lo da vuelta
        lista.pop(bit)#Saca el final o el bit que desees
        lista.append() #Agrega lo que pongas al final
        lista.insert(b, input )#Agrega en el bit "b" el "input" que se desea. se desplaza el
        # que estaba antes.
        lista.remove("b")# Te remueve el string o numero que desees
        lista.count("b")#Te cuenta cuantas veces esta b en lista
        lista.index(b)#Te cuenta en que bit esta b
        objeto_lista.extend(lista)#Te suma el objeto y la lista, pero el extend te lo guarda en la
        #vector que guardes entre ().
        lista.copy()# Te copia dos listas y te las guarda en diferentes espacios de memoria.
        
        
        
