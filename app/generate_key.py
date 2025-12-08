from cryptography.fernet import Fernet

# Generar clave
key = Fernet.generate_key()
print("Tu FERNET_KEY es:")
print(key.decode())
print("\nCopia esta clave (sin las comillas) y úsala en el PASO 2")