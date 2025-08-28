"""
client.py
---------
Cliente de xmlrpc_redes. Exposición de API:
    conn = connect(address, port)
    result = conn.metodo(arg1, arg2, ...)
"""
from __future__ import annotations
import socket
from typing import Any, List
from xmlrpc_redes import build_method_call_xml, parse_method_response_xml, build_http_post, parse_http_response

DEFAULT_PATH = "/RPC2"

class _Connection:
    def __init__(self, address: str, port: int, path: str = DEFAULT_PATH, timeout: float = 10.0):
        self.addr = address
        self.port = port
        self.path = path
        self.timeout = timeout

    def __getattr__(self, method_name: str):
        def _remote_call(*args):
            return self._invoke(method_name, list(args))
        return _remote_call

    def _invoke(self, method: str, params: List[Any]) -> Any:
        # 1) Construir XML-RPC
        body = build_method_call_xml(method, params)
        # 2) Encapsular en HTTP POST
        http = build_http_post(f"{self.addr}:{self.port}", self.path, body)
        # 3) Abrir socket y enviar
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(self.timeout)
            s.connect((self.addr, self.port))
            s.sendall(http)
            # 4) Recibir respuesta completa
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
        # 5) Parsear HTTP y XML-RPC
        status_line, headers, body_bytes = parse_http_response(data)
        # Nota: ignoramos status_code!=200 y dejamos al servidor devolver fault en XML
        xml_text = body_bytes.decode("utf-8", errors="replace")
        ok, value = parse_method_response_xml(xml_text)
        if not ok:
            code = value.get("faultCode", -1)
            msg = value.get("faultString", "Error desconocido")
            raise RuntimeError(f"RPC Fault {code}: {msg}")
        return value

def connect(address: str, port: int) -> _Connection:
    """Punto de entrada público pedido por el enunciado."""
    return _Connection(address, port)
