import xml.etree.ElementTree as ET

def editar_xml_generico(ruta_archivo):
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
