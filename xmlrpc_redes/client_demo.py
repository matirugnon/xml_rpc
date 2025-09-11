# para generar pruebas concurrentes


from __future__ import annotations
import sys
from client import connect

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
        result = conn.slow_method(8)
        print(f"[Cliente {client_id}] Finalizó: {result}", flush=True)

    except Exception as e:
        print(f"[Cliente {client_id}] Error: {e}")

if __name__ == "__main__":
    main()