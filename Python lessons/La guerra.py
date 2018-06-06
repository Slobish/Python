import random
maso=[1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,10,10,10,10,11,11,11,11,12,12,12,12]
j1=[]
j2=[]
n=0
ronda=0
a=0
empate=0

while(n!=40):
    j1.insert(n,maso[n])
    n=n+1
    j2.insert(n,maso[n])
    n=n+1
random.shuffle(j1)
random.shuffle(j2)

while(1):
    if(len(j1)==0 or len(j2)==0):
        break         
    if(empate==1):
        print(" Se tira una carta de cada jugador dada vuelta ")
    else:
        if(j1[ronda]<j2[ronda]):
            print(j1[ronda],"<",j2[ronda])
            print(" Gana jugador 2 ")
            j2.append(j1[ronda])
            j1.pop(j1[ronda])
            ronda=ronda
        if(j1[ronda]>j2[ronda]):
            print(j1[ronda],">",j2[ronda])
            print(" Gana jugador 1 ")
            j1.append(j2[ronda])
            j2.pop(j2[ronda])
            ronda=ronda
    empate=0
    if(j1[ronda]==j2[ronda]):
        print("Empate")
        empate=1
    a=input(" Siguiente turno ")
    if(len(j1)<len(j2)):
        ronda=len(j1)+1       
    if(len(j1)>len(j2)):
        ronda=len(j2)+1   
    if(len(j1)==len(j2)):
        ronda=len(j1)+1
        

    
