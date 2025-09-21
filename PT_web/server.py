from flask import Flask, request, jsonify, send_from_directory, Response
import mysql.connector

import json
import xml.etree.ElementTree as ET
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

import hashlib
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os



app = Flask(__name__, static_folder="client", static_url_path="")
CORS(app)


# Configuración BD
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="rorm990913",
    database="sistema_firmas"
)
cursor = db.cursor()



# =============== Generación de claves ===============
def generar_claves():
    clave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    clave_publica = clave_privada.public_key()
    return clave_privada, clave_publica

def serializar_claves(privada, publica):
    privada_pem = privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ).decode("utf-8")

    publica_pem = publica.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")

    return privada_pem, publica_pem


def calcular_hash(contenido):
    return hashlib.sha256(contenido.encode('utf-8')).hexdigest()

def verificar_firma_existente(contenido, firma, clave_publica_pem):
    try:
        if not firma:
            return False
            
        clave_publica = serialization.load_pem_public_key(clave_publica_pem.encode('utf-8'))
        clave_publica.verify(
            firma,
            contenido.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except:
        return False

# =============== Rutas API ===============
@app.route("/subir", methods=["POST"])
def subir_documento():
    archivo = request.files["archivo"]
    usuario_id = request.form["usuario_id"]

    contenido = archivo.read()
    nombre = archivo.filename
    tipo = "json" if nombre.endswith(".json") else "xml"

    # Generar hash
    hash_doc = hashlib.sha256(contenido).hexdigest()

    # Obtener claves del usuario
    cursor.execute("SELECT clave_privada FROM usuarios WHERE id=%s", (usuario_id,))
    res = cursor.fetchone()
    if not res:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    clave_privada_pem = res[0].encode("utf-8")
    clave_privada = serialization.load_pem_private_key(clave_privada_pem, password=None)

    # Firmar
    firma = clave_privada.sign(
        contenido,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # Guardar en BD
    cursor.execute("""
        INSERT INTO documentos (nombre, tipo, contenido, hash, firma, usuario_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (nombre, tipo, contenido.decode("utf-8"), hash_doc, firma, usuario_id))
    db.commit()
    doc_id = cursor.lastrowid
    crear_version(doc_id, contenido.decode("utf-8"), firma, usuario_id, tipo)


    return jsonify({"mensaje": "Documento subido y firmado correctamente"})


@app.route("/verificar/<int:id_doc>", methods=["GET"])
def verificar(id_doc):
    cursor.execute("SELECT contenido, firma, usuario_id FROM documentos WHERE id=%s", (id_doc,))
    doc = cursor.fetchone()
    if not doc:
        return jsonify({"error": "Documento no encontrado"}), 404

    contenido, firma, usuario_id = doc

    cursor.execute("SELECT clave_publica FROM usuarios WHERE id=%s", (usuario_id,))
    clave_publica_pem = cursor.fetchone()[0].encode("utf-8")
    clave_publica = serialization.load_pem_public_key(clave_publica_pem)

    try:
        
        clave_publica.verify(
            firma,
            contenido.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        # si valida
        cursor.execute("UPDATE documentos SET estado_firma=%s WHERE id=%s", ("valida", id_doc))
        db.commit()

        return jsonify({"valido": True, "mensaje": "La firma es válida"})
    except:
        cursor.execute("UPDATE documentos SET estado_firma=%s WHERE id=%s", ("invalida", id_doc))
        db.commit()
        return jsonify({"valido": False, "mensaje": "Firma inválida o documento alterado"})



@app.route("/registro", methods=["POST"])
def registro():
    data = request.json
    usuario = data.get("usuario")
    password = data.get("password")
    nombre = data.get("nombre")        # nombre de pila
    apellido = data.get("apellido") 

    if not usuario or not password  or not nombre or not apellido:
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    # Generar claves RSA
    clave_privada, clave_publica = generar_claves()
    privada_pem, publica_pem = serializar_claves(clave_privada, clave_publica)

    # Guardar en BD
    cursor.execute("""
        INSERT INTO usuarios (usuario, password, nombre, apellido, clave_publica, clave_privada)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (usuario, generate_password_hash(password), nombre, apellido, publica_pem, privada_pem))
    db.commit()

    return jsonify({"msg": "Usuario registrado correctamente"})
    

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    usuario = data.get("usuario")
    password = data.get("password")

    if not usuario or not password:
        return jsonify({"error": "Usuario y contraseña son obligatorios"}), 400

    try:
        cursor.execute(
            "SELECT id, password, apellido,  nombre FROM usuarios WHERE usuario=%s",
            (usuario,)
        )
        user = cursor.fetchone()

        if user and check_password_hash(user[1], password):
            return jsonify({
                "msg": "Login exitoso",
                "usuario_id": user[0],
                "nombre": user[3],
                "apellido": user[2]
            })
        else:
            return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

    except Exception as e:
        print("Error en /login:", e)
        return jsonify({"error": "Error interno en el servidor"}), 500


# =============== Ruta para listar documentos con sus últimas versiones ===============
@app.route("/documentos", methods=["GET"])
def obtener_documentos():
    try:
        # Traer solo la última versión de cada documento
        cursor.execute("""
            SELECT d.id, d.nombre, d.tipo, d.usuario_id, 
                v.id AS version_id, v.version_num, v.hash, v.fecha, v.usuario_id AS version_user
            FROM documentos d
            JOIN (
                SELECT documento_id, MAX(version_num) AS ultima_version
                FROM versiones_documentos
                GROUP BY documento_id
            ) lv ON d.id = lv.documento_id
            JOIN versiones_documentos v 
                ON v.documento_id = d.id AND v.version_num = lv.ultima_version
            ORDER BY d.id DESC

        """)
        
        filas = cursor.fetchall()
        result = []
        for row in filas:
            result.append({
                "id": row[0],              # id del documento
                "nombre": row[1],          # nombre del documento
                "tipo": row[2],
                "propietario_id": row[3],
                "version_id": row[4],      # id de la versión
                "version": row[5],
                "hash": row[6],
                "fecha": row[7],
                "usuario_version": row[8]
            })

        return jsonify(result)
    except Exception as e:
        print("Error en /documentos:", e)
        return jsonify([])


# =============== Ruta para listar SOLO los documentos originales del propietario ===============
@app.route("/mis_documentos/<int:usuario_id>", methods=["GET"])
def obtener_mis_documentos(usuario_id):
    try:
        cursor.execute("""
            SELECT id, nombre, tipo, usuario_id, hash, estado_firma, version, actualizado
            FROM documentos
            WHERE usuario_id = %s
            ORDER BY id DESC
        """, (usuario_id,))
        
        filas = cursor.fetchall()
        result = []
        for row in filas:
            result.append({
                "id": row[0],
                "nombre": row[1],
                "tipo": row[2],
                "usuario_id": row[3],
                "hash": row[4],
                "estado_firma": row[5],
                "version": row[6],
                "actualizado": row[7]
            })
        return jsonify(result)
    except Exception as e:
        print("Error en /mis_documentos:", e)
        return jsonify([])



# =============== Ruta para obtener un documento específico ===============
@app.route("/documentos/<int:id_doc>", methods=["GET"])
def obtener_documento(id_doc):
    usuario_id = request.args.get("usuario_id", None)  # opcional (si mandas el id del logueado)

    # obtener propietario
    cursor.execute("SELECT usuario_id FROM documentos WHERE id=%s", (id_doc,))
    row = cursor.fetchone()
    if not row:
        return jsonify({"error": "Documento no encontrado"}), 404
    propietario_id = row[0]

    # si es propietario, puede ver el original
    if usuario_id and str(usuario_id) == str(propietario_id):
        cursor.execute("""
            SELECT id, nombre, tipo, usuario_id, contenido, version
            FROM documentos WHERE id=%s
        """, (id_doc,))
        doc = cursor.fetchone()
        return jsonify({
            "id": doc[0],
            "nombre": doc[1],
            "tipo": doc[2],
            "usuario_id": doc[3],
            "contenido": doc[4],  # documento original
            "version": doc[5],
            "origen": "original"
        })

    # si NO es propietario → mostrar última versión
    cursor.execute("""
        SELECT id, documento_id, contenido, usuario_id, version_num, fecha, tipo
        FROM versiones_documentos
        WHERE documento_id=%s
        ORDER BY version_num DESC, fecha DESC
        LIMIT 1
    """, (id_doc,))
    ver = cursor.fetchone()
    if not ver:
        return jsonify({"error": "Sin versiones encontradas"}), 404

    return jsonify({
        "id": ver[0],
        "documento_id": ver[1],
        "contenido": ver[2],
        "usuario_id": ver[3],
        "version": ver[4],
        "fecha": ver[5],
        "tipo": ver[6],
        "origen": "version"
    })



import hashlib
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization

# ---------- Helpers ----------
def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def obtener_ultima_version_valida(documento_id):
    """
    Devuelve la fila de la última versión cuya firma esté 'valida' (la más reciente).
    Retorna None si no hay ninguna versión firmada válida.
    """
    cursor.execute("""
        SELECT id, documento_id, contenido, hash, firma, usuario_id, fecha, version_num, tipo
        FROM versiones_documentos
        WHERE documento_id=%s AND firma IS NOT NULL
        ORDER BY version_num DESC, fecha DESC
        LIMIT 1
    """, (documento_id,))
    return cursor.fetchone()

def obtener_ultima_version(documento_id):
    cursor.execute("""
        SELECT id, documento_id, contenido, hash, firma, usuario_id, fecha, version_num, tipo
        FROM versiones_documentos
        WHERE documento_id=%s
        ORDER BY version_num DESC, fecha DESC
        LIMIT 1
    """, (documento_id,))
    return cursor.fetchone()

def crear_version(documento_id, contenido_str, firma_bytes, usuario_id, tipo):
    contenido_bytes = contenido_str.encode('utf-8')
    hash_ = sha256_bytes(contenido_bytes)
    # calcular el siguiente version_num
    cursor.execute("SELECT COALESCE(MAX(version_num),0) FROM versiones_documentos WHERE documento_id=%s", (documento_id,))
    current_max = cursor.fetchone()[0] or 0
    next_version = current_max + 1
    cursor.execute("""
        INSERT INTO versiones_documentos (documento_id, contenido, hash, firma, usuario_id, version_num, tipo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (documento_id, contenido_str, hash_, firma_bytes, usuario_id, next_version, tipo))
    db.commit()
    return cursor.lastrowid, next_version


@app.route("/modificar/<int:id_doc>", methods=["POST"])
def modificar_documento(id_doc):
    try:
        data = request.get_json(silent=True) or request.form or {}
        nuevo_contenido = data.get("contenido") or data.get("nuevo_contenido")
        usuario_id_raw = data.get("usuario_id")

        if not nuevo_contenido:
            return jsonify({"error": "Contenido requerido"}), 400

        # obtener documento original + info del propietario y tipo
        cursor.execute("""
            SELECT d.contenido, d.firma, d.usuario_id, u.clave_publica, d.tipo
            FROM documentos d
            JOIN usuarios u ON d.usuario_id = u.id
            WHERE d.id = %s
        """, (id_doc,))
        doc = cursor.fetchone()
        if not doc:
            return jsonify({"error": "Documento no encontrado"}), 404

        contenido_original, firma_original, propietario_id, clave_publica_pem, tipo_documento = doc

        # Inicializar bandera
        es_valida_original = False
        if firma_original:
            es_valida_original = verificar_firma_existente(contenido_original, firma_original, clave_publica_pem)

        # normalizar usuario_id
        usuario_id = None
        if usuario_id_raw is not None and usuario_id_raw != "":
            try:
                usuario_id = int(usuario_id_raw)
            except:
                return jsonify({"error": "usuario_id inválido"}), 400

        es_propietario = (usuario_id is not None and propietario_id is not None and int(usuario_id) == int(propietario_id))

        # Si hay versiones posteriores, obtener info de la última versión
        cursor.execute("""
            SELECT id, usuario_id, version_num
            FROM versiones_documentos
            WHERE documento_id = %s
            ORDER BY version_num DESC, fecha DESC
            LIMIT 1
        """, (id_doc,))
        ultima = cursor.fetchone()
        ultima_version_usuario = None
        ultima_version_num = None
        if ultima:
            ultima_version_id, ultima_version_usuario, ultima_version_num = ultima  # ultima[1] es usuario_id

        # Condición extra: si existe una versión más reciente hecha por otro usuario,
        # no permitimos que el propietario reemplace el documento principal automáticamente.
        alterado_por_otros = False
        if ultima_version_usuario is not None and int(ultima_version_usuario) != int(propietario_id):
            alterado_por_otros = True

        # Si es propietario -> firmar nuevo contenido con su clave privada (se intentará firmar)
        firma_bytes = None
        if es_propietario:
            cursor.execute("SELECT clave_privada FROM usuarios WHERE id=%s", (usuario_id,))
            r = cursor.fetchone()
            if not r:
                return jsonify({"error": "Clave privada del usuario no encontrada"}), 500
            clave_privada_pem = r[0]
            if isinstance(clave_privada_pem, str):
                clave_privada_pem = clave_privada_pem.encode("utf-8")
            clave_privada = serialization.load_pem_private_key(clave_privada_pem, password=None)
            firma_bytes = clave_privada.sign(
                nuevo_contenido.encode("utf-8"),
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )

        # Crear nueva versión en versiones_documentos (siempre)
        contenido_bytes = nuevo_contenido.encode('utf-8')
        hash_ = hashlib.sha256(contenido_bytes).hexdigest()
        cursor.execute("SELECT COALESCE(MAX(version_num),0) FROM versiones_documentos WHERE documento_id=%s", (id_doc,))
        current_max = cursor.fetchone()[0] or 0
        next_version = current_max + 1

        cursor.execute("""
            INSERT INTO versiones_documentos (documento_id, contenido, hash, firma, usuario_id, version_num, tipo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (id_doc, nuevo_contenido, hash_, firma_bytes, usuario_id, next_version, tipo_documento))

        # DECISIÓN sobre actualizar la fila principal:
        # Solo actualizar documentos si:
        #  - quien edita es el propietario (es_propietario True)
        #  - y la firma original era válida (es_valida_original True)
        #  - y NO hay versiones posteriores creadas por otros (alterado_por_otros == False)
        if es_propietario and es_valida_original and not alterado_por_otros:
            estado = "valida" if firma_bytes else "sin_firma"
            cursor.execute("""
                UPDATE documentos
                SET contenido=%s, hash=%s, firma=%s, estado_firma=%s, version=%s, actualizado=NOW()
                WHERE id=%s
            """, (nuevo_contenido, hash_, firma_bytes, estado, next_version, id_doc))
            db.commit()
            return jsonify({
                "msg": "Documento modificado por propietario (documento principal actualizado)",
                "version": next_version,
                "firmado": bool(firma_bytes)
            })

        # En cualquier otro caso: no tocar tabla documentos, la nueva versión ya quedó en historial
        db.commit()

        if es_propietario and alterado_por_otros:
            return jsonify({
                "msg": "Nueva versión creada en historial. El documento principal no fue reemplazado porque hay versiones hechas por otros usuarios.",
                "version": next_version,
                "firmado": False
            })

        return jsonify({
            "msg": "Nueva versión creada",
            "version": next_version,
            "firmado": False
        })

    except Exception as e:
        print("Error en /modificar:", e)
        return jsonify({"error": str(e)}), 500



@app.route("/verificar_documento/<int:id_doc>", methods=["GET"])
def verificar_documento_completo(id_doc):
    try:
        cursor.execute("""
            SELECT d.contenido, d.firma, u.clave_publica 
            FROM documentos d 
            JOIN usuarios u ON d.usuario_id = u.id 
            WHERE d.id=%s
        """, (id_doc,))
        
        doc = cursor.fetchone()
        if not doc:
            return jsonify({"error": "Documento no encontrado"}), 404

        contenido, firma, clave_publica_pem = doc
        
        if not firma:
            return jsonify({"valido": False, "mensaje": "Documento no firmado"})

        es_valido = verificar_firma_existente(contenido, firma, clave_publica_pem)
        
        return jsonify({
            "valido": es_valido,
            "mensaje": "✓ Firma válida - documento intacto" if es_valido else "✗ Firma inválida - documento alterado"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- Endpoint: listar versiones ----------
@app.route("/versiones/<int:id_doc>", methods=["GET"])
def listar_versiones(id_doc):
    cursor.execute("""
        SELECT id, version_num, usuario_id, fecha, hash, firma IS NOT NULL AS tiene_firma
        FROM versiones_documentos
        WHERE documento_id=%s
        ORDER BY version_num DESC, fecha DESC
    """, (id_doc,))
    filas = cursor.fetchall()
    res = []
    for fid, vnum, uid, fecha, hsh, tiene in filas:
        res.append({
            "version_id": fid,
            "version_num": vnum,
            "usuario_id": uid,
            "fecha": str(fecha),
            "hash": hsh,
            "tiene_firma": bool(tiene)
        })
    return jsonify(res)

# ---------- Endpoint: restaurar versión ----------   REVISAR ESTOOOOO
@app.route("/restaurar_version/<int:version_id>", methods=["POST"])
def restaurar_version(version_id):
    """
    Restaurar una versión al documento principal.
    Body JSON: { "usuario_id": <id del propietario que solicita restaurar> }
    Solo el propietario original del documento puede restaurar.
    """
    try:
        data = request.json or {}
        requester_id = data.get("usuario_id")
        # obtener la version y su documento
        cursor.execute("SELECT documento_id, contenido, firma, version_num FROM versiones_documentos WHERE id=%s", (version_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error":"Versión no encontrada"}), 404
        documento_id, contenido_str, firma_bytes, version_num = row

        # verificar propietario del documento
        cursor.execute("SELECT usuario_id FROM documentos WHERE id=%s", (documento_id,))
        doc_row = cursor.fetchone()
        if not doc_row:
            return jsonify({"error":"Documento principal no encontrado"}), 404
        propietario_id = doc_row[0]
        if int(requester_id) != int(propietario_id):
            return jsonify({"error":"Solo el propietario puede restaurar"}), 403

        # restaurar: actualizar documento principal con contenido y firma de la version
        estado_firma = "valida" if firma_bytes else "sin_firma"
        es_publico = 0 if firma_bytes else 1
        #actualizar_documento_principal(documento_id, contenido_str, firma_bytes, estado_firma, es_publico, version_num)
        return jsonify({"msg":"Versión restaurada", "documento_id": documento_id, "version": version_num})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
   
@app.route("/info_version/<int:version_id>", methods=["GET"])
def obtener_info_version(version_id):
    try:
        cursor.execute("""
            SELECT id, documento_id, contenido, hash, firma, usuario_id, fecha, version_num, tipo
            FROM versiones_documentos WHERE id=%s
        """, (version_id,))
        
        version = cursor.fetchone()
        if not version:
            return jsonify({"error": "Versión no encontrada"}), 404
        
        return jsonify({
            "id": version[0],
            "documento_id": version[1],
            "contenido": version[2],
            "hash": version[3],
            "tiene_firma": version[4] is not None,
            "usuario_id": version[5],
            "fecha": version[6],
            "version_num": version[7],
            "tipo": version[8]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
from flask import Response
import urllib.parse

@app.route("/descargar_version/<int:version_id>", methods=["GET"])
def descargar_version(version_id):
    try:
        cursor.execute("""
            SELECT v.contenido, v.tipo, v.version_num, d.nombre
            FROM versiones_documentos v
            JOIN documentos d ON d.id = v.documento_id
            WHERE v.id = %s
        """, (version_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "Versión no encontrada"}), 404

        contenido, tipo, numero_version, nombre_doc = row

        # Normalizar extensión y mime-type
        if tipo == "json":
            extension = "json"
            content_type = "application/json"
        elif tipo == "xml":
            extension = "xml"
            content_type = "application/xml"
        else:
            extension = "txt"
            content_type = "text/plain; charset=utf-8"

        # nombre seguro (encodificado para cabecera)
        nombre_archivo = f"{nombre_doc}_v{numero_version}.{extension}"
        quoted = urllib.parse.quote(nombre_archivo)

        # contenido puede ser str (normalmente) -> convertir a bytes
        data = contenido if isinstance(contenido, (bytes, bytearray)) else contenido.encode("utf-8")

        headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{quoted}"
        }

        return Response(data, mimetype=content_type, headers=headers)

    except Exception as e:
        print("Error en /descargar_version:", e)
        return jsonify({"error": str(e)}), 500



@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


# =======================================
if __name__ == "__main__":
    app.run(debug=True)
