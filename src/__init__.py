"""
XML-RPC sobre Sockets TCP/IP

Implementación completa de XML-RPC usando sockets Python sin librerías HTTP externas.
Incluye cliente y servidor con soporte para marshalling/unmarshalling automático,
concurrencia mediante threading, y manejo robusto de errores.

Ejemplo de uso:

Servidor:
    from server import Server
    
    def suma(a, b):
        return int(a) + int(b)
    
    servidor = Server(("127.0.0.1", 8000))
    servidor.add_method(suma)
    servidor.serve()

Cliente:
    from client import connect
    
    conn = connect("127.0.0.1", 8000)
    resultado = conn.suma(5, 3)
    print(resultado)  # 8
"""

__version__ = "1.0.0"
__author__ = "Grupo 05 - Redes de Computadoras UdelaR"

from .client import connect, Client
from .server import Server

__all__ = ['connect', 'Client', 'Server']
