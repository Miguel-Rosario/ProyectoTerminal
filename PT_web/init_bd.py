import mysql.connector
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# 🔹 Conexión al servidor MySQL (sin seleccionar BD aún)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Contraseña"
)
cursor = db.cursor()

# 🔹 Crear BD si no existe
cursor.execute("CREATE DATABASE IF NOT EXISTS sistema_firmas")
cursor.execute("USE sistema_firmas")

# =========================
# TABLA DE USUARIOS
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# =========================
# TABLA DE DOCUMENTOS
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS documentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_archivo VARCHAR(255) NOT NULL,
    contenido LONGTEXT NOT NULL,
    hash VARCHAR(255) NOT NULL,
    propietario_id INT NOT NULL,
    firmado BOOLEAN DEFAULT 1,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (propietario_id) REFERENCES usuarios(id)
)
""")

# =========================
# TABLA DE VERSIONES_DOCUMENTOS
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS versiones_documentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    documento_id INT NOT NULL,
    version INT NOT NULL,
    contenido LONGTEXT NOT NULL,
    hash VARCHAR(255) NOT NULL,
    usuario_id INT NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (documento_id) REFERENCES documentos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
)
""")

# =========================
# CREAR UN USUARIO DE PRUEBA CON CLAVES RSA
# =========================
privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)
publica = privada.public_key()

privada_pem = privada.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
).decode("utf-8")

publica_pem = publica.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode("utf-8")

# Insertar usuario de prueba si no existe
cursor.execute("SELECT COUNT(*) FROM usuarios")
if cursor.fetchone()[0] == 0:
    cursor.execute("""
        INSERT INTO usuarios (usuario, password, nombre, apellido)
        VALUES (%s, %s, %s, %s)
    """, ("usuario_prueba", publica_pem, "Usuario", "Prueba"))
    db.commit()
    print("✅ Usuario de prueba creado con claves RSA (clave pública guardada en 'password').")
else:
    print("ℹ️ Ya existe un usuario en la BD.")

db.close()

