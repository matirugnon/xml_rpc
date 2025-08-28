import socket
import xml.etree.ElementTree as ET

class Client:
    def __init__(self, address, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((address, port))

    def __getattr__(self, method_name):
        def remote_call(*args):
            # 1) Construir XML
            request = self._build_xml_request(method_name, args)
            # 2) Enviar solicitud HTTP
            self.sock.sendall(request.encode())
            # 3) Recibir respuesta
            response = self._recv_response()
            # 4) Parsear XML y devolver resultado
            return self._parse_xml_response(response)
        return remote_call

    def _build_xml_request(self, method_name, args):
        xml = '<?xml version="1.0"?><methodCall>'
        xml += f"<methodName>{method_name}</methodName><params>"
        for a in args:
            xml += f"<param><value><string>{a}</string></value></param>"
        xml += "</params></methodCall>"
        # Encapsular en HTTP POST
        http = "POST /RPC2 HTTP/1.1\r\n"
        http += f"Content-Length: {len(xml)}\r\n"
        http += "Content-Type: text/xml\r\n\r\n"
        http += xml
        return http

    def _recv_response(self):
        data = b""
        while True:
            chunk = self.sock.recv(4096)
            if not chunk: break
            data += chunk
            if b"</methodResponse>" in data or b"</fault>" in data:
                break
        return data.decode()

    def _parse_xml_response(self, response):
        body = response.split("\r\n\r\n", 1)[1]
        root = ET.fromstring(body)
        if root.find("fault") is not None:
            fault = root.find("fault/value/struct")
            code = fault.find("member/value/int").text
            msg = fault.find("member/value/string").text
            raise Exception(f"RPC Error {code}: {msg}")
        return root.find(".//param/value/string").text
