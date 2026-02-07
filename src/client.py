import socket
from typing import Any, List
from xmlrpc_redes import construir_llamado_xml, parsear_respuesta_xml, construir_llamado_http, parsear_respuesta_http

class Client:
    def __init__(self, address: str, port: int, timeout: float):
        self.addr = address
        self.port = port
        self.timeout = timeout

    def __getattr__(self, method_name: str):
        def _remote_call(*args):
            return self._invoke(method_name, list(args))
        return _remote_call

    def _invoke(self, method: str, params: List[Any]) -> Any:
        # Construir XML-RPC
        body = construir_llamado_xml(method, params)
        # Construir llamado HTTP
        http = construir_llamado_http(f"{self.addr}:{self.port}", body)
        # Abrir socket y enviar
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(self.timeout)
            s.connect((self.addr, self.port))
            s.sendall(http)
            # Recibir respuesta completa
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
        # Parsear HTTP y XML-RPC
        _, encabezados, cuerpo = parsear_respuesta_http(data)
        cuerpo_xml = cuerpo.decode()
        ok, res = parsear_respuesta_xml(cuerpo_xml)
        if not ok:
            num_err = res.get("faultCode", 5)
            mensaje_err = res.get("faultString", "Error desconocido")
            raise RuntimeError(f"Error RPC {num_err}: {mensaje_err}")
        return res

def connect(address: str, port: int, timeout: float = 20.0) -> Client:
    return Client(address, port, timeout)
