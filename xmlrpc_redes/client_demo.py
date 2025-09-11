# para generar pruebas concurrentes

"""

Script de cliente para probar el servidor con múltiples clientes concurrentes.
En este script, se conecta al servidor y realiza una llamada al método `slow_method`
que tarda 10 segundos en responder. Esto es útil para probar la capacidad del
servidor para manejar múltiples conexiones simultáneas.

uso:
  Ejecutar múltiples instancias del cliente en segundo plano:

    client python3.8 ./client_demo.py 1 &
    client python3.8 ./client_demo.py 2 &
    client python3.8 ./client_demo.py 3 &

    se puede dejar la ultima en primer plano para ver la salida de las 3 juntas

"""

from __future__ import annotations
import sys
from client import connect
import time

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 client_demo.py <id>")
        return

    client_id = sys.argv[1]
    server_ip = "150.150.0.2"
    port = 8000

    try:
        conn = connect(server_ip, port)
        print(f"[Cliente {client_id}] Conectado al servidor", flush=True)


        print("⌛ Comenzando Slow Method...⌛ ")
        # Hacer una llamada larga
        result = conn.slow_method(10)
        print(f"[Cliente {client_id}] Finalizó: {result} ✅", flush=True)


    except Exception as e:
        print(f"[Cliente {client_id}] Error: {e}")

    


if __name__ == "__main__":
    main()