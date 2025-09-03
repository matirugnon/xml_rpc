"""
server.py
---------
Servidor XML-RPC minimalista sobre sockets.
API:
    server = Server(('0.0.0.0', 8080))
    server.add_method(func)  # func.__name__ será el nombre remoto
    server.serve()  # bloqueante
"""
from __future__ import annotations
import socket
import threading
from typing import Callable, Dict, Tuple, Any
import xml.etree.ElementTree as ET

from xmlrpc_redes import (
    leer_llamado_http, construir_respuesta_http,
    leer_llamado_xml, construir_respuesta_xml, construir_error_xml
)

ERROR_PARSEO_XML = 1
ERROR_NO_EXISTE_METODO = 2
ERROR_EN_PARAMS = 3
ERROR_INTERNO = 4
OTRO_ERROR = 5

class Server:
    def __init__(self, address: Tuple[str, int]):
        self.address = address
        self.methods: Dict[str, Callable[..., Any]] = {}
        self.sock = None

    def add_method(self, func: Callable[..., Any]) -> None:
        """Registra un procedimiento remoto. El nombre es func.__name__"""
        self.methods[func.__name__] = func

    def serve(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(self.address)
            s.listen()
            self.sock = s
            print(f"[xmlrpc_redes] Server escuchando en {self.address[0]}:{self.address[1]}")
            while True:
                conn, peer = s.accept()
                th = threading.Thread(target=self._handle_client, args=(conn, peer), daemon=True)
                th.start()

    # --------------------- Internals ---------------------

    def _handle_client(self, conn: socket.socket, peer):
        try:
            data = b""
            while b"\r\n\r\n" not in data:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk
            if not data:
                conn.close()
                return

            llamado, encabezados, body = leer_llamado_http(data)
            if not llamado:
                self.error(conn, OTRO_ERROR, "Solicitud HTTP inválida")
                return

            # Validar método
            if not llamado.startswith("POST "):
                self.error(conn, OTRO_ERROR, "Solo se acepta HTTP POST")
                return

            # Completar cuerpo según Content-Length si falta
            content_length = int(encabezados.get("content-length"))
            if content_length is None:
                self.error(conn, OTRO_ERROR, "Error en los encabezados HTTP")

            while len(body) < content_length:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                body += chunk

            xml_text = body.decode()

            # Parsear XML-RPC
            try:
                method, params = leer_llamado_xml(xml_text)
            except ET.ParseError:
                self.error(conn, ERROR_PARSEO_XML, "Error parseo de XML")
                return
            except Exception as e:
                self.error(conn, OTRO_ERROR, f"Solicitud XML-RPC inválida: {e}")
                return

            # Buscar método y ejecutar
            func = self.methods.get(method)
            if func is None:
                self.error(conn, ERROR_NO_EXISTE_METODO, "No existe el método invocado")
                return

            try:
                result = func(*params)
            except TypeError as e:
                self.error(conn, ERROR_EN_PARAMS, f"Parámetros inválidos: {e}")
                return
            except Exception as e:
                self.error(conn, ERROR_INTERNO, f"Error interno en la ejecución: {e}")
                return

            # Construir respuesta OK
            resp_xml = construir_respuesta_xml(result)
            conn.sendall(construir_respuesta_http(resp_xml))
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def error(self, conn: socket.socket, code: int, msg: str):
        resp_xml = construir_error_xml(code, msg)
        conn.sendall(construir_respuesta_http(resp_xml))
