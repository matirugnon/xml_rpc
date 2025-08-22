import socket
import threading
from .http import read_http_request, build_http_response
from .xmlrpc_codec import dumps_response, dumps_fault, loads_call

class XMLRPCError(Exception):
    def __init__(self, code, message):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message

FAULT_PARSE_XML = 1
FAULT_NO_METHOD = 2
FAULT_BAD_PARAMS = 3
FAULT_INTERNAL = 4
FAULT_OTHER = 5


class Server:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._methods = {}

    def add_method(self, func):
        """Registra un procedimiento remoto."""
        self._methods[func.__name__] = func

    def serve(self):
        """Bucle principal del servidor (bloqueante)."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(5)
            print(f"Servidor XML-RPC escuchando en {self.host}:{self.port} ...")

            while True:
                conn, addr = s.accept()
                threading.Thread(target=self._handle_client, args=(conn, addr), daemon=True).start()

    def _handle_client(self, conn: socket.socket, addr):
        with conn:
            try:
                method, path, headers, body = read_http_request(conn)

                if method != "POST" or path != "/RPC2":
                    resp = build_http_response(404, b"")
                    conn.sendall(resp)
                    return

                # Parsear XML-RPC request
                try:
                    proc_name, params = loads_call(body.decode("utf-8"))
                except Exception as e:
                    fault = dumps_fault(FAULT_PARSE_XML, f"Error parseando XML: {e}").encode("utf-8")
                    conn.sendall(build_http_response(200, fault))
                    return

                # Buscar procedimiento
                func = self._methods.get(proc_name)
                if not func:
                    fault = dumps_fault(FAULT_NO_METHOD, "Método no existe").encode("utf-8")
                    conn.sendall(build_http_response(200, fault))
                    return

                # Ejecutar procedimiento
                try:
                    result = func(*params)
                except TypeError as e:
                    fault = dumps_fault(FAULT_BAD_PARAMS, f"Parámetros inválidos: {e}").encode("utf-8")
                    conn.sendall(build_http_response(200, fault))
                    return
                except Exception as e:
                    fault = dumps_fault(FAULT_INTERNAL, f"Error interno: {e}").encode("utf-8")
                    conn.sendall(build_http_response(200, fault))
                    return

                # OK → devolver resultado
                response = dumps_response(result).encode("utf-8")
                conn.sendall(build_http_response(200, response))

            except Exception as e:
                fault = dumps_fault(FAULT_INTERNAL, f"Fallo general: {e}").encode("utf-8")
                conn.sendall(build_http_response(500, fault))

