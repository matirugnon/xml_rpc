from .client import Client
from .server import Server

"""
Serialización / Deserialización XML-RPC básica.
Soporta: int, float, str, bool, None, listas, diccionarios.
"""

import xml.etree.ElementTree as ET


# --------------------
# Serialización valores
# --------------------
def _serialize_value(value):
    v = ET.Element("value")

    if isinstance(value, bool):
        t = ET.SubElement(v, "boolean")
        t.text = "1" if value else "0"
    elif isinstance(value, int):
        t = ET.SubElement(v, "int")
        t.text = str(value)
    elif isinstance(value, float):
        t = ET.SubElement(v, "double")
        t.text = str(value)
    elif isinstance(value, str):
        t = ET.SubElement(v, "string")
        t.text = value
    elif value is None:
        ET.SubElement(v, "nil")  # extensión opcional
    elif isinstance(value, (list, tuple)):
        arr = ET.SubElement(v, "array")
        data = ET.SubElement(arr, "data")
        for item in value:
            data.append(_serialize_value(item))
    elif isinstance(value, dict):
        st = ET.SubElement(v, "struct")
        for k, v_ in value.items():
            m = ET.SubElement(st, "member")
            n = ET.SubElement(m, "name")
            n.text = str(k)
            m.append(_serialize_value(v_))
    else:
        raise TypeError(f"No se puede serializar tipo {type(value)}")
    return v


# --------------------
# Deserialización valores
# --------------------
def _deserialize_value(value_elem):
    if len(value_elem) == 0:  # string implícito
        return value_elem.text or ""

    child = value_elem[0]
    tag = child.tag

    if tag in ("int", "i4"):
        return int(child.text)
    elif tag == "double":
        return float(child.text)
    elif tag == "boolean":
        return child.text.strip() == "1"
    elif tag == "string":
        return child.text or ""
    elif tag == "nil":
        return None
    elif tag == "array":
        return [_deserialize_value(v) for v in child.find("data").findall("value")]
    elif tag == "struct":
        result = {}
        for member in child.findall("member"):
            name = member.find("name").text
            val = _deserialize_value(member.find("value"))
            result[name] = val
        return result
    else:
        raise ValueError(f"Tipo XML-RPC desconocido: {tag}")


# --------------------
# Requests & Responses
# --------------------
def dumps(method: str, params: tuple) -> str:
    method_call = ET.Element("methodCall")
    name = ET.SubElement(method_call, "methodName")
    name.text = method

    params_elem = ET.SubElement(method_call, "params")
    for p in params:
        param = ET.SubElement(params_elem, "param")
        param.append(_serialize_value(p))

    return ET.tostring(method_call, encoding="utf-8", method="xml").decode("utf-8")


def loads_call(xml: str):
    root = ET.fromstring(xml)
    method = root.find("methodName").text
    params = []
    for p in root.findall("./params/param"):
        params.append(_deserialize_value(p.find("value")))
    return method, params


def dumps_response(value) -> str:
    method_resp = ET.Element("methodResponse")
    params = ET.SubElement(method_resp, "params")
    param = ET.SubElement(params, "param")
    param.append(_serialize_value(value))
    return ET.tostring(method_resp, encoding="utf-8", method="xml").decode("utf-8")


def loads(xml: str):
    root = ET.fromstring(xml)
    fault = root.find("fault")
    if fault is not None:
        val = _deserialize_value(fault.find("value"))
        raise Exception(f"Fault {val}")
    params = root.findall("./params/param")
    if not params:
        return None
    return _deserialize_value(params[0].find("value"))


def dumps_fault(code: int, message: str) -> str:
    method_resp = ET.Element("methodResponse")
    fault = ET.SubElement(method_resp, "fault")
    struct_val = {"faultCode": code, "faultString": message}
    fault.append(_serialize_value(struct_val))
    return ET.tostring(method_resp, encoding="utf-8", method="xml").decode("utf-8")
