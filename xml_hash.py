import hashlib
import xml.etree.ElementTree as ET

def calcular_hashes(ruta_archivo):
    """
    Calcula diferentes hashes (MD5, SHA-1, SHA-224, SHA-256, SHA-384, SHA-512) del archivo.
    """
    try:
        #abrimos el archivo en modo binario para leer su contenido
        with open(ruta_archivo, 'rb') as archivo:
            contenido = archivo.read() #leemos todos los datos del archivo
            
            #calculamos el hash
            hashes = {
                'md5': hashlib.md5(),
                'sha1': hashlib.sha1(),
                'sha224': hashlib.sha224(),
                'sha256': hashlib.sha256(),
                'sha384': hashlib.sha384(),
                'sha512': hashlib.sha512()
            }

            for hash_obj in hashes.values():
                hash_obj.update(contenido)

            return {nombre: obj.hexdigest() for nombre, obj in hashes.items()}#regresa todos los hashes
    except FileNotFoundError:
        print("Error: Archivo no encontrado.")
        return None

def verificar_checksum(ruta_archivo, checksum_original):
    #calculamos el checksum actual del archivo
    checksum_actual = calcular_hashes(ruta_archivo).get('md5')
    if checksum_actual is None:
        return False #false si el archivo no se encuentra
    return checksum_actual == checksum_original #se compara el actual con el original

def analizar_y_mostrar_xml(ruta_archivo):
    
    #Analiza y muestra el contenido de un archivo XML.
    
    try:
        #analizamos el archivo XML usando ElementTree
        arbol = ET.parse(ruta_archivo)
        raiz = arbol.getroot()  # Obtiene el elemento raíz del XML

        print("Contenido del XML analizado:")
        #iteramos sobre todos los elementos del XML y los imprime
        for elemento in raiz.iter():
            print(f"Etiqueta: {elemento.tag}, Atributos: {elemento.attrib}, Texto: {elemento.text.strip() if elemento.text else None}")
    except ET.ParseError:
        print("Error: No se pudo analizar el archivo XML.")
    except FileNotFoundError:
        print("Error: Archivo no encontrado.")

import xml.etree.ElementTree as ET

def modificar_xml(ruta_archivo):
    """
    Permite modificar un archivo XML de forma genérica.
    """
    try:
        # Cargar el archivo XML
        arbol = ET.parse(ruta_archivo)
        raiz = arbol.getroot()

        print("Opciones de edición:")
        print("1. Modificar un elemento existente.")
        print("2. Agregar un nuevo elemento.")
        print("3. Eliminar un elemento.")
        opcion = input("Seleccione una opción (1/2/3): ")

        if opcion == "1":
            # Modificar un elemento existente
            etiqueta = input("Ingrese el nombre del elemento a modificar: ")
            nuevo_texto = input("Ingrese el nuevo texto para el elemento: ")
            for elemento in raiz.iter(etiqueta):
                print(f"Modificando elemento: {elemento.tag}, Texto actual: {elemento.text}")
                elemento.text = nuevo_texto
                print(f"Texto actualizado: {nuevo_texto}")

        elif opcion == "2":
            # Agregar un nuevo elemento
            nombre_nuevo_elemento = input("Ingrese el nombre del nuevo elemento: ")
            texto_nuevo_elemento = input("Ingrese el texto del nuevo elemento: ")
            nuevo_elemento = ET.Element(nombre_nuevo_elemento)
            nuevo_elemento.text = texto_nuevo_elemento
            raiz.append(nuevo_elemento)
            print(f"Nuevo elemento '{nombre_nuevo_elemento}' agregado con texto '{texto_nuevo_elemento}'.")

        elif opcion == "3":
            # Eliminar un elemento existente
            etiqueta = input("Ingrese el nombre del elemento a eliminar: ")
            for elemento in raiz.findall(etiqueta):
                print(f"Eliminando elemento: {elemento.tag}")
                raiz.remove(elemento)

        else:
            print("Opción no válida.")

        # Guardar los cambios
        arbol.write(ruta_archivo, encoding='utf-8', xml_declaration=True)
        print("Cambios guardados en el archivo XML.")

    except FileNotFoundError:
        print("Error: Archivo no encontrado.")
    except ET.ParseError:
        print("Error: No se pudo analizar el archivo XML.")


if __name__ == "__main__":
    #solicitamos al usuario la ruta del archivo XML
    ruta_archivo_xml = input("Ingrese la ruta del archivo XML: ")

    hashes = calcular_hashes(ruta_archivo_xml)
    if hashes:
        print("Hashes calculados:")
        for nombre, valor in hashes.items():
            print(f"{nombre.upper()}: {valor}")

        #opcional: Solicita al usuario un checksum original para verificar
        checksum_original = input("Ingrese el checksum MD5 original para verificar (o deje en blanco para omitir): ")
        if checksum_original:
            es_valido = verificar_checksum(ruta_archivo_xml, checksum_original)
            if es_valido:
                print("La verificación del checksum pasó: El archivo está intacto.")
            else:
                print("La verificación del checksum falló: El archivo ha sido modificado.")

        #permitimos al usuario modificar el archivo XML
        modificar_xml(ruta_archivo_xml)

        #calculamos nuevamente el checksum para detectar cambios
        nuevo_hashes = calcular_hashes(ruta_archivo_xml)
        print("Nuevos hashes calculados:")
        for nombre, valor in nuevo_hashes.items():
            print(f"{nombre.upper()}: {valor}")

        #analizamos y mostramos el contenido del XML
        analizar_y_mostrar_xml(ruta_archivo_xml)
