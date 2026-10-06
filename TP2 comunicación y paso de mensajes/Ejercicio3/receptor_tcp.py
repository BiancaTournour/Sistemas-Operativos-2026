import socket

IP_SERVIDOR = "0.0.0.0"
PUERTO = 5005

# SOCK_STREAM indica que usamos TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((IP_SERVIDOR, PUERTO))

# listen() habilita al servidor para aceptar conexiones (1 es el máximo de clientes en espera)
sock.listen(1)
print(f"Servidor TCP esperando conexión en el puerto {PUERTO}...")

# accept() bloquea el programa hasta que un cliente se conecta
conexion, direccion = sock.accept()
print(f"¡Conexión TCP establecida con {direccion}!")

while True:
    datos = conexion.recv(1024)
    if not datos:
        break # Si no llegan datos, el cliente cerró la conexión
        
    mensaje = datos.decode('utf-8')
    print(f"Mensaje recibido: {mensaje}")
    
conexion.close()
sock.close()