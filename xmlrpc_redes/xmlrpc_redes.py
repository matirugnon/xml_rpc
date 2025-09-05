from __future__ import annotations
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List, Tuple

# IMPORTANTE Documentar todas las funciones en el archivo de documentacion
# explicar que hace cada funcion y dar ejemplos de uso

#explicar tambien las decisiones que se tomaron en el diseño de las funciones 
# explicar que se uso ElementTree para manejar XML y explicar su funcionamiento basico
# explicar que se uso sockets para manejar la comunicacion en red
# explicar que se uso typing para manejar tipos de datos y mejorar la legibilidad del codigo

#explicar que se siguio el estandar XML-RPC y HTTP/1.1 para la comunicacion
#explicar porque se uso POST en lugar de GET
#explicar que se manejo errores comunes y se definieron codigos de error
#explicar que se uso excepciones para manejar errores en el cliente y servidor
#explicar que se uso threading para manejar multiples conexiones en el servidor

#explicar que decisiones se tomaron para serializar y deserializar tipos de datos
#explicar que decisiones se tomaron para construir y parsear llamadas y respuestas XML-RPC
#explicar que decisiones se tomaron para construir y parsear llamadas y respuestas HTTP
#explicar que decisiones se tomaron para manejar el socket y la comunicacion en red
#explicar que decisiones se tomaron para manejar el timeout y errores de red
#explicar que decisiones se tomaron para manejar la concurrencia en el servidor (HILOS)
#explicar como se diseño la validacion y la integridad de los datos, como se impide funciones invalidas o parametros incorrectos
#explicar que decisiones se tomaron a nivel de protocolo XML-RPC y HTTP
#explicar que decisiones se tomaron a nivel de arquitectura del cliente y servidor




