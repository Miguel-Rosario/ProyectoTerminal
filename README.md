# ProyectoTerminal
Criptografia 
Funciones Hash
# Primera Implementacion. Generación de Hashes

Este proyecto demuestra cómo procesar archivos XML, extraer información, convertirla a diferentes formatos y generar hashes SHA-256 de los datos.

## Funcionalidades

1. Probar con un archivo XML
2. Convertir el XML a otros formatos
3. Extraer información del XML y generar su hash SHA-256
4. Convertir el XML a un diccionario Python y luego generar su hash
5. Operaciones básicas con hashes SHA-256

## Requisitos

- Python 3.x
- Módulos requeridos:
  - `hashlib` (incluido en la biblioteca estándar de Python)

## Uso Básico

El código incluye ejemplos de cómo generar hashes SHA-256:

```python
import hashlib

# Crear un objeto hash SHA-256
m = hashlib.sha256()

# Actualizar el hash con datos (deben ser bytes)
m.update(b"Texto de ejemplo")

# Obtener diferentes representaciones del hash
print("Nombre del algoritmo:", m.name)
print("Digest (bytes):", m.digest())
print("Hexdigest:", m.hexdigest())
print("Tamaño de bloque:", m.block_size)
print("Tamaño del digest:", m.digest_size)
