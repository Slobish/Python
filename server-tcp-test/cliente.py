#!/usr/bin/env python3
import socket, time

def c_msg(text):
    print("[CLIENTE] " + text)
    
cliente = socket.socket()

ip = input("SERVER IP: ")
port = int(input("SERVER PORT: "))
password = input("CLAVE DEL SERVER: ")
print("\n")

cliente.connect((ip, port))

cliente.settimeout(3)

while True:
    c_msg("Enviando mensaje...")
    cliente.send(password.encode())
    c_msg("Esperando respuesta...")
    try:
        data = cliente.recv(128).decode()
    except BrokenPipeError:
        c_msg("Sin respuesta, cerrando cliente.")
        cliente.close()
        break        
    except socket.timeout:
        c_msg("Sin respuesta, cerrando cliente.")
        cliente.close()
        break
    else:
        if data == 'Chau':
            c_msg("Clave incorrecta!")
            cliente.close()
            break
        else:
            c_msg(data + '\n')
    time.sleep(5)
