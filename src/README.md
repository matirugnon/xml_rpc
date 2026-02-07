# XML-RPC Library - Código Fuente

Este directorio contiene la implementación principal de la biblioteca XML-RPC sobre sockets TCP/IP.

## Estructura

```
src/
├── __init__.py           # Inicialización del paquete
├── xmlrpc_redes.py      # Core: marshalling/unmarshalling XML-RPC
├── server.py            # Servidor XML-RPC
├── client.py            # Cliente XML-RPC
└── examples/            # Ejemplos y pruebas
```

## Módulos Principales

### [xmlrpc_redes.py](xmlrpc_redes.py)
**Core de la biblioteca - Funciones de bajo nivel**

Proporciona las funciones fundamentales para:

**Serialización (Python → XML):**
- `serializacion(valor)` - Convierte tipos Python a elementos XML-RPC
- `construir_llamado_xml(method, params)` - Crea `<methodCall>` completo
- `construir_respuesta_xml(result)` - Crea `<methodResponse>` exitoso
- `construir_error_xml(code, message)` - Crea `<fault>` para errores

**Deserialización (XML → Python):**
- `deserializacion(elem)` - Convierte elementos XML a tipos Python
- `parsear_llamado_xml(xml_string)` - Extrae método y parámetros de `<methodCall>`
- `parsear_respuesta_xml(xml_string)` - Extrae resultado o fault de `<methodResponse>`

**Utilidades HTTP:**
- `construir_llamado_http(host, body)` - Crea request HTTP POST
- `parsear_llamado_http(data)` - Parsea request HTTP
- `construir_respuesta_http(body)` - Crea response HTTP
- `parsear_respuesta_http(data)` - Parsea response HTTP

**Tipos soportados:**
- Primitivos: `int`, `bool`, `float`, `str`
- Complejos: `list`, `tuple`, `dict`, `datetime`

### [server.py](server.py)
**Implementación del Servidor XML-RPC**

**Clase `Server`:**
```python
class Server:
    def __init__(self, address: Tuple[str, int])
    def add_method(self, func: Callable)
    def serve(self) -> None
```

**Características:**
- Escucha conexiones TCP en la dirección especificada
- Modelo thread-per-connection para concurrencia
- Registro dinámico de métodos mediante `add_method()`
- Validación de requests HTTP (POST, headers, Content-Type)
- Ejecución de métodos con manejo de excepciones
- Generación de faults con códigos apropiados (1-5)

**Códigos de error:**
- 1: Error de parseo XML
- 2: Método no existe
- 3: Error en parámetros
- 4: Error interno de ejecución
- 5: Otros errores de protocolo

### [client.py](client.py)
**Implementación del Cliente XML-RPC**

**Clase `Client`:**
```python
class Client:
    def __init__(self, address: str, port: int, timeout: float)
    def __getattr__(self, method_name: str) -> Callable
    def _invoke(self, method: str, params: List[Any]) -> Any
```

**Función de utilidad:**
```python
def connect(address: str, port: int, timeout: float = 20.0) -> Client
```

**Características:**
- Sintaxis Pythonic: `conn.method(args)` invoca métodos remotos
- Uso de `__getattr__` para métodos dinámicos
- Construcción automática de requests HTTP/XML-RPC
- Parseo automático de responses
- Conversión de faults a excepciones Python (`RuntimeError`)
- Control de timeouts configurables

### [__init__.py](__init__.py)
**Inicialización del Paquete**

Exporta las interfaces públicas principales:
```python
from .client import connect, Client
from .server import Server

__all__ = ['connect', 'Client', 'Server']
```

Permite importar directamente:
```python
from src import connect, Server
```

## Uso Básico

### Servidor Simple

```python
from server import Server

def suma(a, b):
    return int(a) + int(b)

servidor = Server(("127.0.0.1", 8000))
servidor.add_method(suma)
servidor.serve()
```

### Cliente Simple

```python
from client import connect

conn = connect("127.0.0.1", 8000)
resultado = conn.suma(5, 3)
print(resultado)  # 8
```

## Decisiones de Diseño

### 1. Separación de Responsabilidades
- `xmlrpc_redes.py`: Lógica de serialización independiente
- `server.py` / `client.py`: Lógica de red y protocolo

### 2. Modelo de Concurrencia
- Thread-per-connection en el servidor
- Ventaja: Simplicidad, aislamiento
- Limitación: No escala a miles de clientes

### 3. Protocolo HTTP
- POST en lugar de GET (semántica RPC)
- `Connection: close` (una request por conexión)
- Headers mínimos requeridos por XML-RPC spec

### 4. Manejo de Errores
- Clasificación con 5 faultCodes específicos
- Conversión de excepciones Python a faults XML
- Propagación de faults como RuntimeError en cliente

### 5. Tipos de Datos
- Soporte para tipos comunes de Python
- Conversión automática y recursiva
- Sin soporte para `base64` o `nil` (simplicidad)

## Dependencias

**Módulos estándar de Python únicamente:**
- `socket` - Comunicación TCP/IP
- `threading` - Concurrencia
- `xml.etree.ElementTree` - Parseo XML
- `datetime` - Tipo dateTime.iso8601
- `typing` - Type hints

**No hay dependencias externas.**

## Testing

Ver el directorio [examples/](examples/) para:
- Suite de pruebas completa (`test_app.py`)
- Ejemplos de servidor y cliente
- Casos de uso variados
