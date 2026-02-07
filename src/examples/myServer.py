# myServer.py
from __future__ import annotations
import time
from server import Server


def suma(a, b):
    return int(a) + int(b)

def resta(a, b):
    return int(a) - int(b)

def concat(a, b):
    return str(a) + str(b)


#metodos extra para pruebas segun los requerimientos de la defensa


def get_current_year():
    """Método sin parámetros que retorna un único valor. retorna el año actual."""
    from datetime import datetime
    return datetime.now().year

def repeat_string(n: int, s: str):
    """Método con parámetros entero y string, retorna un único valor."""
    return s * int(n)

def echo_large_text(text: str):
    """Método echo que devuelve el mismo string (para probar con 20k palabras)."""
    return text

def slow_method(secs: int = 12):
    """Método que tarda más de 10 segundos en responder."""
    time.sleep(secs)
    return f"Esperé {secs} segundos"

def divide(a: int, b: int):
    """Método que realiza división. Probar división por cero."""
    if b == 0:
        raise ValueError("División por cero")
    return int(a) // int(b)



if __name__ == "__main__":
    # ¡IP y puerto CORRECTOS para server1!
    server = Server(("150.150.0.2", 8000))
    server.add_method(suma)
    server.add_method(resta)
    server.add_method(concat)

    server.add_method(get_current_year)
    server.add_method(repeat_string)
    server.add_method(echo_large_text)
    server.add_method(slow_method)
    server.add_method(divide)

    print("Servidor A escuchando en 150.150.0.2:8000")
    print("Métodos disponibles: suma \n resta \n divide \n concat \n get_current_year \n repeat_string \n echo_large_text \n slow_method")
    server.serve()
