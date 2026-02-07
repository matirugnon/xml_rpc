# XML-RPC sobre Sockets TCP/IP

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Network Protocol](https://img.shields.io/badge/Protocol-HTTP%2FXML--RPC-orange.svg)](https://xmlrpc.com/spec.md)
[![TCP/IP](https://img.shields.io/badge/Transport-TCP%2FIP-red.svg)](https://en.wikipedia.org/wiki/Transmission_Control_Protocol)

> Implementación completa de XML-RPC desde cero usando sockets Python, sin librerías HTTP externas. Proyecto académico del curso Redes de Computadoras - Facultad de Ingeniería, UdelaR.

## Descripción

Este proyecto implementa el protocolo **XML-RPC** (Remote Procedure Call) sobre **HTTP/1.1** y **TCP/IP** utilizando exclusivamente la API de sockets POSIX de Python, sin recurrir a librerías HTTP de alto nivel. La implementación permite invocar procedimientos remotos de forma transparente, manejando automáticamente la serialización XML, comunicación HTTP y gestión de errores.

### Características

- **Servidor XML-RPC** con registro dinámico de métodos y soporte para múltiples clientes concurrentes
- **Cliente XML-RPC** con sintaxis Pythonic que permite llamar métodos remotos como `conn.metodo(args)`
- **Marshalling/Unmarshalling** automático entre tipos Python y XML-RPC
- **Concurrencia** mediante threading (modelo thread-per-connection)
- **Manejo robusto de errores** implementando los 5 códigos de fallo XML-RPC
- **Suite de pruebas** exhaustiva con casos de éxito, error y concurrencia
- **Validación en red emulada** usando Mininet con topología multi-router

---

## Arquitectura e Implementación

### Decisiones de Diseño

El diseño de la biblioteca se basó en los siguientes principios:

#### 1. **Separación de Responsabilidades**

El código está modularizado en tres componentes principales:

- **`xmlrpc_redes.py`**: Core de marshalling/unmarshalling XML-RPC y utilidades HTTP
  - Serialización/deserialización de tipos Python ↔ XML
  - Construcción y parseo de mensajes XML-RPC (`<methodCall>`, `<methodResponse>`, `<fault>`)
  - Construcción y parseo de requests/responses HTTP/1.1
  
- **`server.py`**: Implementación del servidor
  - Gestión de sockets (bind, listen, accept)
  - Threading para atender múltiples clientes concurrentes
  - Registro dinámico de métodos expuestos
  - Validación de requests HTTP y ejecución de procedimientos
  
- **`client.py`**: Implementación del cliente
  - Conexión TCP al servidor
  - Construcción de requests XML-RPC
  - Parseo de responses y manejo de faults
  - Interface Pythonic usando `__getattr__` para métodos dinámicos

#### 2. **Protocolo HTTP/1.1**

Se eligió **HTTP POST** (en lugar de GET) porque:
- XML-RPC es un protocolo RPC que modifica estado en el servidor
- El cuerpo del request contiene los parámetros serializados en XML
- Permite enviar payloads de tamaño arbitrario
- Cumple con la especificación XML-RPC estándar

**Headers HTTP implementados:**
```http
POST /RPC2 HTTP/1.1
Host: <server>:<port>
User-Agent: xmlrpc_redes/1.0
Content-Type: text/xml
Content-Length: <bytes>
Connection: close
```

Decisión: usar `Connection: close` para simplificar el manejo de sockets (una request por conexión TCP).

#### 3. **Tipos de Datos Soportados**

| Tipo Python | Tipo XML-RPC | Decisiones de Implementación |
|-------------|--------------|------------------------------|
| `int` | `<int>` o `<i4>` | Conversión directa con `int()` |
| `bool` | `<boolean>` | `True` → `1`, `False` → `0` |
| `float` | `<double>` | Conversión con `float()`, representación decimal |
| `str` | `<string>` | Codificación UTF-8, escape de caracteres XML |
| `datetime` | `<dateTime.iso8601>` | Formato ISO `YYYYMMDDTHH:MM:SS` |
| `list/tuple` | `<array>` | Serialización recursiva de elementos |
| `dict` | `<struct>` | Claves deben ser strings, valores recursivos |

**Decisión:** No se implementaron tipos `<base64>` ni `<nil>` por simplicidad, enfocándose en los tipos más comunes.

#### 4. **Manejo de Errores**

Se implementaron los **5 códigos de faultCode** del estándar:

| FaultCode | Descripción | Cuándo se genera |
|-----------|-------------|------------------|
| **1** | Error de parseo XML | XML malformado o encoding inválido |
| **2** | Método no existe | Se invoca un método no registrado |
| **3** | Error en parámetros | Número o tipo de argumentos incorrectos |
| **4** | Error interno | Excepción no controlada durante ejecución |
| **5** | Otros errores | Violación del protocolo HTTP/XML-RPC |

**Decisión:** Capturar excepciones específicas (ParseError, TypeError, ValueError) para clasificar errores correctamente.

#### 5. **Concurrencia**

**Modelo thread-per-connection:**
- Cada cliente que se conecta es atendido en un hilo dedicado
- Ventaja: simplicidad de implementación, aislamiento de fallos
- Limitación: no escala a miles de clientes (overhead de hilos)
- Alternativas consideradas: asyncio, thread pool (complejidad mayor)

**Decisión:** Threads daemon para evitar bloquear el shutdown del servidor.

#### 6. **Validación y Seguridad**

- **Validación de headers HTTP**: se verifica presencia de `Host`, `Content-Type`, `Content-Length`
- **Validación de Content-Type**: debe ser exactamente `text/xml`
- **Validación de Content-Length**: se lee exactamente la cantidad de bytes especificada
- **Validación de método HTTP**: solo se acepta POST
- **Validación de path**: solo se acepta `/RPC2` (estándar XML-RPC)

**Decisión:** Fallar rápido con faultCode apropiado ante requests inválidos.

---

## Estructura del Proyecto

```
xml_rpc/
├── LICENSE                     # Licencia MIT
├── README.md                   # Este archivo
├── .gitignore                  # Archivos ignorados por Git
├── docs/                       # Documentación del proyecto
│   ├── Grupo05.pdf            # Informe técnico del grupo
│   └── Obligatorio1-2025.pdf  # Letra del obligatorio
├── captures/                   # Capturas de tráfico de red
│   ├── server1.pcap
│   └── vhost*.pcap
├── src/                        # Código fuente
│   ├── __init__.py            # Inicialización del paquete
│   ├── xmlrpc_redes.py        # Core: marshalling/unmarshalling
│   ├── server.py              # Servidor XML-RPC
│   ├── client.py              # Cliente XML-RPC
│   └── examples/              # Ejemplos y pruebas
│       ├── test_app.py        # Suite de pruebas completa
│       ├── myServer.py        # Servidor de ejemplo
│       ├── myClient.py        # Cliente de ejemplo
│       └── myServer2.py       # Segundo servidor para pruebas
└── xmlrpc_redes/              # Código original (legacy)
```

---

## Instalación y Uso

### Requisitos

- Python 3.8 o superior
- No se requieren dependencias externas (solo módulos estándar)

### Inicio Rápido

#### 1. Ejecutar Demo Completa

```bash
cd src/examples
python test_app.py
```

Esto iniciará dos servidores (puertos 8080 y 8081) y ejecutará casos de prueba de:
- Operaciones básicas (suma, resta, concatenación)
- Manejo de errores (método inexistente, parámetros inválidos)
- Concurrencia (múltiples clientes simultáneos)

#### 2. Crear un Servidor

```python
import sys
sys.path.insert(0, '..')  # Ajustar path si es necesario

from server import Server

def suma(a, b):
    """Suma dos números"""
    return int(a) + int(b)

def saludar(nombre):
    """Saluda a una persona"""
    return f"Hola, {nombre}!"

# Crear y configurar servidor
servidor = Server(("127.0.0.1", 8000))
servidor.add_method(suma)
servidor.add_method(saludar)

print("Servidor XML-RPC escuchando en 127.0.0.1:8000")
servidor.serve()  # Bloqueante
```

#### 3. Conectar un Cliente

```python
import sys
sys.path.insert(0, '..')

from client import connect

# Conectar al servidor
conn = connect("127.0.0.1", 8000, timeout=10.0)

# Llamar métodos remotos
resultado = conn.suma(5, 3)
print(f"5 + 3 = {resultado}")  # Output: 5 + 3 = 8

mensaje = conn.saludar("Matías")
print(f"Mensaje: {mensaje}")  # Output: Mensaje: Hola, Matías!
```

---

## Flujo de Comunicación

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTE                                 │
├─────────────────────────────────────────────────────────────────┤
│  1. Construir llamado XML: <methodCall>...</methodCall>        │
│  2. Encapsular en HTTP POST con headers                        │
│  3. Abrir socket TCP al servidor                               │
│  4. Enviar request y recibir response                          │
│  5. Parsear response XML → convertir a tipo Python            │
└─────────────────────────────────────────────────────────────────┘
                              ↓ TCP/IP ↓
┌─────────────────────────────────────────────────────────────────┐
│                        SERVIDOR                                 │
├─────────────────────────────────────────────────────────────────┤
│  1. Escuchar en puerto TCP (socket.listen())                   │
│  2. Aceptar conexión entrante                                  │
│  3. Crear hilo dedicado para esta conexión                     │
│  4. Parsear HTTP request y cuerpo XML                          │
│  5. Ejecutar método solicitado con parámetros                  │
│  6. Construir response HTTP/XML                                │
│  7. Enviar respuesta al cliente y cerrar conexión             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Formato de Mensajes

```http
POST /RPC2 HTTP/1.1
Host: 127.0.0.1:8080
User-Agent: xmlrpc_redes/1.0
Content-Type: text/xml
Content-Length: 185
Connection: close

<?xml version="1.0"?>
<methodCall>
  <methodName>suma</methodName>
  <params>
    <param><value><int>5</int></value></param>
    <param><value><int>3</int></value></param>
  </params>
</methodCall>
```

### Respuesta Servidor → Cliente

```http
HTTP/1.1 200 OK
Content-Type: text/xml
Content-Length: 120

<?xml version="1.0"?>
<methodResponse>
  <params>
    <param><value><int>8</int></value></param>
  </params>
</methodResponse>
```

---

## Pruebas y Validación

### Suite de Pruebas

El archivo [test_app.py](src/examples/test_app.py) incluye:

**Pruebas básicas:**
- Operaciones aritméticas: `suma(7, 5)`, `resta(10, 3)`
- Manipulación de strings: `concat("Hola", " Mundo")`
- Potencias y formatos: `power(2, 8)`, `to_upper("ok", 3)`

**Pruebas de error:**
- Método inexistente → `FaultCode 2`
- Parámetros insuficientes/inválidos → `FaultCode 3`
- Errores internos (división por cero) → `FaultCode 4`

**Pruebas de concurrencia:**
- Múltiples clientes simultáneos
- Métodos con delays prolongados
- Stress testing

### Validación en Red Emulada (Mininet)

El proyecto fue validado en una topología de red con múltiples routers.

**Capturas de tráfico** (disponibles en [captures/](captures/)):
- Análisis con Wireshark confirma handshake TCP correcto
- Headers HTTP válidos en todas las comunicaciones
- Cuerpos XML-RPC correctamente formados
- Respuestas con `<methodResponse>` o `<fault>` apropiados

### Prueba Manual con curl

```bash
curl -X POST http://127.0.0.1:8080/RPC2 \
  -H "Content-Type: text/xml" \
  -H "Host: 127.0.0.1:8080" \
  --data '<?xml version="1.0"?>
<methodCall>
  <methodName>suma</methodName>
  <params>
    <param><value><int>10</int></value></param>
    <param><value><int>20</int></value></param>
  </params>
</methodCall>'
```

**Respuesta esperada:**
```xml
<?xml version="1.0"?>
<methodResponse>
  <params>
    <param><value><int>30</int></value></param>
  </params>
</methodResponse>
```

---

## Contexto Académico

**Obligatorio 1 - Redes de Computadoras 2025**  
**Facultad de Ingeniería - Instituto de Computación - Universidad de la República**

### Objetivos Cumplidos

- Implementación de protocolo de capa de aplicación (XML-RPC)
- Uso de sockets TCP para comunicación cliente-servidor
- Aplicación de HTTP/1.1 como protocolo de transporte
- Manejo de concurrencia mediante threading
- Validación exhaustiva con casos de prueba
- Análisis de tráfico de red con herramientas profesionales
- Documentación técnica completa

### Equipo

**Grupo 05:**
- Matías Rugnon
- Germán Capurro
- Tiago Calero

---

## Referencias

1. [XML-RPC Specification](http://xmlrpc.com/spec.md)
2. Tanenbaum, A. S. (2011). *Redes de Computadoras*. 5ta Edición
3. Kurose, J. F. & Ross, K. W. *Redes de Computadoras: Un Enfoque Descendente*
4. [Python Socket Programming HOWTO](https://docs.python.org/3/howto/sockets.html)
5. [HTTP/1.1 Specification (RFC 2616)](https://www.rfc-editor.org/rfc/rfc2616)

---

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

Desarrollado con fines académicos como parte del curso de Redes de Computadoras, Facultad de Ingeniería, UdelaR.
