import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("127.0.0.1", 5000))
print("Esperando mensaje...")

datos, direccion = s.recvfrom(1024)
print("Llegó:", datos.decode())