import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto("Hola!".encode(), ("127.0.0.1", 5000))
print("Mensaje enviado")