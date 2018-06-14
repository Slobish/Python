#!/usr/bin/env python3
import socket, datetime

def sv_msg(text):
    print("[SERVER] - " + text)

def tiempo_on():
    global start
    actual = datetime.datetime.now()
    dif = actual - start
    horas = (dif.seconds + 1) // 3600
    minutos = ((dif.seconds + 1) % 3600 ) // 60
    seg = (((dif.seconds + 1) % 3600) % 60)
    return "{}h {}m {}s ONLINE".format(str(horas), str(minutos), str(seg))

start = datetime.datetime.now()

print("Servidor de prueba")

sv_msg("Configurar puerto")

host = socket.gethostname()
ip = socket.gethostbyname(host)
port = int(input("Puerto: "))
sv_msg("Configurar clave")
password = input("Clave: ")

sv_msg("IP: " + ip)
sv_msg("PORT: " + str(port))

server = socket.socket()

server.bind((host, port))

server.listen(5)

while True:
    server.settimeout(None)
    try:
        sv_msg("Esperando conexion")
        c, reg = server.accept()
    except KeyboardInterrupt:
        sv_msg("Desconectando servidor...")
        server.close()
        break
    else:
        server.settimeout(5)
        sv_msg("Conexion entrante - " + str(reg))
        while True:
            sv_msg("Esperando mensaje...")
            try:
                data = c.recv(512).decode()
            except:
                sv_msg("Sin mensaje, desconectando cliente.")
                c.close()
                break
            else:
                sv_msg("Respondiendo mensaje...\n")
                if data == password:
                    c.send(tiempo_on().encode())
                else:
                    c.send("Chau".encode())
                    sv_msg("Desconectando cliente, clave erronea")
                    c.close()
                    break
