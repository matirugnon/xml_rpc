import threading
import time

from server import Server
from client import connect

# ----------------------- Servidor A -----------------------
def suma(a, b):
    return int(a) + int(b)

def resta(a, b):
    return int(a) - int(b)

def concat(a, b):
    return str(a) + str(b)

def start_server_a():
    s = Server(("127.0.0.1", 8080))
    s.add_method(suma)
    s.add_method(resta)
    s.add_method(concat)
    s.serve()

# ----------------------- Servidor B -----------------------
def power(base, exp):
    return float(base) ** float(exp)

def join_with(sep, items):
    # espera lista y separador
    if not isinstance(items, list):
        raise TypeError("items debe ser lista")
    return str(sep).join(map(str, items))

def to_upper(s, times):
    return (str(s).upper()) * int(times)

def start_server_b():
    s = Server(("127.0.0.1", 8081))
    s.add_method(power)
    s.add_method(join_with)
    s.add_method(to_upper)
    s.serve()

def main():
    # Arrancar servidores en threads
    th_a = threading.Thread(target=start_server_a, daemon=True)
    th_b = threading.Thread(target=start_server_b, daemon=True)
    th_a.start(); th_b.start()

    time.sleep(0.5)  # pequeña espera para que arranquen

    # Cliente A
    conn_a = connect("127.0.0.1", 8080)
    print("A.suma(7,5)    =>", conn_a.suma(7, 5))
    print("A.resta(7,5)   =>", conn_a.resta(7, 5))
    print("A.concat('hi','!') =>", conn_a.concat("hi", "!"))

    # Cliente B
    conn_b = connect("127.0.0.1", 8081)
    print("B.power(2, 8)       =>", conn_b.power(2, 8))
    print("B.join_with('-', [1,2,3]) =>", conn_b.join_with("-", [1,2,3]))
    print("B.to_upper('ok', 3)  =>", conn_b.to_upper("ok", 3))

    # Casos de error
    try:
        print("A.noexiste(1,2) =>", conn_a.noexiste(1,2))
    except Exception as e:
        print("Esperado error noexiste:", e)

    try:
        # join_with espera (sep, items:list) y forzamos error
        print("B.join_with('-', 123) =>", conn_b.join_with("-", 123))
    except Exception as e:
        print("Esperado error bad params:", e)

if __name__ == "__main__":
    main()
