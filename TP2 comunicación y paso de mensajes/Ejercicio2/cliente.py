import socket

MODO = 4   # tiene que ser igual al del servidor

# Socket para RECIBIR (puerto 5000)
rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rx.bind(("127.0.0.1", 5000))

# Socket para ENVIAR (puerto 5001)
tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tx.bind(("127.0.0.1", 5001))

DESTINO = ("127.0.0.1", 6000)   # donde escucha el servidor

def enviar(texto):
    tx.sendto(texto.encode(), DESTINO)

def recibir():
    datos, _ = rx.recvfrom(1024)
    return datos.decode()

# 1) Mando la petición
enviar("PETICION: hola servidor")
print("Envié la petición")

# 2) Solo en 4 vías: espero el ACK de la petición
if MODO == 4:
    print("Recibí:", recibir())

# 3) Recibo la respuesta (en todos los modos)
print("Recibí:", recibir())

# 4) En 3 y 4 vías: confirmo que recibí la respuesta
if MODO in (3, 4):
    enviar("ACK de la respuesta")
    print("Envié ACK final")