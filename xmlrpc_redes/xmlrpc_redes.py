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
