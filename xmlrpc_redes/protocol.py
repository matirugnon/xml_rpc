import xml.etree.ElementTree as ET

def build_request_xml(method_name, params):
    root = ET.Element("methodCall")
    method_elem = ET.SubElement(root, "methodName")
    method_elem.text = method_name

    params_elem = ET.SubElement(root, "params")
    for param in params:
        param_elem = ET.SubElement(params_elem, "param")
        value_elem = ET.SubElement(param_elem, "value")
        
        if isinstance(param, int):
            int_elem = ET.SubElement(value_elem, "int")
            int_elem.text = str(param)
        elif isinstance(param, str):
            str_elem = ET.SubElement(value_elem, "string")
            str_elem.text = param
        else:
            raise ValueError("Tipo de parámetro no soportado")

    return ET.tostring(root, encoding="utf-8", method="xml").decode()

def parse_response_xml(xml_string):
    try:
        root = ET.fromstring(xml_string)
        if root.find("fault") is not None:
            fault_struct = root.find(".//struct")
            fault_code = int(fault_struct.find("./member[name='faultCode']/value/int").text)
            fault_string = fault_struct.find("./member[name='faultString']/value/string").text
            raise Exception(f"Error XML-RPC {fault_code}: {fault_string}")

        value_elem = root.find(".//param/value")
        return extract_value(value_elem)
    except ET.ParseError:
        raise Exception("Error de parseo XML (FaultCode 1)")

def extract_value(value_elem):
    if value_elem.find("int") is not None:
        return int(value_elem.find("int").text)
    elif value_elem.find("string") is not None:
        return value_elem.find("string").text
    else:
        raise Exception("Tipo de dato no soportado")


def parse_request_xml(xml_string):
    try:
        root = ET.fromstring(xml_string)
        method_name = root.find("methodName").text
        params = []

        for param_elem in root.findall(".//param"):
            value_elem = param_elem.find("value")
            params.append(extract_value(value_elem))

        return method_name, params

    except ET.ParseError:
        raise Exception("Error parseando XML")

def build_response_xml(result):
    root = ET.Element("methodResponse")
    params_elem = ET.SubElement(root, "params")
    param_elem = ET.SubElement(params_elem, "param")
    value_elem = ET.SubElement(param_elem, "value")

    if isinstance(result, int):
        int_elem = ET.SubElement(value_elem, "int")
        int_elem.text = str(result)
    elif isinstance(result, str):
        str_elem = ET.SubElement(value_elem, "string")
        str_elem.text = result
    else:
        raise Exception("Tipo de retorno no soportado")

    return ET.tostring(root, encoding="utf-8").decode()

def build_fault_xml(code, message):
    root = ET.Element("methodResponse")
    fault_elem = ET.SubElement(root, "fault")
    value_elem = ET.SubElement(fault_elem, "value")
    struct_elem = ET.SubElement(value_elem, "struct")

    code_member = ET.SubElement(struct_elem, "member")
    code_name = ET.SubElement(code_member, "name")
    code_name.text = "faultCode"
    code_value = ET.SubElement(code_member, "value")
    code_int = ET.SubElement(code_value, "int")
    code_int.text = str(code)

    msg_member = ET.SubElement(struct_elem, "member")
    msg_name = ET.SubElement(msg_member, "name")
    msg_name.text = "faultString"
    msg_value = ET.SubElement(msg_member, "value")
    msg_str = ET.SubElement(msg_value, "string")
    msg_str.text = message

    return ET.tostring(root, encoding="utf-8").decode()

