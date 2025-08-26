import socket
from typing import Tuple, Dict

CRLF = "\r\n"
HEADER_BODY_SEP = b"\r\n\r\n"


# -----------------
# Construcción HTTP
# -----------------
def build_http_request(host: str, path: str, body: bytes, content_type: str = "text/xml") -> bytes:
    headers = [
        f"POST {path} HTTP/1.1",
        f"Host: {host}",
        f"Content-Type: {content_type}",
        f"Content-Length: {len(body)}",
        "Connection: close",
    ]
    head = (CRLF.join(headers) + CRLF * 2).encode("ascii")
    return head + body


def build_http_response(status_code: int, body: bytes, content_type: str = "text/xml") -> bytes:
    reason = {
        0: "OK",
        1: "Error parseo de XML",
        2: "No existe el metodo invocado",
        3: "Error en parametros del metodo invocado",
        4: "Error interno en la ejecucion del metodo",
        5: "Otros errores",
    }.get(status_code, "OK")

    headers = [
        f"HTTP/1.1 {status_code} {reason}",
        f"Content-Type: {content_type}",
        f"Content-Length: {len(body)}",
        "Connection: close",
    ]
    head = (CRLF.join(headers) + CRLF * 2).encode("ascii")
    return head + body


# -----------------
# Lectura auxiliar
# -----------------
def _recv_until(sock: socket.socket, delim: bytes, max_bytes: int = 2 * 1024 * 1024):
    """Lee hasta encontrar `delim` (por ejemplo, fin de headers)."""
    buf = bytearray()
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf.extend(chunk)
        if len(buf) > max_bytes:
            raise ValueError("HTTP headers too large")
        idx = buf.find(delim)
        if idx != -1:
            return bytes(buf[:idx]), bytes(buf[idx + len(delim):])
    return bytes(buf), b""


def _recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ValueError("Socket closed before receiving expected bytes")
        buf.extend(chunk)
    return bytes(buf)


# -----------------
# Parseo de HTTP
# -----------------
def read_http_request(sock: socket.socket) -> Tuple[str, str, Dict[str, str], bytes]:
    """Devuelve: method, path, headers, body."""
    head, rest = _recv_until(sock, HEADER_BODY_SEP)
    lines = head.decode("iso-8859-1").split(CRLF)
    method, path, _ = lines[0].split(" ", 2)

    headers: Dict[str, str] = {}
    for line in lines[1:]:
        if line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()

    content_length = int(headers.get("content-length", "0"))
    if len(rest) >= content_length:
        body = rest[:content_length]
    else:
        body = rest + _recv_exact(sock, content_length - len(rest))
    return method, path, headers, body


def read_http_response(sock: socket.socket) -> Tuple[int, Dict[str, str], bytes]:
    """Devuelve: status_code, headers, body."""
    head, rest = _recv_until(sock, HEADER_BODY_SEP)
    lines = head.decode("iso-8859-1").split(CRLF)
    _proto, status_code, *_ = lines[0].split(" ")

    headers: Dict[str, str] = {}
    for line in lines[1:]:
        if line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()

    content_length = int(headers.get("content-length", "0"))
    if len(rest) >= content_length:
        body = rest[:content_length]
    else:
        body = rest + _recv_exact(sock, content_length - len(rest))

    return int(status_code), headers, body

