# Capturas de Tráfico de Red

Este directorio contiene las capturas de tráfico generadas durante las pruebas del proyecto en una topología de red emulada con Mininet.

## Archivos de Captura

### [server1.pcap](server1.pcap)
Captura de tráfico en el servidor principal.
- Muestra todas las conexiones TCP entrantes
- Requests HTTP POST con payloads XML-RPC
- Responses HTTP con resultados o faults
- Permite validar handshake TCP y formato de mensajes

### [vhost1.pcap](vhost1.pcap) - [vhost5.pcap](vhost5.pcap)
Capturas de tráfico en cada router virtual de la topología.
- vhost1: Router principal conectado al cliente
- vhost2-5: Routers intermedios en la red
- Permiten analizar enrutamiento y propagación de paquetes

## Cómo Analizar las Capturas

### Con Wireshark

```bash
wireshark server1.pcap
```

**Filtros útiles:**
- `tcp.port == 8080` - Tráfico en puerto del servidor
- `http` - Solo requests/responses HTTP
- `xml` - Payloads XML-RPC
- `tcp.flags.syn == 1` - Handshake TCP (SYN)

### Con tcpdump

```bash
tcpdump -r server1.pcap -A | less
```

## Qué Buscar en las Capturas

1. **Handshake TCP correcto:**
   - SYN → SYN-ACK → ACK
   
2. **Headers HTTP válidos:**
   - `POST /RPC2 HTTP/1.1`
   - `Content-Type: text/xml`
   - `Content-Length: <bytes>`
   
3. **Cuerpos XML-RPC bien formados:**
   - `<methodCall>` en requests
   - `<methodResponse>` o `<fault>` en responses
   
4. **Manejo de errores:**
   - Responses con `<fault>` para métodos inválidos
   - Códigos de error apropiados (faultCode 1-5)

## Topología de Red Utilizada

```
              Cliente
                 │
        ┌────────┼────────┐
        │        │        │
    Router1  Router2  Router3
        │                │
   Servidor1        Servidor2
```

Las capturas validan que el protocolo XML-RPC funciona correctamente a través de múltiples saltos de red.