"""Funciones para serializar y deserializar tipos de datos
aca van todas las funciones que sirven para manejar XML y HTTP

funciones:

XML

-----------------------------------------------------------------------

1. serializacion(valor: Any) -> ET.Element
2. deserializacion(elem: ET.Element) -> Any

sirven para convertir entre tipos de Python y XML-RPC, por ejemplo: 

para serializar un int, se crea un elemento <value><int>...</int></value>
para deserializar, se recibe un elemento <value> y se devuelve el int

---------------------------------------------------------------------

3. construir_llamado_xml(method: str, params: List[Any]) -> str


sirve para construir y parsear llamadas XML-RPC completas, por ejemplo:
construir_llamado_xml("suma", [5,7]) devuelve el string XML:

<?xml version="1.0"?>
<methodCall>
  <methodName>suma</methodName>
    <params>
        <param><value><int>5</int></value></param>
        <param><value><int>7</int></value></param>
    </params>
</methodCall>

esta funcion es usada por el cliente para enviar llamadas al servidor,

4. parsear_llamado_xml(xml: str) -> Tuple[str, List[Any]]

esta es usada por el servidor para recibir llamadas del cliente,
devuelve el nombre del método y la lista de parámetros
por ejemplo, parsear_llamado_xml(...) del XML anterior devuelve ("suma", [5, 7])

---------------------------------------------------------------

5. construir_respuesta_xml(res: Any) -> str

esta sirve para construir respuestas XML-RPC exitosas, por ejemplo:
construir_respuesta_xml(12) devuelve el string XML:
<?xml version="1.0"?>
<methodResponse>
    <params>
        <param><value><int>12</int></value></param>
    </params>
</methodResponse>
esta es usada por el servidor para responder al cliente


6. construir_error_xml(num_err: int, mensaje_err: str) -> str

esta se usa por el servidor para responder errores al cliente
por ejemplo, construir_error_xml(4, "No existe el método invocado") devuelve:   
<?xml version="1.0"?>
<methodResponse>
    <fault>
        <value>
            <struct>
                <member>   
                    <name>faultCode</name>
                    <value><int>4</int></value>
                </member>
                <member>
                    <name>faultString</name>
                    <value><string>No existe el método invocado</string></value>
                </member>
            </struct>
        </value>
    </fault>
</methodResponse>


7. parsear_respuesta_xml(xml_text: str) -> Tuple[bool, Any]

esta es usada por el cliente para recibir respuestas del servidor
devuelve una tupla (ok, res) donde ok es True si la respuesta es exitosa
y res es el valor devuelto o el diccionario de error
se recibe el string pasado por el servidor y se parsea a XML
y se devuelve el resultado deserializado como tupla (ok, res)
por ejemplo, parsear_respuesta_xml(...) del XML anterior devuelve (False, {"faultCode": 4, "faultString": "No existe el método invocado"})

Http

son usadas tanto por el cliente como por el servidor para manejar la capa HTTP
estas funciones construyen y parsean llamadas y respuestas HTTP/1.1

1. construir_llamado_http(host: str, data: str) -> bytes

esta se usa tanto por el cliente como por el servidor para construir llamadas y respuestas HTTP
por ejemplo, construir_llamado_http("localhost:8000", "<xml>...</xml>") devuelve:


b"POST / HTTP/1.1\r\nHost: localhost:8000\r\n
User-Agent: xmlrpc_redes/1.0\r\nContent-Type: text/xml\r\n
Content-Length: 15\r\n
Connection: close\r\n\r\n<xml>...</xml>"


2. parsear_llamado_http(resp: bytes) -> Tuple[str, Dict[str, str], bytes]

esta se usa tanto por el cliente como por el servidor para parsear llamadas y respuestas HTTP
devuelve una tupla (llamado, encabezados, cuerpo) 

esta funcion separa las 3 partes que nos interesan de una llamada o respuesta HTTP:
- la primera linea (llamado)
- los encabezados (encabezados)
- el cuerpo (cuerpo)


3. construir_respuesta_http(data: str) -> bytes

tambien se usa tanto por el cliente como por el servidor para construir respuestas HTTP
por ejemplo, construir_respuesta_http("<xml>...</xml>") devuelve:
b"HTTP/1.1 200 OK\r\nContent-Type: text/xml\r\n
Content-Length: 15\r\n
Connection: close\r\n\r\n
<xml>...</xml>"


4. parsear_respuesta_http(resp: bytes) -> Tuple[str, Dict[str, str], bytes]

mas de lo mismo, esta se usa tanto por el cliente como por el servidor para parsear respuestas HTTP
devuelve una tupla (llamado, encabezados, cuerpo) igual que parsear_llamado_http



"""

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

def parsear_llamado_xml(xml: str) -> Tuple[str, List[Any]]:
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

def construir_error_xml(num_err: int, mensaje_err: str) -> str:
    elem = ET.Element("methodResponse")
    fault = ET.SubElement(elem, "fault")
    value = ET.SubElement(fault, "value")
    struct = ET.SubElement(value, "struct")

    m1 = ET.SubElement(struct, "member")
    n1 = ET.SubElement(m1, "name"); n1.text = "faultCode"
    m1.append(serializacion(int(num_err)))

    m2 = ET.SubElement(struct, "member")
    n2 = ET.SubElement(m2, "name"); n2.text = "faultString"
    m2.append(serializacion(str(mensaje_err)))

    return '<?xml version="1.0"?>' + ET.tostring(elem, encoding="unicode")

def parsear_respuesta_xml(xml_text: str) -> Tuple[bool, Any]:
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

def parsear_llamado_http(resp: bytes) -> Tuple[str, Dict[str, str], bytes]:
    sep = b"\r\n\r\n"
    if sep not in resp:
        return "", {}, b""
    encabezado, cuerpo = resp.split(sep, 1)
    lineas = encabezado.decode().split("\r\n")
    llamado = lineas[0]
    encabezados = {}
    for ln in lineas[1:]:
        if not ln.strip():
            continue
        if ":" in ln:
            k, v = ln.split(":", 1)
            encabezados[k.strip().lower()] = v.strip()
    return llamado, encabezados, cuerpo

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

def parsear_respuesta_http(resp: bytes) -> Tuple[str, Dict[str, str], bytes]:
    """Igual que parsear_llamado_http pero para respuestas HTTP."""
    return parsear_llamado_http(resp)
