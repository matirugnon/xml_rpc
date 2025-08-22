import socket
import threading
from xmlrpc_redes.protocol import parse_request_xml, build_response_xml, build_fault_xml

class Server:
    def __init__(self, address):
        self.host, self.port = address
        self.methods = {}

    def add_method(self, func):
        self.methods[func.__name__] = func

    def serve(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((self.host, self.port))
            server_sock.listen(5)
            print(f"[+] Servidor escuchando en {self.host}:{self.port}")

            while True:
                client_sock, client_addr = server_sock.accept()
                threading.Thread(target=self.handle_client, args=(client_sock,)).start()

    def handle_client(self, client_sock):
        try:
            request = b""
            while True:
                data = client_sock.recv(4096)
                if not data:
                    break
                request += data

            # Extraer el cuerpo XML del mensaje HTTP
            request_str = request.decode()
            body = request_str.split("\r\n\r\n", 1)[1]

            try:
                method_name, params = parse_request_xml(body)
                if method_name not in self.methods:
                    response = build_fault_xml(2, "No existe el método invocado")
                else:
                    try:
                        result = self.methods[method_name](*params)
                        response = build_response_xml(result)
                    except TypeError:
                        response = build_fault_xml(3, "Error en parámetros del método invocado")
                    except Exception as e:
                        response = build_fault_xml(4, f"Error interno en el método: {str(e)}")
            except Exception as e:
                response = build_fault_xml(1, f"Error de parseo XML: {str(e)}")

            http_response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/xml\r\n"
                f"Content-Length: {len(response)}\r\n"
                "Connection: close\r\n"
                "\r\n"
                f"{response}"
            )
            client_sock.sendall(http_response.encode())

        finally:
            client_sock.close()

