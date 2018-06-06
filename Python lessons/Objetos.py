Objetos:
		-Representación de una cosa
		-Los objetos representan items/cosas.
		-Tipos de datos: vectores variables y usarlos mas dinamicamente
		-
Clase=molde que me permite crear objetos

EJEMPLO:
import random
##Para convertir esto en una clase se hace:
class Dado
	#constructor
	#se ejecuta al crear un objeto de esta clase
	#self es los que te permite usar las funciones
	def __init__ (self, lados):
		self.cantidad_caras=lados
		self.numero= random.randragne(1,lados+1)

	def tirar(self):
		self.numero= random.randragne(1,lados+1)
		
	#Atributos:
	#			numero
	#			cantidad de caras	

	#Métodos:
	#			tirar

#instanciar un objeto clase Dado
# a es un objeto clase Dado		
a= Dado(6)



