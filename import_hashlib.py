#   1.- Probar con un archivo xml 
#   2.- pasarlo a 
#   3.- sacar informacion de xml y hacer hash
#   4.- pasar xml a diccionario y despues hash 
#   5.- 

import hashlib

m = hashlib.sha256()    #m = hash 
m.update(b"Texto de ejemplo")
#m.update(b" the spammish repetition")
#m.digest()
print(m.name)
print(m.digest)
print(m.hexdigest())
print(m.block_size)
print(m.digest_size)
print(m.__class__)
# Crear un hash SHA-256
#data = "Texto de ejemplo".encode()
#hash_obj = hashlib.sha256(data)
#print(hash_obj.hexdigest())
