# Registro de Cambios

Todos los cambios notables en este proyecto serán documentados en este archivo.

## [1.0.0] - 2026-02-06

### ✨ Reorganización para Publicación en GitHub

Reestructuración completa del repositorio para hacerlo público y profesional.

#### Agregado
- **Estructura de directorios profesional**:
  - `src/` - Código fuente organizado como paquete Python
  - `docs/` - Documentación técnica (PDFs del grupo y obligatorio)
  - `captures/` - Capturas de tráfico de red (PCAP)
  - `src/examples/` - Ejemplos y suite de pruebas

- **Archivos de proyecto**:
  - `LICENSE` - Licencia MIT
  - `.gitignore` - Configuración profesional para Python
  - `PUBLICAR_GITHUB.md` - Guía para publicación
  - `CHANGELOG.md` - Este archivo

- **Documentación mejorada**:
  - README principal completo con decisiones de diseño
  - README en cada subdirectorio explicando contenido
  - Documentación detallada de arquitectura e implementación

- **Paquete Python**:
  - `src/__init__.py` - Inicialización del paquete
  - Estructura que permite `from src import connect, Server`

#### Reorganizado
- Código fuente movido de raíz a `src/`
- PDFs movidos a `docs/`
- Archivos PCAP movidos a `captures/`
- Ejemplos organizados en `src/examples/`

#### Modificado
- README principal completamente reescrito con:
  - Explicación clara del proyecto
  - Decisiones de diseño documentadas
  - Arquitectura e implementación detalladas
  - Instrucciones de uso mejoradas
  - Sección de validación y pruebas

- `xmlrpc_redes/README.md` actualizado para indicar código legacy

#### Eliminado
- `PROMPT_PORTFOLIO.md` - Archivo interno no apropiado para repo público
- Archivos duplicados en raíz

#### Mantenido
- Directorio `xmlrpc_redes/` como código original (legacy)
- Todos los archivos PCAP para validación
- PDFs de documentación académica

### 📦 Decisiones de Organización

**Rationale:**
1. **Separación clara**: Código, docs y capturas en directorios dedicados
2. **Paquete Python**: Estructura profesional que facilita importación
3. **Documentación exhaustiva**: README en cada nivel para claridad
4. **Legacy preservado**: Código original mantenido para referencia
5. **Licencia clara**: MIT para proyecto académico

### 🎓 Contexto Académico

**Proyecto:** Obligatorio 1 - Redes de Computadoras 2025  
**Institución:** Facultad de Ingeniería - UdelaR  
**Grupo:** 05 (Matías Rugnon, Germán Capurro, Tiago Calero)

### 🔧 Compatibilidad

- Python 3.8+
- Sin dependencias externas
- Compatible con implementación original
- Ejemplos migrados y funcionales

---

## [0.1.0] - 2025-09-12

### Versión Original (Pre-reorganización)

Implementación inicial del proyecto según especificación del obligatorio.

#### Incluido
- Implementación completa de XML-RPC sobre sockets
- Servidor con threading
- Cliente con sintaxis Pythonic
- Marshalling/unmarshalling automático
- 5 códigos de error implementados
- Suite de pruebas
- Validación en Mininet
- Capturas de tráfico
- Documentación técnica en PDF

---

## Formato

Este archivo sigue el formato de [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

### Tipos de Cambios

- **Agregado** - para nuevas funcionalidades
- **Modificado** - para cambios en funcionalidad existente
- **Obsoleto** - para funcionalidades que se eliminarán pronto
- **Eliminado** - para funcionalidades eliminadas
- **Corregido** - para corrección de bugs
- **Seguridad** - en caso de vulnerabilidades
