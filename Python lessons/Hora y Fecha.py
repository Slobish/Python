Hora y Fecha:
	import datetime
	fecha_hoy= datetime.datetime.now()
	##Nos indica la fecha y la hora
	print(fecha_hoy.day) #Dia
	print(fecha_hoy.month) #Mes
	print(fecha_hoy.minute) #Minutos
	print(fecha_hoy.weekday()) #Dia de la semana que es, empieza en lunes(0)
	fecha=fatetime.datetime(1810,5,25)
	print(fecha.weekday()) #Te indica que dia era el 25/05/1810
	dif=(fecha_hoy-fecha)
	print(dif.days) #Cuantos dias pasaron
	print(dif.microseconds) #Me indica los microsegundos

