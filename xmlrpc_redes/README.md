# xmlrpc_redes (Código Legacy)

⚠️ **Nota:** Este es el código original del proyecto. Para la versión organizada y lista para producción, ver el directorio [`src/`](../src/).

## Qué contiene este directorio

Esta es la implementación original desarrollada durante el obligatorio, mantenida para:
- Referencia histórica
- Comparación con la versión refactorizada
- Compatibilidad con scripts anteriores

## Usar la versión nueva

La versión organizada está en [`src/`](../src/) con:
- Estructura de paquete Python profesional
- Documentación mejorada
- Ejemplos actualizados
- READMEs detallados para cada módulo

## Contenido Legacy

- `xmlrpc_redes.py` - Core de marshalling/unmarshalling
- `server.py` - Servidor XML-RPC
- `client.py` - Cliente XML-RPC
- `test_app.py` - Suite de pruebas original
- `myServer.py`, `myClient.py`, `myServer2.py` - Ejemplos

## Migrando a la Nueva Estructura

**Antes:**
```python
from xmlrpc_redes import connect, Server
```

**Ahora:**
```python
import sys
sys.path.insert(0, '../src')

from client import connect
from server import Server
```

O mejor aún, usando el paquete:
```python
from src import connect, Server
```
