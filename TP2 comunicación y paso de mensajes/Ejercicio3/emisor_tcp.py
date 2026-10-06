import socket

IP_DESTINO = "127.0.0.1" 
PUERTO_DESTINO = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect() establece el "handshake" o enlace inicial con el servidor
sock.connect((IP_DESTINO, PUERTO_DESTINO))
print("¡Conectado exitosamente al servidor TCP!")

while True:
    mensaje = input("Escribe un mensaje TCP (o 'salir'): ")
    if mensaje.lower() == 'salir':
        break
        
    # sendall() asegura que se transmita todo el bloque de datos por la conexión
    sock.sendall(mensaje.encode('utf-8'))

sock.close()