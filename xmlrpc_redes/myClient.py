# myClient.py
from __future__ import annotations
import threading
import time
from client import connect
from lorem_text import lorem  

def test_basic_calls(conn):
    print("\n--- Llamadas Válidas Básicas ---")
    print("A.suma(7,5)    =>", conn.suma(7, 5))
    print("A.resta(7,5)   =>", conn.resta(7, 5))
    print("A.concat('hi','!') =>", conn.concat("hi", "!"))

def test_new_methods(conn):
    print("\n--- Nuevos Métodos para Defensa ---")
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
        (1, "suma", (10, 20)),               # Cliente 1: suma -> éxito
        (2, "divide", (100, 0)),             # Cliente 2: división por cero -> ERROR
        (3, "repeat_string", (3, "Jorge!")),   # Cliente 3: repeat_string -> éxito
        (4, "suma", ("a", "b")),             # Cliente 4: suma con strings -> ERROR (parámetros inválidos)
        (5, "concat", ("Tiago", " Ger"))    # Cliente 5: concat -> éxito
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







def main():
    conn_a = connect("150.150.0.2", 8000)
    
    # Pruebas básicas
    test_basic_calls(conn_a)
    
    # Nuevos métodos para defensa
    test_new_methods(conn_a)
    
    # Casos de error
    test_error_cases(conn_a)
    
    # Prueba de concurrencia
    test_concurrency()

    # prueba de concurrencia con operaciones mixtas y errores
    test_concurrency_mixed_operations()
    
    print("\n✅ ¡Todas las pruebas completadas exitosamente!")

if __name__ == "__main__":
    main()