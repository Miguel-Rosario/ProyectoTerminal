# XML
import xml.etree.ElementTree as ET
import hashlib

try:
    # Abre el archivo XML
    with open('citas.xml', 'r', encoding='utf-8') as xml_file:
        # Leer el contenido completo del archivo
        xml_content = xml_file.read()
        print("Contenido del archivo XML:")
        print(xml_content)

        # Generar el hash del contenido
        hash_obj = hashlib.sha256(xml_content.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()
        print("\nHash generado (SHA-256):")
        print(hash_hex)

        # Procesar el contenido XML
        xml_data = ET.fromstring(xml_content)
        print("\nDatos del XML procesados correctamente.")

except FileNotFoundError:
    print("Error: El archivo 'citas.xml' no existe.")
except ET.ParseError as err:
    print(f"Error al procesar el archivo XML: {err}")
except Exception as err:
    print(f"Error inesperado: {err}")
