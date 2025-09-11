# myClient.py
from __future__ import annotations
import threading
import time
from client import connect
from lorem_text import lorem  
import socket


def test_basic_calls(conn):
    print("\n--- Llamadas Válidas Básicas ---")
    print("A.suma(7,5)    =>", conn.suma(7, 5))
    print("A.resta(7,5)   =>", conn.resta(7, 5))
    print("A.concat('hi','!') =>", conn.concat("hi", "!"))

def test_new_methods(conn):
    print("\n--- Nuevos Métodos ---")
    print("A.get_current_year() =>", conn.get_current_year())
    print("A.repeat_string(3, 'OK') =>", conn.repeat_string(3, "OK"))
    
    # Generar texto grande (~20.000 palabras)
    print("Generando texto grande (~20.000 palabras)...")
    large_text = lorem.words(20000)  # Genera 20.000 palabras
    print(f"Texto generado: {len(large_text)} caracteres")
    echoed = conn.echo_large_text(large_text)
    print(f"Echo recibido: {len(echoed)} caracteres (OK si coincide)")
    
    print("A.slow_method(12) => Iniciando (esperar ~12s)...")
    result = conn.slow_method(12)
    print("Resultado:", result)
    
    print("A.divide(10, 2) =>", conn.divide(10, 2))
    try:
        print("A.divide(10, 0) =>", conn.divide(10, 0))
    except Exception as e:
        print("✅ Error esperado (división por cero):", e)

#pruebas de errores 

def test_error_cases(conn):
    print("\n--- Casos de Error ---")
    try:
        print("A.noexiste(1,2) =>", conn.noexiste(1,2))
    except Exception as e:
        print("✅ Error esperado (método no existe):", e)

    try:
        print("A.suma() =>", conn.suma())  # Menos parámetros
    except Exception as e:
        print("✅ Error esperado (faltan parámetros):", e)

    try:
        print("A.suma(1,2,3) =>", conn.suma(1,2,3))  # Más parámetros
    except Exception as e:
        print("✅ Error esperado (demasiados parámetros):", e)

    try:
        print("A.suma('a', 'b') =>", conn.suma('a', 'b'))  # Parámetros inválidos
    except Exception as e:
        print("✅ Error esperado (parámetros inválidos):", e)

def test_concurrency():
    print("\n--- Prueba de Concurrencia (5 clientes simultáneos) ---")
    def client_thread(id):
        try:
            conn = connect("150.150.0.2", 8000)
            print(f"[Cliente {id}] Llamando a slow_method...")
            result = conn.slow_method(5)  # 5 segundos para no demorar demasiado
            print(f"[Cliente {id}] Resultado: {result}")
        except Exception as e:
            print(f"[Cliente {id}] Error: {e}")

    threads = []
    for i in range(5):
        th = threading.Thread(target=client_thread, args=(i+1,), daemon=True)
        threads.append(th)
        th.start()

    # Esperar a que terminen
    for th in threads:
        th.join()
    print("✅ Todos los clientes concurrentes terminaron.")



#agrego prueba de concurrencia con operaciones simultaneas

def test_concurrency_mixed_operations():
    """
    Prueba de concurrencia mejorada: 5 clientes simultáneos haciendo operaciones distintas.
    2 de ellos provocan errores intencionales (división por cero y parámetros inválidos).
    """
    print("\n--- PRUEBA DE CONCURRENCIA MEJORADA (5 clientes, operaciones mixtas + errores) ---")
    
    def client_thread(id, operation, args):
        try:
            conn = connect("150.150.0.2", 8000)
            print(f"[Cliente {id}] Ejecutando: {operation}{args}...")
            method = getattr(conn, operation)
            result = method(*args)
            print(f"[Cliente {id}] ✅ Resultado: {result}")
        except Exception as e:
            print(f"[Cliente {id}] ❌ Error capturado: {e}")

    # Definimos las operaciones para cada cliente
    test_cases = [
        (1, "suma", (10, 20)),               # Cliente 1 éxito
        (2, "divide", (100, 0)),             # Cliente 2 ERROR
        (3, "repeat_string", (3, "Jorge!")),   # Cliente 3 éxito
        (4, "suma", ("a", "b")),             # Cliente 4 ERROR (parámetros inválidos)
        (5, "concat", ("Tiago", " Ger"))    # Cliente 5 éxito
    ]

    threads = []
    for client_id, operation, args in test_cases:
        th = threading.Thread(
            target=client_thread,
            args=(client_id, operation, args),
            daemon=True
        )
        threads.append(th)
        th.start()

    # Esperar a que todos terminen
    for th in threads:
        th.join()
    
    print("\n✅ PRUEBA DE CONCURRENCIA MEJORADA: Todos los clientes han terminado.")


#pruebas en el server  2

