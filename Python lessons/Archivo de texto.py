Archvios de texto (Editor de textos):
	a=open("nombre","acceso")
	Abrir para leer:
		a=open("prueba.txt","w")
		##"a" va a ser mi archivo.
		##Si no existe se crea. Si existe lo borra y crea uno nuevo.
		a.write("Lo que quiero escribir \n")
		##El \n es un caracter mas
		a.close()
	Abrir para agregar
		a=open("prueba.txt","a")
		##No sobrescribi el archivo agrega al lado
		##Si no existe se crea.
		a.write("Lo que quiero escribir \n")
		##El \n es un caracter mas
		a.close()
	Abrir para escribir
		u=open("prueba.txt","r")
		##Si existe se abre y se lee. Si no existe te tira error.
		linea=u.readline()
		print(linea)
		##Te va imprimiendo las lineas.
		lin=u.readlines()
		##Lee todas las lineas y crea una lista
		
SIEMPRE CERRAR LOS ARCHIVOS
