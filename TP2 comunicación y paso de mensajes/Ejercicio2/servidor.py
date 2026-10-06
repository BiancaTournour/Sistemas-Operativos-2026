import socket

MODO = 4   # cambiá a 3 o 4 (tiene que ser igual en el cliente)

# Socket para RECIBIR (puerto 6000)
rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rx.bind(("127.0.0.1", 6000))

# Socket para ENVIAR (puerto 6001)
tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tx.bind(("127.0.0.1", 6001))

DESTINO = ("127.0.0.1", 5000)   # donde escucha el cliente

def enviar(texto):
    tx.sendto(texto.encode(), DESTINO)

def recibir():
    datos, _ = rx.recvfrom(1024)
    return datos.decode()

print(f"Servidor en modo {MODO} vías. Esperando petición...")

# 1) Llega la petición
print("Recibí:", recibir())

# 2) Solo en 4 vías: ACK de la petición
if MODO == 4:
    enviar("ACK de la petición")
    print("Envié ACK de la petición")

# 3) Respuesta (en todos los modos)
enviar("RESPUESTA: todo ok")
print("Envié la respuesta")

# 4) En 3 y 4 vías: espero el ACK final del cliente
if MODO in (3, 4):
    print("Recibí:", recibir())