def test_server2_methods(conn_b):
    """Pruebas específicas para server2 (100.100.0.2) - Simple y efectiva."""
    print("\n--- PRUEBAS PARA SERVIDOR B (100.100.0.2) ---")

    # 1. Llamadas Válidas
    print("\n1. Llamadas Válidas:")
    print("  B.power(2, 8)       =>", conn_b.power(2, 8))          # → 256.0
    print("  B.join_with('-', [1,2,3]) =>", conn_b.join_with("-", [1,2,3]))  # → "1-2-3"
    print("  B.to_upper('rpc', 3)  =>", conn_b.to_upper("rpc", 3))   # → "RPCRPCRPC"

    # 2. Casos de Error (Parámetros Incorrectos)
    print("\n2. Casos de Error (Parámetros Incorrectos):")
    try:
        print("  B.join_with('-', 'NO_es_lista') =>", conn_b.join_with("-", "NO_es_lista"))
    except Exception as e:
        print("  ✅ Error esperado (join_with):", e)

    try:
        print("  B.to_upper('hola', 'NO_es_int') =>", conn_b.to_upper("hola", "NO_es_int"))
    except Exception as e:
        print("  ✅ Error esperado (to_upper):", e)

    try:
        print("  B.power('a', 'b') =>", conn_b.power('a', 'b'))
    except Exception as e:
        print("  ✅ Error esperado (power):", e)






def test_invalid_xml():
    print("\n--- Prueba de XML Inválido ---")

    # XML intencionalmente mal formado 
    invalid_xml = """<?xml version="1.0"?>
    <MatiasRugnon>
    <methodName>suma</methodName>
    <params>
        <param><value><int>5</int></value></param>
        <param><value><int>7</int></value></param> 
    </params>
    </methodCall>
    """

    # Armamos el request HTTP a mano
    host = "150.150.0.2:8000"
    data_bytes = invalid_xml.encode()
    request = (
        "POST / HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "User-Agent: xmlrpc_redes/1.0\r\n"
        "Content-Type: text/xml\r\n"
        f"Content-Length: {len(data_bytes)}\r\n"
        "Connection: close\r\n\r\n"
    ).encode() + data_bytes

    # Mandamos por socket crudo
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("150.150.0.2", 8000))
        s.sendall(request)
        response = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk

    # Mostramos la respuesta del servidor
    print(response.decode(errors="ignore"))
    print("✅ Devuelve un <fault> con faultCode=1 (Error parseo de XML).")


def test_invalid_http_get():
    print("\n--- Prueba de HTTP Inválido ---")

    # Request armado con GET en lugar de POST
    bad_http = (
        "GET / HTTP/1.1\r\n"
        "Host: 150.150.0.2:8000\r\n"
        "User-Agent: xmlrpc_redes/1.0\r\n"
        "Content-Type: text/xml\r\n"
        "Content-Length: 0\r\n"
        "Connection: close\r\n\r\n"
    ).encode()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("150.150.0.2", 8000))
        s.sendall(bad_http)
        response = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk

    print(response.decode(errors="ignore"))
    print("✅ El servidor debería devolver un <fault> con faultCode=5 (Solicitud HTTP inválida o método no permitido).")


def test_invalid_http_bad_headers():
    print("\n--- Prueba de HTTP Inválido ---")

    valid_xml = """<?xml version="1.0"?>
        <methodCall>
        <methodName>suma</methodName>
        <params>
            <param><value><int>5</int></value></param>
            <param><value><int>7</int></value></param> 
        </params>
        </methodCall>
        """
    data_bytes = valid_xml.encode()

    # Request armado con POST pero un encabezado mal y otro faltante
    # XML valido
    bad_http = (
        "POST / HTTP/1.1\r\n"
        "Host: 150.150.0.2:8000\r\n"
        "User-Agent: xmlrpc_redes/1.0\r\n"
        "Content-HOLA: text/xml\r\n"
        "Connection: close\r\n\r\n"
    ).encode() + data_bytes

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("150.150.0.2", 8000))
        s.sendall(bad_http)
        response = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk

    print(response.decode(errors="ignore"))
    print("✅ El servidor debería devolver un <fault> con faultCode=5 (Solicitud HTTP inválida o método no permitido).")






def main():
    conn_a = connect("150.150.0.2", 8000)
    conn_b = connect("100.100.0.2", 8000)  
    

    # Pruebas básicas
    test_basic_calls(conn_a)
    
    # Nuevos métodos para defensa
    test_new_methods(conn_a)

    # Casos de error
    test_error_cases(conn_a)

    #test server 2
    test_server2_methods(conn_b)

    # Prueba de concurrencia, se hacen en el server 1
    test_concurrency()

    # prueba de concurrencia con operaciones mixtas y errores, se hacen en el server 1
    test_concurrency_mixed_operations()

    #prueba para error de parseo xml
    test_invalid_xml()

    #prueba 1 para error de HTTP (se manda con GET)
    test_invalid_http_get()

    #prueba 2 para error de HTTP (head corrupto)
    test_invalid_http_bad_headers()
    
    print("\n✅ ¡Todas las pruebas completadas exitosamente!")

    print("\n--- CLIENTE EN ESPERA (Presiona Ctrl+C para salir) ---")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Cliente cerrado por el usuario.")


if __name__ == "__main__":
    main()