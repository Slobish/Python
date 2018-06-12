import socket
 
def keyboardInput():
    a=raw_input()
    return a

TCP_IP = '10.10.0.78'
TCP_PORT = 2000
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"
while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(keyboardInput())
    data = s.recv(BUFFER_SIZE)
    print "received data:", data    

