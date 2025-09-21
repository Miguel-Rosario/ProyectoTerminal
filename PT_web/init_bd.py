import mysql.connector
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Conexión al servidor MySQL (no a la BD aún)
print("entro ")
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="rorm990913"
)
print("SE conecto")
cursor = db.cursor()

# Crear BD
cursor.execute("CREATE DATABASE IF NOT EXISTS sistema_firmas")
cursor.execute("USE sistema_firmas")

# Crear tablas
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    clave_publica TEXT,
    clave_privada TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS documentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255),
    tipo ENUM('json','xml'),
    contenido LONGTEXT,
    hash VARCHAR(64),
    firma BLOB,
    usuario_id INT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
)
""")

# Generar claves RSA
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
        INSERT INTO usuarios (nombre, clave_publica, clave_privada)
        VALUES (%s, %s, %s)
    """, ("usuario_prueba", publica_pem, privada_pem))
    db.commit()
    print("✅ Usuario de prueba creado con claves RSA.")
else:
    print("ℹ️ Ya existe un usuario en la BD.")

db.close()
