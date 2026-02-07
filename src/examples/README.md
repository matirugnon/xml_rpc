# Ejemplos y Pruebas XML-RPC

Este directorio contiene ejemplos de uso y una suite de pruebas completa para el proyecto XML-RPC.

## Archivos

### [test_app.py](test_app.py)
Suite de pruebas completa que valida toda la funcionalidad de la biblioteca.

**Qué hace:**
- Inicia dos servidores XML-RPC en los puertos 8080 y 8081
- Registra métodos de ejemplo (suma, resta, potencia, concatenación, etc.)
- Ejecuta casos de prueba de éxito y error
- Valida manejo de errores con todos los faultCodes
- Prueba concurrencia con múltiples clientes simultáneos

**Cómo ejecutar:**
```bash
cd src/examples
python test_app.py
```

**Salida esperada:**
- ✓ Pruebas exitosas muestran resultados correctos
- ✓ Pruebas de error muestran faultCode y mensaje apropiado
- ✓ Servidores se cierran al finalizar

### [myServer.py](myServer.py)
Servidor de ejemplo simple que demuestra cómo:
- Crear un servidor XML-RPC
- Registrar métodos personalizados
- Configurar dirección y puerto
- Mantener el servidor corriendo

**Cómo ejecutar:**
```bash
cd src/examples
python myServer.py
```

### [myClient.py](myClient.py)
Cliente de ejemplo que se conecta a myServer.py y:
- Establece conexión al servidor
- Invoca métodos remotos
- Maneja errores y timeouts
- Muestra resultados en consola

**Cómo ejecutar (con el servidor corriendo):**
```bash
cd src/examples
python myClient.py
```

### [myServer2.py](myServer2.py)
Segundo servidor para pruebas de múltiples servidores concurrentes.
Similar a myServer.py pero con:
- Puerto diferente
- Métodos adicionales
- Casos de prueba específicos

## Uso Típico

### 1. Ejecutar la Demo Completa
```bash
python test_app.py
```

### 2. Servidor y Cliente Separados

**Terminal 1 (Servidor):**
```bash
python myServer.py
```

**Terminal 2 (Cliente):**
```bash
python myClient.py
```

## Creando tu Propio Servidor

```python
import sys
sys.path.insert(0, '..')

from server import Server

def mi_funcion(param1, param2):
    # Tu lógica aquí
    return resultado

servidor = Server(("127.0.0.1", 8000))
servidor.add_method(mi_funcion)
servidor.serve()
```

## Creando tu Propio Cliente

```python
import sys
sys.path.insert(0, '..')

from client import connect

conn = connect("127.0.0.1", 8000)
resultado = conn.mi_funcion("arg1", "arg2")
print(resultado)
```

## Casos de Prueba Incluidos

**Operaciones básicas:**
- Suma, resta, multiplicación, potencia
- Concatenación de strings
- Transformaciones (mayúsculas, repetición)

**Manejo de errores:**
- Método inexistente (faultCode 2)
- Parámetros incorrectos (faultCode 3)
- Errores de ejecución (faultCode 4)

**Concurrencia:**
- Múltiples clientes simultáneos
- Métodos con delays largos
- Stress testing

## Notas

- Asegúrate de ajustar `sys.path.insert(0, '..')` según tu estructura de directorios
- Los servidores corren en localhost por defecto
- Puertos predeterminados: 8080 y 8081
- Para detener un servidor: Ctrl+C
