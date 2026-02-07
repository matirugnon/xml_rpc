from __future__ import annotations
from server import Server
import time

def power(base, exp):
    return float(base) ** float(exp)

def join_with(sep, items):
    # espera lista y separador
    if not isinstance(items, list):
        raise TypeError("items debe ser lista")
    return str(sep).join(map(str, items))

def to_upper(s, times):
    return (str(s).upper()) * int(times)

if __name__ == "__main__":
    server = Server(("100.100.0.2", 8000))
    server.add_method(power)
    server.add_method(join_with)
    server.add_method(to_upper)
    print("Servidor B escuchando en 100.100.0.2:8000")
    server.serve()
