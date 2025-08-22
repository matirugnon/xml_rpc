import socket
from .protoloHTTP import build_http_request, read_http_response
from .xmlrpc_codec import dumps, loads
from .server import XMLRPCError, FAULT_PARSE_XML, FAULT_OTHER

class Client:

    def __init__(self, host: str, port: int, path: str = "/RPC2", timeout: float = 5.0):
        self.host = host
        self.port = port
        self.path = path
        self.timeout = timeout

    def __getattr__(self, name: str):
        """Intercepta llamadas dinámicas como client.metodo(...)"""
        def call(*args):
            return self._call(name, args)
        return call

    def _call(self, method: str, params: tuple):
        # Serializar a XML-RPC
        try:
            body = dumps(method, params).encode("utf-8")
        except Exception as e:
            raise XMLRPCError(FAULT_PARSE_XML, f"Error serializando XML: {e}")

        # Crear request HTTP
        request = build_http_request(self.host, self.path, body)

        # Enviar por socket
        with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
            sock.sendall(request)
            status, headers, response_body = read_http_response(sock)

        if status != 200:
            raise XMLRPCError(FAULT_OTHER, f"HTTP status {status}")

        # Parsear respuesta XML-RPC
        try:
            return loads(response_body.decode("utf-8"))
        except Exception as e:
            raise XMLRPCError(FAULT_PARSE_XML, f"Error parseando XML: {e}")

