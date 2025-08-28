# xmlrpc_redes (implementación didáctica)

Proyecto de referencia para el obligatorio: una biblioteca XML-RPC **sobre sockets** usando **HTTP-POST** y **XML** con `xml.etree.ElementTree`.

## Estructura
- `xmlrpc_redes.py`: serialización/deserialización XML-RPC + helpers HTTP.
- `server.py`: servidor HTTP+XML-RPC minimalista con registro de métodos.
- `client.py`: cliente con `connect(address, port)` que permite `conn.metodo(...)` dinámicamente.
- `test_app.py`: lanza **dos servidores** y ejecuta un cliente con casos OK y de error.

## Requisitos
- Python 3.8+
- No usa librerías HTTP externas.

## Ejecutar demo
```bash
python test_app.py
```
Verás la salida de invocaciones exitosas y dos errores (método inexistente y parámetros inválidos).

## Notas de implementación
- Soporta tipos: `int`, `bool`, `float`, `str`, `list/tuple`, `dict`, `datetime` (ISO8601).  
- Una petición por conexión (Connection: close).  
- El servidor solo acepta `POST` a `/RPC2`.  
- Manejo de *faults* conforme al enunciado:  
  1. Error parseo de XML  
  2. No existe el método invocado  
  3. Error en parámetros del método invocado  
  4. Error interno en la ejecución del método  
  5. Otros errores

## Pruebas con curl
Con un servidor corriendo en `:8080`:
```bash
curl -v -X POST http://127.0.0.1:8080/RPC2 \
  -H "Content-Type: text/xml" \
  --data '<?xml version="1.0"?><methodCall><methodName>suma</methodName><params><param><value><int>3</int></value></param><param><value><int>4</int></value></param></params></methodCall>'
```
