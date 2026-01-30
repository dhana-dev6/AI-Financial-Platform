from cryptography.fernet import Fernet
import os

# Generate a key if not exists (In prod, store this in .env or KMS)
KEY_FILE = "secret.key"

def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
    else:
        with open(KEY_FILE, "rb") as key_file:
            key = key_file.read()
    return key

cipher_suite = Fernet(load_key())

def encrypt_value(value):
    """Encrypts a value (int, float, str) -> returns str (ciphertext)"""
    if value is None:
        return None
    val_str = str(value)
    encrypted_bytes = cipher_suite.encrypt(val_str.encode('utf-8'))
    return encrypted_bytes.decode('utf-8')

def decrypt_value(token, type_cast=str):
    """Decrypts token -> returns value cast to type_cast"""
    if not token:
        return None
    try:
        decrypted_bytes = cipher_suite.decrypt(token.encode('utf-8'))
        decrypted_str = decrypted_bytes.decode('utf-8')
        return type_cast(decrypted_str)
    except Exception as e:
        print(f"Decryption Error: {e}")
        return None
