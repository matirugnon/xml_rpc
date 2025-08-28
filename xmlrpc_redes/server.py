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
    parse_http_request, http_ok_response,
    parse_method_call_xml, build_method_response_xml, build_fault_xml
)

FAULT_PARSE_XML = 1
FAULT_NO_METHOD = 2
FAULT_BAD_PARAMS = 3
FAULT_INTERNAL = 4
FAULT_OTHER = 5

class Server:
    def __init__(self, addr: Tuple[str, int], path: str = "/RPC2", backlog: int = 20, timeout: float = 30.0):
        self.addr = addr
        self.path = path
        self.backlog = backlog
        self.timeout = timeout
        self.methods: Dict[str, Callable[..., Any]] = {}
        self._sock = None

    def add_method(self, func: Callable[..., Any]) -> None:
        """Registra un procedimiento remoto. El nombre es func.__name__"""
        self.methods[func.__name__] = func

    def serve(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(self.addr)
            s.listen(self.backlog)
            self._sock = s
            print(f"[xmlrpc_redes] Server escuchando en {self.addr[0]}:{self.addr[1]} (path={self.path})")
            while True:
                conn, peer = s.accept()
                conn.settimeout(self.timeout)
                th = threading.Thread(target=self._handle_client, args=(conn, peer), daemon=True)
                th.start()

    # --------------------- Internals ---------------------

    def _handle_client(self, conn: socket.socket, peer):
        try:
            data = b""
            # leer encabezados
            while b"\r\n\r\n" not in data:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk
            if not data:
                conn.close()
                return

            request_line, headers, body = parse_http_request(data)
            if not request_line:
                self._send_fault(conn, FAULT_OTHER, "Solicitud HTTP inválida")
                return

            # Validar método y path
            if not request_line.startswith("POST "):
                self._send_fault(conn, FAULT_OTHER, "Solo se acepta HTTP POST")
                return
            # path
            try:
                path = request_line.split(" ")[1]
            except Exception:
                self._send_fault(conn, FAULT_OTHER, "Request-Line inválida")
                return
            if path != self.path:
                self._send_fault(conn, FAULT_OTHER, f"Path inválido (esperado {self.path})")
                return

            # Completar cuerpo según Content-Length si falta
            content_length = int(headers.get("content-length", "0"))
            while len(body) < content_length:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                body += chunk

            xml_text = body.decode("utf-8", errors="replace")

            # Parsear XML-RPC
            try:
                method, params = parse_method_call_xml(xml_text)
            except ET.ParseError:
                self._send_fault(conn, FAULT_PARSE_XML, "Error parseo de XML")
                return
            except Exception as e:
                self._send_fault(conn, FAULT_OTHER, f"Solicitud XML-RPC inválida: {e}")
                return

            # Buscar método y ejecutar
            func = self.methods.get(method)
            if func is None:
                self._send_fault(conn, FAULT_NO_METHOD, "No existe el método invocado")
                return

            try:
                result = func(*params)
            except TypeError as e:
                self._send_fault(conn, FAULT_BAD_PARAMS, f"Parámetros inválidos: {e}")
                return
            except Exception as e:
                self._send_fault(conn, FAULT_INTERNAL, f"Error interno en la ejecución: {e}")
                return

            # Construir respuesta OK
            resp_xml = build_method_response_xml(result)
            conn.sendall(http_ok_response(resp_xml))
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def _send_fault(self, conn: socket.socket, code: int, msg: str):
        resp_xml = build_fault_xml(code, msg)
        conn.sendall(http_ok_response(resp_xml))
