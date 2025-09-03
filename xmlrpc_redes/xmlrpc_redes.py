from __future__ import annotations
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List, Tuple


# -----------------------------
# XML
# -----------------------------

def serializacion(valor: Any) -> ET.Element:
    v = ET.Element("value")
    if isinstance(valor, bool):
        e = ET.SubElement(v, "boolean")
        e.text = "1" if valor else "0"
    elif isinstance(valor, int):
        e = ET.SubElement(v, "int")
        e.text = str(valor)
    elif isinstance(valor, float):
        e = ET.SubElement(v, "double")
        e.text = repr(valor)
    elif isinstance(valor, str):
        e = ET.SubElement(v, "string")
        e.text = valor
    elif isinstance(valor, (list, tuple)):
        arr = ET.SubElement(v, "array")
        data = ET.SubElement(arr, "data")
        for item in valor:
            data.append(serializacion(item))
    elif isinstance(valor, dict):
        st = ET.SubElement(v, "struct")
        for k, val in valor.items():
            m = ET.SubElement(st, "member")
            nom = ET.SubElement(m, "name")
            nom.text = str(k)
            m.append(serializacion(val))
    elif isinstance(valor, datetime):
        e = ET.SubElement(v, "dateTime.iso8601")
        e.text = valor.strftime("%Y%m%dT%H:%M:%S")
    else:
        e = ET.SubElement(v, "string")
        e.text = str(valor)
    return v

def deserializacion(elem: ET.Element) -> Any:
    if elem is None:
        return None
    if len(elem) == 0:
        return elem.text or ""
    child = elem[0]
    tag = child.tag
    valor = child.text or ""
    if tag in ("int", "i4"):
        try:
            return int(valor.strip())
        except:
            return 0
    if tag == "boolean":
        return valor.strip() in ("1", "true", "True")
    if tag == "double":
        try:
            return float(valor.strip())
        except:
            return 0.0
    if tag == "string":
        return valor
    if tag == "dateTime.iso8601":
        try:
            return datetime.strptime(valor.strip(), "%Y%m%dT%H:%M:%S")
        except:
            return valor
    if tag == "array":
        data = child.find("data")
        items = []
        if data is not None:
            for val in data.findall("value"):
                items.append(deserializacion(val))
        return items
    if tag == "struct":
        obj = {}
        for member in child.findall("member"):
            nom_el = member.find("name")
            val_el = member.find("value")
            nom = nom_el.text if nom_el is not None else ""
            obj[nom] = deserializacion(val_el)
        return obj
    return valor

def construir_llamado_xml(method: str, params: List[Any]) -> str:
    elem = ET.Element("methodCall")
    mnom = ET.SubElement(elem, "methodName")
    mnom.text = method
    params_el = ET.SubElement(elem, "params")
    for p in params:
        param = ET.SubElement(params_el, "param")
        param.append(serializacion(p))
    return '<?xml version="1.0"?>' + ET.tostring(elem, encoding="unicode")

def leer_llamado_xml(xml: str) -> Tuple[str, List[Any]]:
    elem = ET.fromstring(xml)
    if elem.tag != "methodCall":
        raise ValueError("XML-RPC: método inválido")
    mnom_el = elem.find("methodName")
    if mnom_el is None or not (mnom_el.text or "").strip():
        raise ValueError("XML-RPC: método inválido")
    method = mnom_el.text.strip()
    params: List[Any] = []
    for p in elem.findall("./params/param"):
        val = p.find("value")
        params.append(deserializacion(val))
    return method, params

def construir_respuesta_xml(res: Any) -> str:
    elem = ET.Element("methodResponse")
    params = ET.SubElement(elem, "params")
    param = ET.SubElement(params, "param")
    param.append(serializacion(res))
    return '<?xml version="1.0"?>' + ET.tostring(elem, encoding="unicode")

def construir_error_xml(code: int, message: str) -> str:
    root = ET.Element("methodResponse")
    fault = ET.SubElement(root, "fault")
    value = ET.SubElement(fault, "value")
    struct = ET.SubElement(value, "struct")

    m1 = ET.SubElement(struct, "member")
    n1 = ET.SubElement(m1, "name"); n1.text = "faultCode"
    m1.append(serializacion(int(code)))

    m2 = ET.SubElement(struct, "member")
    n2 = ET.SubElement(m2, "name"); n2.text = "faultString"
    m2.append(serializacion(str(message)))

    return '<?xml version="1.0"?>' + ET.tostring(root, encoding="unicode")

def leer_respuesta_xml(xml_text: str) -> Tuple[bool, Any]:
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
                fault_obj[key] = deserializacion(val_el)
        return False, fault_obj
    # ok
    val_el = root.find("./params/param/value")
    return True, deserializacion(val_el)

# -----------------------------
# HTTP
# -----------------------------

def construir_llamado_http(host: str, data: str) -> bytes:
    data_bytes = data.encode()
    encabezados = [
        "POST / HTTP/1.1",
        f"Host: {host}",
        "User-Agent: xmlrpc_redes/1.0",
        "Content-Type: text/xml",
        f"Content-Length: {len(data_bytes)}",
        "Connection: close",
        "\r\n"
    ]
    encabezado = "\r\n".join(encabezados).encode()
    return encabezado + data_bytes

def leer_llamado_http(resp: bytes) -> Tuple[str, Dict[str, str], bytes]:
    """
    Parsea una solicitud HTTP cruda y devuelve (request_line, headers_dict, body).
    Si el cuerpo no está completamente recibido (según Content-Length), lo esperado
    es que la capa superior continúe leyendo desde el socket.
    """
    sep = b"\r\n\r\n"
    if sep not in resp:
        return "", {}, b""
    encabezado, body = resp.split(sep, 1)
    lineas = encabezado.decode().split("\r\n")
    llamado = lineas[0]
    encabezados = {}
    for ln in lineas[1:]:
        if not ln.strip():
            continue
        if ":" in ln:
            k, v = ln.split(":", 1)
            encabezados[k.strip().lower()] = v.strip()
    return llamado, encabezados, body

def construir_respuesta_http(data: str) -> bytes:
    data_bytes = data.encode()
    encabezados = [
        "HTTP/1.1 200 OK",
        "Content-Type: text/xml",
        f"Content-Length: {len(data_bytes)}",
        "Connection: close",
        "\r\n"
    ]
    encabezado = "\r\n".join(encabezados).encode()
    return encabezado + data_bytes

def leer_respuesta_http(resp: bytes) -> Tuple[str, Dict[str, str], bytes]:
    """Igual que leer_llamado_http pero para respuestas HTTP."""
    return leer_llamado_http(resp)
