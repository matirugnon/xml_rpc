"""
xmlrpc_redes.py
----------------
Funciones utilitarias para serializar/deserializar XML-RPC y helpers de HTTP.

Restricciones: sin uso de librerías HTTP de alto nivel. Solo sockets + xml.etree.
"""
from __future__ import annotations
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List, Tuple

# -----------------------------
# XML-RPC serialization helpers
# -----------------------------

def _value_to_xml(value: Any) -> ET.Element:
    """Convierte un valor de Python a <value> XML-RPC (tipos soportados: int, bool, float, str, list, dict)."""
    v = ET.Element("value")
    if isinstance(value, bool):
        e = ET.SubElement(v, "boolean")
        e.text = "1" if value else "0"
    elif isinstance(value, int):
        e = ET.SubElement(v, "int")
        e.text = str(value)
    elif isinstance(value, float):
        e = ET.SubElement(v, "double")
        e.text = repr(value)
    elif isinstance(value, str):
        e = ET.SubElement(v, "string")
        e.text = value
    elif isinstance(value, (list, tuple)):
        arr = ET.SubElement(v, "array")
        data = ET.SubElement(arr, "data")
        for item in value:
            data.append(_value_to_xml(item))
    elif isinstance(value, dict):
        st = ET.SubElement(v, "struct")
        for k, val in value.items():
            m = ET.SubElement(st, "member")
            name = ET.SubElement(m, "name")
            name.text = str(k)
            m.append(_value_to_xml(val))
    elif isinstance(value, datetime):
        e = ET.SubElement(v, "dateTime.iso8601")
        e.text = value.strftime("%Y%m%dT%H:%M:%S")
    else:
        # fallback a string
        e = ET.SubElement(v, "string")
        e.text = str(value)
    return v

def _xml_to_value(node: ET.Element) -> Any:
    """Convierte un nodo <value> XML-RPC a objeto Python."""
    if node is None:
        return None
    # El propio <value> contiene un hijo que define el tipo
    if len(node) == 0:
        # value directo con texto
        return node.text or ""
    child = node[0]
    tag = child.tag
    text = child.text or ""
    if tag in ("int", "i4"):
        try:
            return int(text.strip())
        except:
            return 0
    if tag == "boolean":
        return text.strip() in ("1", "true", "True")
    if tag == "double":
        try:
            return float(text.strip())
        except:
            return 0.0
    if tag == "string":
        return text
    if tag == "dateTime.iso8601":
        try:
            return datetime.strptime(text.strip(), "%Y%m%dT%H:%M:%S")
        except:
            return text
    if tag == "array":
        data = child.find("data")
        items = []
        if data is not None:
            for val in data.findall("value"):
                items.append(_xml_to_value(val))
        return items
    if tag == "struct":
        obj = {}
        for member in child.findall("member"):
            name_el = member.find("name")
            val_el = member.find("value")
            name = name_el.text if name_el is not None else ""
            obj[name] = _xml_to_value(val_el)
        return obj
    # fallback
    return text

def build_method_call_xml(method: str, params: List[Any]) -> str:
    root = ET.Element("methodCall")
    mname = ET.SubElement(root, "methodName")
    mname.text = method
    params_el = ET.SubElement(root, "params")
    for p in params:
        param = ET.SubElement(params_el, "param")
        param.append(_value_to_xml(p))
    return '<?xml version="1.0"?>' + ET.tostring(root, encoding="unicode")

def parse_method_call_xml(xml_text: str) -> Tuple[str, List[Any]]:
    root = ET.fromstring(xml_text)
    if root.tag != "methodCall":
        raise ValueError("XML-RPC: método inválido")
    mname_el = root.find("methodName")
    if mname_el is None or not (mname_el.text or "").strip():
        raise ValueError("XML-RPC: falta methodName")
    method = mname_el.text.strip()
    params: List[Any] = []
    for p in root.findall("./params/param"):
        val = p.find("value")
        params.append(_xml_to_value(val))
    return method, params

def build_method_response_xml(result: Any) -> str:
    root = ET.Element("methodResponse")
    params = ET.SubElement(root, "params")
    param = ET.SubElement(params, "param")
    param.append(_value_to_xml(result))
    return '<?xml version="1.0"?>' + ET.tostring(root, encoding="unicode")

def build_fault_xml(code: int, message: str) -> str:
    root = ET.Element("methodResponse")
    fault = ET.SubElement(root, "fault")
    value = ET.SubElement(fault, "value")
    struct = ET.SubElement(value, "struct")

    m1 = ET.SubElement(struct, "member")
    n1 = ET.SubElement(m1, "name"); n1.text = "faultCode"
    m1.append(_value_to_xml(int(code)))

    m2 = ET.SubElement(struct, "member")
    n2 = ET.SubElement(m2, "name"); n2.text = "faultString"
    m2.append(_value_to_xml(str(message)))

    return '<?xml version="1.0"?>' + ET.tostring(root, encoding="unicode")

def parse_method_response_xml(xml_text: str) -> Tuple[bool, Any]:
    """
    Devuelve (ok, value). Si ok=False, value es dict con faultCode/faultString.
    """
    root = ET.fromstring(xml_text)
    if root.tag != "methodResponse":
        raise ValueError("XML-RPC: respuesta inválida")
    fault = root.find("fault")
    if fault is not None:
        struct = fault.find("value/struct")
        fault_obj = {}
        if struct is not None:
            for member in struct.findall("member"):
                name_el = member.find("name")
                val_el = member.find("value")
                key = name_el.text if name_el is not None else ""
                fault_obj[key] = _xml_to_value(val_el)
        return False, fault_obj
    # ok
    val_el = root.find("./params/param/value")
    return True, _xml_to_value(val_el)

# -----------------------------
# HTTP helpers (mínimos)
# -----------------------------

def build_http_post(host: str, path: str, body: str) -> bytes:
    body_bytes = body.encode("utf-8")
    headers = [
        "POST {} HTTP/1.1".format(path),
        "Host: {}".format(host),
        "User-Agent: xmlrpc_redes/1.0",
        "Content-Type: text/xml",
        "Content-Length: {}".format(len(body_bytes)),
        "Connection: close",
        "", ""
    ]
    head = "\r\n".join(headers).encode("utf-8")
    return head + body_bytes

def parse_http_request(raw: bytes) -> Tuple[str, Dict[str, str], bytes]:
    """
    Parsea una solicitud HTTP cruda y devuelve (request_line, headers_dict, body).
    Si el cuerpo no está completamente recibido (según Content-Length), lo esperado
    es que la capa superior continúe leyendo desde el socket.
    """
    sep = b"\r\n\r\n"
    if sep not in raw:
        return "", {}, b""
    head, body = raw.split(sep, 1)
    lines = head.decode("iso-8859-1").split("\r\n")
    request_line = lines[0]
    headers = {}
    for ln in lines[1:]:
        if not ln.strip():
            continue
        if ":" in ln:
            k, v = ln.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    return request_line, headers, body

def parse_http_response(raw: bytes) -> Tuple[str, Dict[str, str], bytes]:
    """Igual que parse_http_request pero para respuestas HTTP."""
    return parse_http_request(raw)

def http_ok_response(body: str) -> bytes:
    body_bytes = body.encode("utf-8")
    headers = [
        "HTTP/1.1 200 OK",
        "Content-Type: text/xml",
        "Content-Length: {}".format(len(body_bytes)),
        "Connection: close",
        "", ""
    ]
    head = "\r\n".join(headers).encode("utf-8")
    return head + body_bytes
