from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import hashlib
import xml.etree.ElementTree as ET
import json
import os

# Archivos utilizados
FIRMA_ARCHIVO = "firma.bin"
CLAVE_PRIVADA = "clave_privada.pem"
CLAVE_PUBLICA = "clave_publica.pem"

# Funciones para manejo de claves RSA
def generar_claves():
    clave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    clave_publica = clave_privada.public_key()
    return clave_privada, clave_publica

def guardar_clave(clave, ruta, es_privada=False):
    with open(ruta, "wb") as archivo_clave:
        if es_privada:
            archivo_clave.write(
                clave.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )
        else:
            archivo_clave.write(
                clave.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            )

def cargar_clave(ruta, es_privada=False):
    with open(ruta, "rb") as archivo_clave:
        if es_privada:
            return serialization.load_pem_private_key(
                archivo_clave.read(),
                password=None,
                backend=default_backend()
            )
        else:
            return serialization.load_pem_public_key(
                archivo_clave.read(),
                backend=default_backend()
            )

# Funciones para firmar y verificar documentos
def firmar_documento(contenido, clave_privada):
    return clave_privada.sign(
        contenido,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

def verificar_firma(contenido, firma, clave_publica):
    try:
        clave_publica.verify(
            firma,
            contenido,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False

# Funciones para JSON y XML
def calcular_hash(contenido):
    return hashlib.sha256(contenido).hexdigest()

def modificar_json(ruta_json):
    try:
        with open(ruta_json, "r", encoding="utf-8") as archivo:
            data = json.load(archivo)
        
        clave = input("Ingrese la clave del elemento a modificar: ")
        if clave in data:
            nuevo_valor = input("Ingrese el nuevo valor: ")
            data[clave] = nuevo_valor
            
            with open(ruta_json, "w", encoding="utf-8") as archivo:
                json.dump(data, archivo, indent=4)
            print("JSON modificado exitosamente.")
            return True
        else:
            print("Clave no encontrada en el JSON.")
            return False
    except Exception as e:
        print(f"Error al modificar JSON: {e}")
        return False

def modificar_xml(ruta_xml):
    try:
        arbol = ET.parse(ruta_xml)
        raiz = arbol.getroot()
        
        etiqueta = input("Ingrese el nombre del elemento a modificar: ")
        nuevo_texto = input("Ingrese el nuevo texto: ")
        
        for elemento in raiz.iter(etiqueta):
            elemento.text = nuevo_texto
        
        arbol.write(ruta_xml, encoding='utf-8', xml_declaration=True)
        print("XML modificado exitosamente.")
        return True
    except Exception as e:
        print(f"Error al modificar XML: {e}")
        return False

# Programa principal
if __name__ == "__main__":
    if not os.path.exists(CLAVE_PRIVADA) or not os.path.exists(CLAVE_PUBLICA):
        clave_privada, clave_publica = generar_claves()
        guardar_clave(clave_privada, CLAVE_PRIVADA, es_privada=True)
        guardar_clave(clave_publica, CLAVE_PUBLICA, es_privada=False)
        print("Claves generadas y guardadas.")

    ruta_archivo = input("Ingrese la ruta del archivo (XML/JSON): ")
    tipo_archivo = "json" if ruta_archivo.lower().endswith(".json") else "xml"

    if os.path.exists(FIRMA_ARCHIVO):
        print("Verificando firma...")
        clave_publica = cargar_clave(CLAVE_PUBLICA, es_privada=False)
        with open(FIRMA_ARCHIVO, "rb") as f:
            firma_guardada = f.read()
        
        with open(ruta_archivo, "rb") as archivo:
            contenido = archivo.read()
        
        if verificar_firma(contenido, firma_guardada, clave_publica):
            print("✅ La firma es válida: el documento no ha sido alterado.")
            puede_modificarse = True
        else:
            print("❌ La firma NO es válida: el documento fue modificado o las claves cambiaron.")
            puede_modificarse = False
    else:
        print("⚠️ El archivo no está firmado. Se firmará después de modificarlo.")
        puede_modificarse = True

    
    if puede_modificarse:
        if tipo_archivo == "xml":
            if modificar_xml(ruta_archivo):
                with open(ruta_archivo, "rb") as archivo:
                    contenido = archivo.read()
                firma = firmar_documento(contenido, cargar_clave(CLAVE_PRIVADA, es_privada=True))
                with open(FIRMA_ARCHIVO, "wb") as f:
                    f.write(firma)
                print("✅ Documento XML firmado nuevamente.")
        else:
            if modificar_json(ruta_archivo):
                with open(ruta_archivo, "rb") as archivo:
                    contenido = archivo.read()
                firma = firmar_documento(contenido, cargar_clave(CLAVE_PRIVADA, es_privada=True))
                with open(FIRMA_ARCHIVO, "wb") as f:
                    f.write(firma)
                print("✅ Documento JSON firmado nuevamente.")
    else:
        print("❌ No se puede modificar ni firmar el documento debido a una firma inválida.")
