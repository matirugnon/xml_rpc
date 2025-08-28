import socket
import threading
import xml.etree.ElementTree as ET

class Server:
    def __init__(self, addr):
        self.addr = addr
        self.methods = {}

    def add_method(self, func):
        self.methods[func.__name__] = func

    def serve(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(self.addr)
            s.listen()
            print(f"Servidor escuchando en {self.addr}...")
            while True:
                conn, _ = s.accept()
                threading.Thread(target=self.handle_client, args=(conn,)).start()

    def handle_client(self, conn):
        data = conn.recv(4096).decode()
        body = data.split("\r\n\r\n", 1)[1]
        try:
            root = ET.fromstring(body)
            method = root.find("methodName").text
            params = [p.find("value/string").text for p in root.findall(".//param")]
            if method not in self.methods:
                response = self._build_fault(2, "No existe el método invocado")
            else:
                try:
                    result = self.methods[method](*params)
                    response = self._build_response(result)
                except Exception as e:
                    response = self._build_fault(4, f"Error interno: {e}")
        except ET.ParseError:
            response = self._build_fault(1, "Error parseo de XML")

        http = "HTTP/1.1 200 OK\r\n"
        http += f"Content-Length: {len(response)}\r\n"
        http += "Content-Type: text/xml\r\n\r\n"
        http += response
        conn.sendall(http.encode())
        conn.close()

    def _build_response(self, result):
        return f"""<?xml version="1.0"?>
                    <methodResponse>
                    <params>
                        <param><value><string>{result}</string></value></param>
                    </params>
                    </methodResponse>"""

    def _build_fault(self, code, msg):
        return f"""<?xml version="1.0"?>
                    <methodResponse>
                    <fault>
                        <value>
                        <struct>
                            <member><name>faultCode</name><value><int>{code}</int></value></member>
                            <member><name>faultString</name><value><string>{msg}</string></value></member>
                        </struct>
                        </value>
                    </fault>
                    </methodResponse>"""
