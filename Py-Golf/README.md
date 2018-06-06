# Py-Golf

Dado que se puede jugar tanto OFFLINE como ONLINE no es necesario entrar en la carpeta
server para probar modo individual.

En la parte superior derecha hay dos botones, uno alterna los modos OFFLINE/ONLINE y el otro, "INFO", muestra informacion general sobre los modos de juego.

--------------------------------
INSTRUCCIONES PARA JUGAR OFFLINE
--------------------------------

En la carpeta /CLIENTE ejecutar el archivo "launcher.py"
En el menu izquierdo, estando en modo OFFLINE hay varias opciones:
	-PARTIDA: Para elegir un mapa y jugar individualmente
	-SCORE: Tabla de puntuaciones
	-OPCIONES: Para configurar el nombre que quedara registrado en la tabla
	-CREADOR: Para crear tus propios mapas

-------------------------------------
INSTRUCCIONES PARA JUGAR MULTIJUGADOR
-------------------------------------

Para jugar de a varias personas, una de ellas debe ejecutar el programa servidor en su PC para poder permitir la interconexion de todos los programas.

1) Ejecutar el archivo que se encuentra en la carpeta /SERVER con el nombre de "servidor.py"

2) Ingresar un nombre y numero de puerto a utilizar, luego el servidor funcionara de manera autonoma.

3) Seguido a esto, quienes vayan a conectarse deben poner el programa en modo ONLINE, ir a la seccion SERVER, ingresar la IP y el PUERTO donde el servidor esta siendo ejecutado y conectarse.

4) Luego de esto deben acceder a una cuenta, en la seccion CUENTAS se registran y luego entran. Las cuentas son guardadas en una base de datos en el programa servidor.

Finalmente quedan 3 secciones.

-PARTIDA: Se puede ver los usuarios conectados, seleccionar a varios de ellos, junto con un mapa y algunas configuraciones para armar una partida.
Al presionar JUGAR se enviara una invitacion a los demas usuarios para que el juego inicie.

-CHAT: Se puede ver los usuarios conectados, hay una sala de chat y los puntos actuales.
Cada partida ganada da 100 puntos, permitiendo cierta competitividad en el servidor.

-SCORE: Tabla de puntuaciones.
