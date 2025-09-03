from __future__ import annotations
import socket
from typing import Any, List
from xmlrpc_redes import construir_llamado_xml, leer_respuesta_xml, construir_llamado_http, leer_respuesta_http

class Client:
    def __init__(self, address: str, port: int, timeout: float = 10.0):
        self.addr = address
        self.port = port
        self.timeout = timeout

    def __getattr__(self, method_name: str):
        def _remote_call(*args):
            return self._invoke(method_name, list(args))
        return _remote_call

    def _invoke(self, method: str, params: List[Any]) -> Any:
        # 1) Construir XML-RPC
        body = construir_llamado_xml(method, params)
        # 2) Encapsular en HTTP POST
        http = construir_llamado_http(f"{self.addr}:{self.port}", body)
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
        status_line, headers, body_bytes = leer_respuesta_http(data)
        # Nota: ignoramos status_code!=200 y dejamos al servidor devolver fault en XML
        xml_text = body_bytes.decode("utf-8", errors="replace")
        ok, res = leer_respuesta_xml(xml_text)
        if not ok:
            code = res.get("faultCode", -1)
            msg = res.get("faultString", "Error desconocido")
            raise RuntimeError(f"RPC Fault {code}: {msg}")
        return res

def connect(address: str, port: int) -> Client:
    return Client(address, port)
