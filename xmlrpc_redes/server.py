import socket
import threading
from typing import Callable, Dict, Tuple, Any
import xml.etree.ElementTree as ET

from xmlrpc_redes import (
    parsear_llamado_http, construir_respuesta_http,
    parsear_llamado_xml, construir_respuesta_xml, construir_error_xml
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
                th = threading.Thread(target=self.atender_cliente, args=(conn, peer), daemon=True)
                th.start()

    def atender_cliente(self, conn: socket.socket, peer):
        try:
            data = b""
            while b"\r\n\r\n" not in data:
                bytes_recv = conn.recv(4096)
                if not bytes_recv:
                    break
                data += bytes_recv
            if not data:
                conn.close()
                return

            llamado, encabezados, cuerpo = parsear_llamado_http(data)
            if not llamado:
                self.error(conn, OTRO_ERROR, "Solicitud HTTP inválida")
                return

            # Validar método
            if not llamado.startswith("POST "):
                self.error(conn, OTRO_ERROR, "Solo se acepta HTTP POST")
                return

            user_agent = encabezados.get("user-agent")
            host = encabezados.get("host")
            content_type = encabezados.get("content-type")
            content_length = encabezados.get("content-length")

            # Cheque que existan los encabezados necesarios
            if (user_agent is None) or (host is None) or (content_type is None) or (content_length is None):
                self.error(conn, OTRO_ERROR, "Error en los encabezados HTTP")
                return
            if content_type != "text/xml":
                self.error(conn, OTRO_ERROR, "Error en los encabezados HTTP")
                return

            content_length = int(content_length)
            # Completar cuerpo según Content-Length si falta
            while len(cuerpo) < content_length:
                bytes_recv = conn.recv(4096)
                if not bytes_recv:
                    break
                cuerpo += bytes_recv

            cuerpo_xml = cuerpo.decode()

            # Parsear XML-RPC
            try:
                method, params = parsear_llamado_xml(cuerpo_xml)
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
                res = func(*params)
            except TypeError as e:
                self.error(conn, ERROR_EN_PARAMS, f"Error en parámetros del método invocado: {e}")
                return
            except Exception as e:
                self.error(conn, ERROR_INTERNO, f"Error interno en la ejecución del método: {e}")
                return

            # Construir respuesta
            resp_xml = construir_respuesta_xml(res)
            conn.sendall(construir_respuesta_http(resp_xml))
        finally:
            conn.close()

    def error(self, conn: socket.socket, num_err: int, mensaje_err: str):
        resp_xml = construir_error_xml(num_err, mensaje_err)
        conn.sendall(construir_respuesta_http(resp_xml))
