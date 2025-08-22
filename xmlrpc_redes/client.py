import socket
from xmlrpc_redes.protocol import build_request_xml, parse_response_xml

class RemoteMethod:
    def __init__(self, sock, method_name):
        self.sock = sock
        self.method_name = method_name

    def __call__(self, *args):
        xml = build_request_xml(self.method_name, args)
        request = (
            "POST /RPC2 HTTP/1.1\r\n"
            f"Host: localhost\r\n"
            "Content-Type: text/xml\r\n"
            f"Content-Length: {len(xml)}\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{xml}"
        )
        self.sock.sendall(request.encode())

        response = b""
        while True:
            chunk = self.sock.recv(4096)
            if not chunk:
                break
            response += chunk

        return parse_response_xml(response.decode())

class Connection:
    def __init__(self, sock):
        self.sock = sock

    def __getattr__(self, name):
        return RemoteMethod(self.sock, name)

def connect(address, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((address, int(port)))
    return Connection(sock)

